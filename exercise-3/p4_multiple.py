# coding=utf-8
# p4_multiple.py
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.clean import cleanup
from mininet.log import setLogLevel
from mininet.cli import CLI
from stratum import StratumBmv2Switch
from p4_mininet import P4Host

P4_JSON = 'basic.json'


class LinearCascadeTopo(Topo):
    def build(self):
        # Linear cascade topology: s1 <--> s2 <--> s3
        s1 = self.addSwitch('s1', cls=StratumBmv2Switch, onosdevid='1', json=P4_JSON)
        s2 = self.addSwitch('s2', cls=StratumBmv2Switch, onosdevid='2', json=P4_JSON)
        s3 = self.addSwitch('s3', cls=StratumBmv2Switch, onosdevid='3', json=P4_JSON)

        # Inter-switch links
        self.addLink(s1, s2)
        self.addLink(s2, s3)

        # Hosts attached to s1
        h1 = self.addHost('h1', cls=P4Host, mac='00:00:00:01:00:01', ip='10.0.1.1/24')
        h2 = self.addHost('h2', cls=P4Host, mac='00:00:00:01:00:02', ip='10.0.1.2/24')
        h3 = self.addHost('h3', cls=P4Host, mac='00:00:00:01:00:03', ip='10.0.1.3/24')
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)

        # Hosts attached to s2
        h4 = self.addHost('h4', cls=P4Host, mac='00:00:00:01:00:04', ip='10.0.1.4/24')
        h5 = self.addHost('h5', cls=P4Host, mac='00:00:00:01:00:05', ip='10.0.1.5/24')
        h6 = self.addHost('h6', cls=P4Host, mac='00:00:00:01:00:06', ip='10.0.1.6/24')
        self.addLink(h4, s2)
        self.addLink(h5, s2)
        self.addLink(h6, s2)

        # Hosts attached to s3
        h7 = self.addHost('h7', cls=P4Host, mac='00:00:00:01:00:07', ip='10.0.1.7/24')
        h8 = self.addHost('h8', cls=P4Host, mac='00:00:00:01:00:08', ip='10.0.1.8/24')
        h9 = self.addHost('h9', cls=P4Host, mac='00:00:00:01:00:09', ip='10.0.1.9/24')
        self.addLink(h7, s3)
        self.addLink(h8, s3)
        self.addLink(h9, s3)


if __name__ == '__main__':
    cleanup()
    setLogLevel('info')
    topo = LinearCascadeTopo()
    net = Mininet(
        topo=topo,
        switch=StratumBmv2Switch,
        controller=None,
        host=P4Host,
        build=False,
        waitConnected=False
    )
    try:
        net.build()
        net.start()
        CLI(net)
    finally:
        net.stop()