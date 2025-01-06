from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.link import TCLink
from mininet.cli import CLI

class SimpleTopo(Topo):
    def build(self):
        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add links with bandwidth constraints
        self.addLink(h1, s1, bw=10)
        self.addLink(h2, s1, bw=10)
        self.addLink(s1, s2, bw=10)
        self.addLink(s2, h3, bw=10)
        self.addLink(s2, h4, bw=10)

def run():
    topo = SimpleTopo()
    net = Mininet(topo=topo, controller=lambda name: RemoteController(name, ip='127.0.0.1'), link=TCLink)
    net.start()

    print("Running CLI...")
    CLI(net)

    net.stop()

if __name__ == '__main__':
    run()
