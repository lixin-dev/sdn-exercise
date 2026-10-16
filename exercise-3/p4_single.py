# single_p4.py
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.clean import cleanup
from mininet.log import setLogLevel
from mininet.cli import CLI
from stratum import StratumBmv2Switch
from p4_mininet import P4Host

P4_JSON = 'basic.json'
DEVICE_ID = '1'

class SingleP4Topo(Topo):
    def build(self):
        h1 = self.addHost('h1', cls=P4Host,
                          mac='00:00:00:00:00:01', ip='10.0.0.1/24')
        h2 = self.addHost('h2', cls=P4Host,
                          mac='00:00:00:00:00:02', ip='10.0.0.2/24')

        s1 = self.addSwitch(
            's1',
            cls=StratumBmv2Switch,
            onosdevid=DEVICE_ID,
            # pcap_dump='/tmp/pcap',
            json='basic.json'
        )
        self.addLink(h1, s1)
        self.addLink(h2, s1)

if __name__ == '__main__':
    cleanup()
    setLogLevel('info')
    topo = SingleP4Topo()
    net = Mininet(topo=topo, switch=StratumBmv2Switch, controller=None,
                  host=P4Host, build=False, waitConnected=False)
    try:
        net.build()
        net.start()
        CLI(net)
    finally:
        net.stop()