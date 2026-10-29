from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import (
    CONFIG_DISPATCHER,
    MAIN_DISPATCHER,
    set_ev_cls,
)
from os_ken.ofproto import ofproto_v1_3
from os_ken.ofproto import ether
from os_ken.lib.packet import packet, ethernet, ipv4, udp


class SDNController(app_manager.OSKenApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SDNController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    def add_flow(self, datapath, priority, match, actions):
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        instructions = [
            parser.OFPInstructionActions(
                ofproto.OFPIT_APPLY_ACTIONS,
                actions
            )
        ]

        datapath.send_msg(
            parser.OFPFlowMod(
                datapath=datapath,
                priority=priority,
                match=match,
                instructions=instructions
            )
        )

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        # Default rule: send unmatched packets to the controller.
        table_miss_match = parser.OFPMatch()
        table_miss_actions = [
            parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER,
                ofproto.OFPCML_NO_BUFFER
            )
        ]

        self.add_flow(
            datapath,
            priority=0,
            match=table_miss_match,
            actions=table_miss_actions
        )

        # DNS-like requests: IPv4 UDP traffic destined for port 5353.
        dns_match = parser.OFPMatch(
            eth_type=0x0800,
            ip_proto=17,
            udp_dst=5353
        )

        dns_actions = [
            parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER,
                ofproto.OFPCML_NO_BUFFER
            )
        ]

        self.add_flow(
            datapath,
            priority=10,
            match=dns_match,
            actions=dns_actions
        )

        self.logger.info(
            "Installed DNS UDP/5353 controller rule on switch %s",
            datapath.id
        )
        self.logger.info("Switch connected: %s", datapath.id)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match["in_port"]

        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        udp_pkt = pkt.get_protocol(udp.udp)

        # Log DNS-like UDP requests.
        if (
            ip_pkt is not None
            and udp_pkt is not None
            and udp_pkt.dst_port == 5353
        ):
            self.logger.info(
                "DNS-like UDP request: %s -> %s, port %s",
                ip_pkt.src,
                ip_pkt.dst,
                udp_pkt.dst_port
            )

        if (
            eth_pkt is None
            or eth_pkt.ethertype == ether.ETH_TYPE_LLDP
        ):
            return

        dst = eth_pkt.dst
        src = eth_pkt.src
        dpid = datapath.id

        # Learn which switch port each source MAC address uses.
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        # Forward to a learned destination; otherwise flood.
        out_port = self.mac_to_port[dpid].get(
            dst,
            ofproto.OFPP_FLOOD
        )

        actions = [parser.OFPActionOutput(out_port)]

        # Install a forwarding rule when the destination is known.
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(
                in_port=in_port,
                eth_dst=dst
            )

            self.add_flow(
                datapath,
                priority=1,
                match=match,
                actions=actions
            )

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        # Forward the packet that triggered the packet-in event.
        datapath.send_msg(
            parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=msg.buffer_id,
                in_port=in_port,
                actions=actions,
                data=data
            )
        )