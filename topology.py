import random
import threading
import os
import socket

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch, OVSSwitch, Host
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink, Link


class Network:

    def run(self):

        # defining net
        net = Mininet(controller=RemoteController, link=TCLink)

        # adding hosts
        h1 = net.addHost("h1", ip="10.0.0.1", mac="00:00:00:00:00:01")
        h2 = net.addHost("h2", ip="10.0.0.2", mac="00:00:00:00:00:02")
        h3 = net.addHost("h3", ip="10.0.0.3", mac="00:00:00:00:00:03")

        # adding servers
        s1 = net.addHost("s1", ip="10.0.0.4", mac="00:00:00:00:00:04")
        s2 = net.addHost("s2", ip="10.0.0.5", mac="00:00:00:00:00:05")
        s3 = net.addHost("s3", ip="10.0.0.6", mac="00:00:00:00:00:06")
        s4 = net.addHost("s4", ip="10.0.0.7", mac="00:00:00:00:00:07")
        s5 = net.addHost("s5", ip="10.0.0.8", mac="00:00:00:00:00:08")
        s6 = net.addHost("s6", ip="10.0.0.9", mac="00:00:00:00:00:09")
        s7 = net.addHost("s7", ip="10.0.0.10", mac="00:00:00:00:00:10")
        s8 = net.addHost("s8", ip="10.0.0.11", mac="00:00:00:00:00:11")
        s9 = net.addHost("s9", ip="10.0.0.12", mac="00:00:00:00:00:12")
        s10 = net.addHost("s10", ip="10.0.0.13", mac="00:00:00:00:00:13")
        s11 = net.addHost("s11", ip="10.0.0.14", mac="00:00:00:00:00:14")
        s12 = net.addHost("s12", ip="10.0.0.15", mac="00:00:00:00:00:15")


        # adding switches
        sw1 = net.addSwitch("sw1")
        sw2 = net.addSwitch("sw2")
        sw3 = net.addSwitch("sw3")
        sw4 = net.addSwitch("sw4")
        sw5 = net.addSwitch("sw5")
        sw6 = net.addSwitch("sw6")
        sw7 = net.addSwitch("sw7")
        sw8 = net.addSwitch("sw8")
        sw9 = net.addSwitch("sw9")
        sw10 = net.addSwitch("sw10")
        sw11 = net.addSwitch("sw11")
        sw12 = net.addSwitch("sw12")
        sw13 = net.addSwitch("sw13")
        sw14 = net.addSwitch("sw14")
        sw15 = net.addSwitch("sw15")
        sw16 = net.addSwitch("sw16")

        # adding controller
        net.addController("C0", controller=RemoteController, ip="127.0.0.1", port=6633)

        # defining link options
        linkopt5 = dict(bw=5, delay='1ms', cls=TCLink)
        linkopt10 = dict(bw=10, delay='1ms', cls=TCLink)
        linkopt15 = dict(bw=15, delay='1ms', cls=TCLink)
        linkopt50 = dict(bw=50, delay='1ms', cls=TCLink)
        linkopt100 = dict(bw=100, delay='1ms', cls=TCLink)

        # adding links
        # sw1
        net.addLink(sw1, s1, **linkopt100, port1=12000, port2=12001)
        net.addLink(sw1, s2, **linkopt100, port1=12002, port2=12003)
        net.addLink(sw1, sw3, **linkopt50, port1=12004, port2=12005)
        net.addLink(sw1, sw4, **linkopt100, port1=12006, port2=12007)
        # sw2
        net.addLink(sw2, s3, **linkopt100, port1=12008, port2=12009)
        net.addLink(sw2, s4, **linkopt100, port1=12010, port2=12011)
        # net.addLink(sw2, sw3, **linkopt100, port1=12012, port2=12013)
        net.addLink(sw2, sw4, **linkopt50, port1=12014, port2=12015)
        # sw3
        # net.addLink(sw3, sw13, **linkopt15, port1=12016, port2=12017)
        # net.addLink(sw3, sw14, **linkopt10, port1=12018, port2=12019)
        # sw4
        net.addLink(sw4, sw14, **linkopt5, port1=12020, port2=12021)
        # sw5
        net.addLink(sw5, s5, **linkopt100, port1=12022, port2=12023)
        net.addLink(sw5, s6, **linkopt100, port1=12024, port2=12025)
        net.addLink(sw5, sw7, **linkopt50, port1=12026, port2=12027)
        net.addLink(sw5, sw8, **linkopt100, port1=12028, port2=12029)
        # sw6
        net.addLink(sw6, s7, **linkopt100, port1=12030, port2=12031)
        net.addLink(sw6, s8, **linkopt100, port1=12032, port2=12033)
        # net.addLink(sw6, sw7, **linkopt100, port1=12034, port2=12035)
        net.addLink(sw6, sw8, **linkopt50, port1=12036, port2=12037)
        # sw7
        net.addLink(sw7, sw13, **linkopt15, port1=12038, port2=12039)
        # net.addLink(sw7, sw14, **linkopt20, port1=12040, port2=12041)
        # net.addLink(sw7, sw15, **linkopt5, port1=12042, port2=12043)
        # sw8
        net.addLink(sw8, sw15, **linkopt10, port1=12044, port2=12045)
        # net.addLink(sw8, sw16, **linkopt15, port1=12046, port2=12047)
        # sw9
        net.addLink(sw9, s9, **linkopt100, port1=12048, port2=12049)
        net.addLink(sw9, s10, **linkopt100, port1=12050, port2=12051)
        net.addLink(sw9, sw11, **linkopt50, port1=12052, port2=12053)
        net.addLink(sw9, sw12, **linkopt100, port1=12054, port2=12055)
        # sw10
        net.addLink(sw10, s11, **linkopt100, port1=12056, port2=12057)
        net.addLink(sw10, s12, **linkopt100, port1=12058, port2=12059)
        # net.addLink(sw10, sw11, **linkopt100, port1=12060, port2=12061)
        net.addLink(sw10, sw12, **linkopt50, port1=12062, port2=12063)
        # sw11
        net.addLink(sw11, sw14, **linkopt10, port1=12064, port2=12065)
        # sw12
        net.addLink(sw12, sw16, **linkopt10, port1=12066, port2=12067)
        # sw13
        net.addLink(sw13, h1, **linkopt100, port1=12068, port2=12069)
        # sw14
        net.addLink(sw14, h2, **linkopt100, port1=12070, port2=12071)
        # sw15
        net.addLink(sw15, sw12, **linkopt15, port1=12072, port2=12073)
        # sw16
        net.addLink(sw16, h3, **linkopt100, port1=12074, port2=12075)

        # running network
        net.start()
        
        # starting cli
        CLI(net)

        # stopping network
        net.stop()


if __name__ == "__main__":
    network = Network()
    network.run()