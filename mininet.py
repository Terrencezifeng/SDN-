from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

def simple_topology():
    # 初始化Mininet网络，使用远程控制器和OVS交换机
    net = Mininet(controller=RemoteController, link=TCLink, switch=OVSSwitch)

    # 添加远程控制器，连接到Ryu控制器，默认IP为127.0.0.1，端口6633
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    # 创建主机，客户端h1和三个服务器h2, h3, h4
    client = net.addHost('h1', ip='10.0.0.1')
    server1 = net.addHost('h2', ip='10.0.0.2')
    server2 = net.addHost('h3', ip='10.0.0.3')
    server3 = net.addHost('h4', ip='10.0.0.4')

    # 创建一个OVS交换机
    s1 = net.addSwitch('s1')

    # 将每个主机与交换机相连
    net.addLink(client, s1)
    net.addLink(server1, s1)
    net.addLink(server2, s1)
    net.addLink(server3, s1)

    # 启动网络
    net.start()

    # 启动Mininet命令行界面，允许交互测试
    CLI(net)

    # 停止网络
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')  # 设置日志级别
    simple_topology()    # 运行拓扑构建函数
