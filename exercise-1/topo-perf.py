from mininet.link import TCLink
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, OVSController
from mininet.clean import cleanup
from topology_utils import render_topo, render_topo_switches_only

if __name__ == '__main__':
    cleanup()
    topo = Topo()
    # 包含3个交换机，9台主机的拓扑结构
    h1 = topo.addHost('h1')
    h2 = topo.addHost('h2')
    h3 = topo.addHost('h3')
    h4 = topo.addHost('h4')
    h5 = topo.addHost('h5')
    h6 = topo.addHost('h6')
    h7 = topo.addHost('h7')
    h8 = topo.addHost('h8')
    h9 = topo.addHost('h9')
    
    s1 = topo.addSwitch('s1')
    s2 = topo.addSwitch('s2')
    s3 = topo.addSwitch('s3')
    topo.addLink(h1, s1)
    topo.addLink(h2, s1)
    topo.addLink(h3, s2)
    topo.addLink(h4, s2)
    topo.addLink(h5, s3)
    topo.addLink(h6, s3)
    topo.addLink(h7, s1)
    topo.addLink(h8, s2)
    topo.addLink(h9, s3)
    # 对交换机之间的链路性能进行限制
    topo.addLink(s1, s2) # 对照组： 不做任何限制，性能由宿主机的性能决定
    topo.addLink(s2, s3, bw=10, delay='5ms', jitter='10ms', loss=15)  # 限制s2和s3之间的链路带宽为10Mbps，延迟为5ms，丢包率为1%

    net = Mininet(topo=topo, link=TCLink, switch=OVSKernelSwitch, controller=OVSController)
    try:
        net.start()
        render_topo(net, "topo.svg")
        render_topo_switches_only(net, "topo_switches_only.svg")
        # 进入MiniNet CLI
        from mininet.cli import CLI
        CLI(net)
    finally:
        net.stop()
