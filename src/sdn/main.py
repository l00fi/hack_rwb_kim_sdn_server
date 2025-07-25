from topology import SimpleTopo

import os
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import Intf
from mininet.node import RemoteController
from mininet.clean import cleanup
cleanup()

def run():
    topo = SimpleTopo()
    net = Mininet(topo=topo, controller=None, build=False)
    c0 = net.addController(
            "c0",
            controller=RemoteController,
            ip="127.0.0.1",
            port=6613
    )
    net.build()
    c0.start()
    for sw in net.switches:
        sw.start([c0])    
    CLI(net)
    net.stop()

if __name__ == "__main__":
    setLogLevel("info")
    run()
