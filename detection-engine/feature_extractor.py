# detection-engine/feature_extractor.py
"""
Lightweight feature extractor used by realtime_sniffer.py and realtime detectors.

Returns per-flow features (small set used for baseline/realtime):
 - Destination Port
 - Flow Duration (seconds)
 - Fwd Packet Length Min
 - Packet Length Std
"""
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
        # store integer port safely
        try:
            self.dst_port = int(dst_port) if dst_port not in (None, "") else 0
        except Exception:
            self.dst_port = 0

    def update(self, pkt_len):
        # robust conversion to int
        try:
            self.packet_lengths.append(int(pkt_len))
        except Exception:
            try:
                self.packet_lengths.append(int(float(pkt_len)))
            except Exception:
                self.packet_lengths.append(0)

    def get_features(self):
        duration = max(0.0, time.time() - self.start_time)
        if self.packet_lengths:
            try:
                fwd_pkt_min = int(min(self.packet_lengths))
            except Exception:
                fwd_pkt_min = 0
            if len(self.packet_lengths) > 1:
                try:
                    pkt_len_std = float(statistics.pstdev(self.packet_lengths))
                except Exception:
                    pkt_len_std = 0.0
            else:
                pkt_len_std = 0.0
        else:
            fwd_pkt_min = 0
            pkt_len_std = 0.0

        return {
            "Destination Port": int(self.dst_port),
            "Flow Duration": float(duration),
            "Fwd Packet Length Min": int(fwd_pkt_min),
            "Packet Length Std": float(pkt_len_std),
        }

class FeatureExtractor:
    def __init__(self):
        self.flows = {}

    def _make_flow_key(self, src, dst, sport, dport, proto):
        # normalize values to stable types
        try:
            sport_i = int(sport) if sport not in (None, "") else 0
        except Exception:
            sport_i = 0
        try:
            dport_i = int(dport) if dport not in (None, "") else 0
        except Exception:
            dport_i = 0
        return (str(src), str(dst), sport_i, dport_i, str(proto))

    def process_packet(self, pkt):
        # returns feature dict or None
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

        # packet length: use raw bytes length to be safe
        try:
            pkt_len = len(bytes(pkt))
        except Exception:
            try:
                pkt_len = int(getattr(pkt, "len", 0) or 0)
            except Exception:
                pkt_len = 0

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
        for k, v in list(self.flows.items()):
            try:
                if (now - v.start_time) > seconds:
                    to_delete.append(k)
            except Exception:
                # ignore malformed entries and mark for deletion to be safe
                to_delete.append(k)
        for k in to_delete:
            try:
                del self.flows[k]
            except Exception:
                pass
