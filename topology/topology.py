
#!/usr/bin/env python3

from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info


def create_topology():
    net = Mininet(
        controller=None,
        switch=OVSSwitch,
        build=False
    )

    info("*** Adding controller\n")
    net.addController(
        "c0",
        controller=RemoteController,
        ip="127.0.0.1",
        port=6653
    )

    info("*** Adding hosts\n")
    client = net.addHost("h1", ip="10.0.0.1/24")
    dns1 = net.addHost("h2", ip="10.0.0.2/24")
    dns2 = net.addHost("h3", ip="10.0.0.3/24")

    info("*** Adding switch\n")
    switch = net.addSwitch(
        "s1",
        protocols="OpenFlow13",
        failMode="secure"
    )

    info("*** Creating links\n")
    net.addLink(client, switch)
    net.addLink(dns1, switch)
    net.addLink(dns2, switch)

    info("*** Starting network\n")
    net.build()
    net.start()

    info("*** Network is ready\n")
    info("Client: h1 | DNS Server 1: h2 | DNS Server 2: h3\n")

    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    create_topology()

