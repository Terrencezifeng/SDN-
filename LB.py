from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, icmp
from ryu.lib.packet import ether_types

class RoundRobinLB(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(RoundRobinLB, self).__init__(*args, **kwargs)
        self.servers = ['10.0.0.2', '10.0.0.3', '10.0.0.4']
        self.current_server = 0

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dst = eth.dst
        src = eth.src
        self.logger.info("packet in %s %s %s %s", datapath.id, src, dst, in_port)

        # 添加对 ICMP 和 ARP 数据包的处理
        if eth.ethertype in [ether_types.ETH_TYPE_ARP, ether_types.ETH_TYPE_IP]:
            if eth.ethertype == ether_types.ETH_TYPE_IP:
                ip_pkt = pkt.get_protocols(ipv4.ipv4)[0]
                if isinstance(pkt.get_protocols(icmp.icmp)[0], icmp.icmp):
                    # 为 ICMP 数据包选定后端主机
                    self.current_server = (self.current_server + 1) % len(self.servers)
                    selected_server = self.servers[self.current_server]
                    match = parser.OFPMatch(in_port=in_port)
                    actions = [parser.OFPActionSetField(ipv4_dst=selected_server),
                               parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
            else:
                # 处理 ARP 数据包
                self.logger.info("Processing ARP packet")
                match = parser.OFPMatch(in_port=in_port)
                actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]  # Flood ARP requests

            # 添加流表项
            self.add_flow(datapath, 1, match, actions, msg.buffer_id)

        # 处理到其他数据包的默认路径
        if msg.buffer_id != ofproto.OFP_NO_BUFFER:
            self.add_flow(datapath, 1, match, actions, msg.buffer_id)
        else:
            out = parser.OFPPacketOut(
                datapath=datapath, buffer_id=msg.buffer_id,
                in_port=in_port, actions=actions, data=msg.data)
            datapath.send_msg(out)
