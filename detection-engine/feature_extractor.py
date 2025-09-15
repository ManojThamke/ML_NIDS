from scapy.all import IP, TCP, UDP
import time
import statistics
from collections import deque

# Max packets to keep per-flow (keep memory usage bounded)
MAX_PKT_RECORD = 200

class FlowStats:
    def __init__(self, dst_port):
        self.start_time = time.time()
        self.packet_lengths = deque(maxlen=MAX_PKT_RECORD)
        self.dst_port = int(dst_port) if dst_port is not None else 0

    def update(self, pkt_len):
        try:
            self.packet_lengths.append(int(pkt_len))
        except Exception:
            self.packet_lengths.append(0)

    def get_features(self):

        duration = time.time() - self.start_time
        if self.packet_lengths:
            fwd_pkt_min = min(self.packet_lengths)

            pkt_len_std = statistics.pstdev(self.packet_lengths) if len(self.packet_lengths) > 1 else 0.0
        else:
            fwd_pkt_min = 0
            pkt_len_std = 0.0

        return {
            "Destination Port": self.dst_port,
            "Flow Duration": float(duration),
            "Fwd Packet Length Min": int(fwd_pkt_min),
            "Packet Length Std": float(pkt_len_std),
        }
    
class FeatureExtractor:
    def __init__(self):
        self.flows = {}

    def _make_flow_key(self, src, dst, sport, dport, proto):
        return (str(src), str(dst), int(sport) if sport is not None else 0, int(dport) if dport is not None else 0, str(proto))

    def process_packet(self, pkt):
        if IP not in pkt:
            return None

        ip = pkt[IP] 
        src = getattr(ip, 'src', "")
        dst = getattr(ip, 'dst', "")

        # Determine transport/protocol and ports
        if TCP in pkt:
            proto = "TCP"
            sport = getattr(pkt[TCP], 'sport', 0)
            dport = getattr(pkt[TCP], 'dport', 0)
        elif UDP in pkt:
            proto = "UDP"
            sport = getattr(pkt[UDP], 'sport', 0)
            dport = getattr(pkt[UDP], 'dport', 0)
        else:
            proto = str(getattr(ip, "proto", "OTHER"))
            sport = 0
            dport = 0

        flow_key = self._make_flow_key(src, dst, sport, dport, proto)
        pkt_len = len(pkt)

        # initialize flow if not present
        if flow_key not in self.flows:

            self.flows[flow_key] = FlowStats(dport)

        # update stats
        self.flows[flow_key].update(pkt_len)

        # Return current features for this flow
        return self.flows[flow_key].get_features()

    def num_active_flows(self):
        return len(self.flows)

    def clear_older_than(self, seconds=300):

        now = time.time()
        to_delete = []
        for k, v in self.flows.items():
            if (now - v.start_time) > seconds:
                to_delete.appens(k)
        for k in to_delete:
            del self.flows[k]    