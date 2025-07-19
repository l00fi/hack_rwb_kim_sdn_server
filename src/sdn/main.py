from topology import SimpleTopo

import os
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import Intf
from mininet.node import Controller

def run():
    topo = SimpleTopo()
    net = Mininet(topo=topo, controller=None)
    net.start()

    print("Server is working!")
    
    CLI(net)
    net.stop()

if __name__ == "__main__":
    setLogLevel("info")
    run()
