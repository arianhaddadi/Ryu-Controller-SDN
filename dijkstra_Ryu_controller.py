from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib import mac
from ryu.topology.api import get_switch, get_link
from ryu.app.wsgi import ControllerBase
from ryu.topology import event, switches
from collections import defaultdict

# switches
switches = []

# mymacs[srcmac]->(switch, port)
mymacs = {}

# adjacency map [sw1][sw2]->port from sw1 to sw2
adjacency = defaultdict(lambda:defaultdict(lambda:None))


# getting the node with lowest distance in Q
def minimum_distance(distance, Q):
    min = float('Inf')
    node = 0
    for v in Q:
        if distance[v] < min:
            min = distance[v]
            node = v
    return node

 

def get_path (src, dst, first_port, final_port):
    # executing Dijkstra's algorithm
    print( "get_path function is called, src=", src," dst=", dst, " first_port=", first_port, " final_port=", final_port)
    
    # defining dictionaries for saving each node's distance and its previous node in the path from first node to that node
    distance = {}
    previous = {}

    # setting initial distance of every node to infinity
    for dpid in switches:
        distance[dpid] = float('Inf')
        previous[dpid] = None

    # setting distance of the source to 0
    distance[src] = 0

    # creating a set of all nodes
    Q = set(switches)

    # checking for all undiscovered nodes whether there is a path that goes through them to their adjacent nodes which will make its adjacent nodes closer to src
    while len(Q) > 0:
        # getting the closest node to src among undiscovered nodes
        u = minimum_distance(distance, Q)
        # removing the node from Q
        Q.remove(u)
        # calculate minimum distance for all adjacent nodes to u
        for p in switches:
            # if u and other switches are adjacent
            if adjacency[u][p] != None:
                # setting the weight to 1 so that we count the number of routers in the path
                w = 1
                # if the path via u to p has lower cost then make the cost equal to this new path's cost
                if distance[u] + w < distance[p]:
                    distance[p] = distance[u] + w
                    previous[p] = u

    # creating a list of switches between src and dst which are in the shortest path obtained by Dijkstra's algorithm reversely
    r = []
    p = dst
    r.append(p)
    # set q to the last node before dst 
    q = previous[p]
    while q is not None:
        if q == src:
            r.append(q)
            break
        p = q
        r.append(p)
        q = previous[p]

    # reversing r as it was from dst to src
    r.reverse()

    # setting path 
    if src == dst:
        path=[src]
    else:
        path=r

    # Now adding in_port and out_port to the path
    r = []
    in_port = first_port
    for s1, s2 in zip(path[:-1], path[1:]):
        out_port = adjacency[s1][s2]
        r.append((s1, in_port, out_port))
        in_port = adjacency[s2][s1]
    r.append((dst, in_port, final_port))
    return r

 

class ProjectController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ProjectController, self).__init__(*args, **kwargs)
        self.topology_api_app = self
        self.datapath_list = []

    def install_path(self, p, ev, src_mac, dst_mac):
       print("install_path function is called!")
       #print( "p=", p, " src_mac=", src_mac, " dst_mac=", dst_mac)
       msg = ev.msg
       datapath = msg.datapath
       ofproto = datapath.ofproto
       parser = datapath.ofproto_parser
       # adding path to flow table of each switch inside the shortest path
       for sw, in_port, out_port in p:
            #print( src_mac,"->", dst_mac, "via ", sw, " in_port=", in_port, " out_port=", out_port)
            # setting match part of the flow table
            match = parser.OFPMatch(in_port=in_port, eth_src=src_mac, eth_dst=dst_mac)
            # setting actions part of the flow table
            actions = [parser.OFPActionOutput(out_port)]
            # getting the datapath
            datapath = self.datapath_list[int(sw)-1]
            # getting instructions based on the actions
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS , actions)]
            mod = datapath.ofproto_parser.OFPFlowMod(datapath=datapath, match=match, idle_timeout=0, hard_timeout=0,
                                                     priority=1, instructions=inst)
            # finalizing the change to switch datapath
            datapath.send_msg(mod)

 
    # defining event handler for setup and configuring of switches
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures , CONFIG_DISPATCHER)
    def switch_features_handler(self , ev):
        print("switch_features_handler function is called")
        # getting the datapath, ofproto and parser objects of the event
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # setting match condition to nothing so that it will match to anything
        match = parser.OFPMatch()
        # setting action to send packets to OpenFlow Controller without buffering
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS , actions)]
        # setting the priority to 0 so that it will be that last entry to match any packet inside any flow table
        mod = datapath.ofproto_parser.OFPFlowMod(
                            datapath=datapath, match=match, cookie=0,
                            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                            priority=0, instructions=inst)
        # finalizing the mod 
        datapath.send_msg(mod)

 
    # defining an event handler for packets coming to switches event
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # getting msg, datapath, ofproto and parser objects
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # getting the port switch received the packet with
        in_port = msg.match['in_port']
        # creating a packet encoder/decoder class with the raw data obtained by msg
        pkt = packet.Packet(msg.data)
        # getting the protocl that matches the received packet
        eth = pkt.get_protocol(ethernet.ethernet)

        # avoid broadcasts from LLDP 
        if eth.ethertype == 35020 or eth.ethertype == 34525:
            return

        # getting source and destination of the link
        dst = eth.dst
        src = eth.src
        dpid = datapath.id
        print("packet in. src=", src, " dst=", dst," dpid=", dpid)

        # add the host to the mymacs of the first switch that gets the packet
        if src not in mymacs.keys():
            mymacs[src] = (dpid, in_port)
            print("mymacs=", mymacs)

        # finding shortest path if destination exists in mymacs
        if dst in mymacs.keys():
            print("destination is known.")
            p = get_path(mymacs[src][0], mymacs[dst][0], mymacs[src][1], mymacs[dst][1])
            self.install_path(p, ev, src, dst)
            print("installed path=", p)
            out_port = p[0][2]
        else:
            print("destination is unknown.Flood has happened.")
            out_port = ofproto.OFPP_FLOOD

        # getting actions part of the flow table
        actions = [parser.OFPActionOutput(out_port)]

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
                                  actions=actions, data=data)
        datapath.send_msg(out)

    
    # defining an event handler for adding/deleting of switches, hosts, ports and links event
    events = [event.EventSwitchEnter,
              event.EventSwitchLeave, event.EventPortAdd,
              event.EventPortDelete, event.EventPortModify,
              event.EventLinkAdd, event.EventLinkDelete]
    @set_ev_cls(events)
    def get_topology_data(self, ev):
        global switches
        print("get_topology_data is called.")
        # getting the list of known switches 
        switch_list = get_switch(self.topology_api_app, None)  
        switches = [switch.dp.id for switch in switch_list]
        print("current known switches=", switches)
        # getting the list of datapaths from the list of switches
        self.datapath_list = [switch.dp for switch in switch_list]
        # sorting the datapath list based on their id so that indexing them in install_function will be correct
        self.datapath_list.sort(key=lambda dp: dp.id)

        # getting the list of links between switches
        links_list = get_link(self.topology_api_app, None)
        mylinks = [(link.src.dpid,link.dst.dpid,link.src.port_no,link.dst.port_no) for link in links_list]

        # setting adjacency of nodes
        for s1, s2, port1, port2 in mylinks:
            adjacency[s1][s2] = port1
            adjacency[s2][s1] = port2
