from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.clean import cleanup
from mininet.log import setLogLevel
from mininet.cli import CLI
from p4_mininet import P4Switch, P4Host
from topology_utils import render_topo, render_topo_switches_only

# ================== 用户需修改的配置 ==================
# P4 程序编译产物路径（p4c 编译后的 .json）
P4_JSON = 'build/basic.json'

# BMv2 可执行文件：使用支持 P4Runtime 的 simple_switch_grpc
SW_PATH = 'simple_switch_grpc'

# 每个交换机的 gRPC 端口（P4Runtime 服务端监听）
# ONOS 将作为 gRPC 客户端连接到这些端口
GRPC_BASE = 50051

# 每个交换机的 Thrift 端口（仍用于 simple_switch_CLI 调试）
THRIFT_BASE = 9091

# 每个交换机的 pcap dump 目录
PCAP_DIR = '/tmp/pcap'
# =====================================================


class P4RuntimeTopo(Topo):
    """
    3 台 P4 交换机 (BMv2 simple_switch_grpc) + 9 台主机
    拓扑结构:
        h1,h2,h3 -- s1
        h4,h5,h6 -- s2
        h7,h8,h9 -- s3
        s1 -- s2 -- s3

    每台 P4 交换机启动一个 gRPC 服务端，等待 ONOS 通过 P4Runtime 接入。
    """

    def build(self):
        # ------- 主机：使用 P4Host，预置静态 ARP -------
        # 静态 ARP 能避免实验初期因 ARP 泛洪造成的干扰
        # 如果你希望观察 ARP 学习过程，可以改用默认 Host
        h1 = self.addHost('h1', cls=P4Host, mac='00:00:00:00:00:01', ip='10.0.0.1/24')
        h2 = self.addHost('h2', cls=P4Host, mac='00:00:00:00:00:02', ip='10.0.0.2/24')
        h3 = self.addHost('h3', cls=P4Host, mac='00:00:00:00:00:03', ip='10.0.0.3/24')
        h4 = self.addHost('h4', cls=P4Host, mac='00:00:00:00:00:04', ip='10.0.0.4/24')
        h5 = self.addHost('h5', cls=P4Host, mac='00:00:00:00:00:05', ip='10.0.0.5/24')
        h6 = self.addHost('h6', cls=P4Host, mac='00:00:00:00:00:06', ip='10.0.0.6/24')
        h7 = self.addHost('h7', cls=P4Host, mac='00:00:00:00:00:07', ip='10.0.0.7/24')
        h8 = self.addHost('h8', cls=P4Host, mac='00:00:00:00:00:08', ip='10.0.0.8/24')
        h9 = self.addHost('h9', cls=P4Host, mac='00:00:00:00:00:09', ip='10.0.0.9/24')

        # ------- P4 交换机 -------
        # 关键点:
        #   1. sw_path 使用 simple_switch_grpc
        #   2. grpc_port 每台唯一，ONOS 通过该端口接入
        #   3. thrift_port 保留用于本地调试
        #   4. device_id 是 P4Runtime 中设备的唯一标识，需与 ONOS 配置一致
        s1 = self.addSwitch(
            's1',
            cls=P4Switch,
            sw_path=SW_PATH,
            json_path=P4_JSON,
            thrift_port=THRIFT_BASE + 0,
            grpc_port=GRPC_BASE + 0,
            device_id=1,
            pcap_dump=PCAP_DIR,
            log_console=False,
            verbose=False,
        )
        s2 = self.addSwitch(
            's2',
            cls=P4Switch,
            sw_path=SW_PATH,
            json_path=P4_JSON,
            thrift_port=THRIFT_BASE + 1,
            grpc_port=GRPC_BASE + 1,
            device_id=2,
            pcap_dump=PCAP_DIR,
            log_console=False,
            verbose=False,
        )
        s3 = self.addSwitch(
            's3',
            cls=P4Switch,
            sw_path=SW_PATH,
            json_path=P4_JSON,
            thrift_port=THRIFT_BASE + 2,
            grpc_port=GRPC_BASE + 2,
            device_id=3,
            pcap_dump=PCAP_DIR,
            log_console=False,
            verbose=False,
        )

        # ------- 链路 -------
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s2)
        self.addLink(h5, s2)
        self.addLink(h6, s2)
        self.addLink(h7, s3)
        self.addLink(h8, s3)
        self.addLink(h9, s3)
        self.addLink(s1, s2)
        self.addLink(s2, s3)


if __name__ == '__main__':
    cleanup()
    setLogLevel('info')

    topo = P4RuntimeTopo()

    # 说明：
    #   在 P4Runtime 架构中，交换机是 gRPC 服务端（在 grpc_port 监听）
    #   控制器（ONOS）是 gRPC 客户端，主动连接交换机
    #   因此 Mininet 侧不传 RemoteController，也不需要 waitConnected
    net = Mininet(
        topo=topo,
        switch=P4Switch,
        controller=None,
        host=P4Host,
        build=False,
        waitConnected=False,
    )

    try:
        net.build()
        net.start()

        # 输出网络拓扑
        render_topo(net, "topo.svg")
        render_topo_switches_only(net, "topo_switches_only.svg")

        # 打印各交换机的 gRPC / Thrift 端口，便于配置 ONOS
        print("\n============ P4Runtime Switch Endpoints ============")
        print(f"{'Switch':<8}{'gRPC Port':<12}{'Thrift Port':<14}{'Device ID':<10}")
        print("-" * 44)
        for name in ['s1', 's2', 's3']:
            sw = net.get(name)
            grpc_port = GRPC_BASE + int(name[1:]) - 1
            thrift_port = THRIFT_BASE + int(name[1:]) - 1
            print(f"{name:<8}{grpc_port:<12}{thrift_port:<14}{sw.device_id:<10}")
        print("====================================================\n")

        print("[提示] 现在可以在 ONOS 侧执行以下步骤:")
        print("  1) 确认 ONOS 能访问 127.0.0.1 上的以下端口: "
              f"{GRPC_BASE}, {GRPC_BASE + 1}, {GRPC_BASE + 2}")
        print("  2) 在 ONOS 中激活 P4Runtime 相关应用:")
        print("       app activate org.onosproject.drivers.bmv2")
        print("       app activate org.onosproject.p4runtime")
        print("  3) 用 netcfg 或 REST 配置 P4 设备:")
        print("       devices: {")
        print("         of:0000000000000001: {")
        print("           p4rtPort: 50051, ")
        print("           managementAddress: 127.0.0.1,")
        print("           ...")
        print("         }, ...")
        print("       }")
        print("  4) 上传 pipeconf 应用后，ONOS 会自动连接各 P4 交换机\n")

        CLI(net)
    finally:
        net.stop()