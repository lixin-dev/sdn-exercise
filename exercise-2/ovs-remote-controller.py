from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, OVSController, RemoteController, OVSSwitch
from mininet.clean import cleanup
from mininet.log import setLogLevel
from mininet.cli import CLI
from topology_utils import render_topo, render_topo_switches_only

if __name__ == '__main__':
    cleanup()
    setLogLevel( 'info' )

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
    s4 = topo.addSwitch('s4')

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
    topo.addLink(s3, s4)

    c0 = RemoteController( 'c0', ip='127.0.0.1', port=6653 )
    cmap = { 's1': c0, 's2': c0, 's3': c0, 's4': c0 }

    class ConnectToRemoteSwitch( OVSSwitch ):
        "Custom Switch() subclass that connects to different controllers"
        def start( self, controllers ):
            return OVSSwitch.start( self, [ cmap[ self.name ] ] )

    # OVS 内核交换机, OVSKernelSwitch默认，支持 OpenFlow、ovs-vsctl、VXLAN
    net = Mininet(topo=topo, 
        switch=ConnectToRemoteSwitch,
        controller=None,
        build=False,
        waitConnected=True)
    try:
        net.build()
        net.start()

        # 强制所有交换机使用OpenFlow13
        for sw_name in ['s1','s2','s3', 's4']:
            sw = net.get(sw_name)
            sw.cmd(f'ovs-vsctl set bridge {sw_name} protocols=OpenFlow13')
    
        # 删除默认兜底流表 actions=CONTROLLER，关键！
        # s1 = net.get('s1')
        # s2 = net.get('s2')
        # s3 = net.get('s3')
        # s1.cmd('ovs-ofctl del-flows s1')
        # s2.cmd('ovs-ofctl del-flows s2')
        # s3.cmd('ovs-ofctl del-flows s3')
        
        # 输出网络拓扑
        render_topo(net, "topo.svg")
        render_topo_switches_only(net, "topo_switches_only.svg")
        # 进入MiniNet CLI
        CLI(net)
    finally:
        net.stop()
