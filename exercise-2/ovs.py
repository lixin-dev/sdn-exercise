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
    topo.addLink(s1, s2)
    topo.addLink(s2, s3)

    # OVS 内核交换机, OVSKernelSwitch默认，支持 OpenFlow、ovs-vsctl、VXLAN
    net = Mininet(topo=topo, switch=OVSKernelSwitch)
    try:
        net.start()

        # 删除默认兜底流表 actions=CONTROLLER，关键！
        s1 = net.get('s1')
        s2 = net.get('s2')
        s3 = net.get('s3')
        s1.cmd('ovs-ofctl del-flows s1')
        s2.cmd('ovs-ofctl del-flows s2')
        s3.cmd('ovs-ofctl del-flows s3')
        
        # 输出网络拓扑
        render_topo(net, "topo.svg")
        render_topo_switches_only(net, "topo_switches_only.svg")
        # 进入MiniNet CLI
        from mininet.cli import CLI
        CLI(net)
    finally:
        net.stop()
