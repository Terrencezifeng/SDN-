from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.log import setLogLevel, info

class CustomTopo(Topo):
    def build(self):
        # Add switches
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        switch3 = self.addSwitch('s3')

        # Add hosts
        host1 = self.addHost('h1', ip='10.0.0.1/24')
        host2 = self.addHost('h2', ip='10.0.0.2/24')
        host3 = self.addHost('h3', ip='10.0.0.3/24')
        host4 = self.addHost('h4', ip='10.0.0.4/24')

        # Add links
        self.addLink(host1, switch1)
        self.addLink(host2, switch1)
        self.addLink(switch1, switch2)
        self.addLink(switch2, switch3)
        self.addLink(switch3, host3)
        self.addLink(switch3, host4)

def run():
    # Create network with external RYU controller
    net = Mininet(topo=CustomTopo(),
                  controller=lambda name: RemoteController(name, ip='127.0.0.1'),
                  switch=OVSSwitch,
                  link=TCLink)

    # Start the network
    net.start()

    # Test network connectivity
    info("Testing network connectivity\n")
    net.pingAll()

    # Launch CLI
    info("Running CLI\n")
    net.interact()

    # Stop the network
    net.stop()

if __name__ == '__main__':
    # Set log level to info
    setLogLevel('info')

    # Run the Mininet script
    run()
