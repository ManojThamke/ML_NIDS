# detection-engine/feature_extractor.py
"""
Advanced Feature Extractor for ML-NIDS (Phase-2)

Outputs per-flow feature dict with robust handling:
 - Destination Port
 - Flow Duration
 - Flow Packet Count
 - Total Bytes
 - Bytes Fwd
 - Bytes Bwd
 - Avg Packet Length
 - Packet Length Std
 - Fwd Packet Length Min/Max/Mean
 - Packet Rate (pkt/sec)
 - Fwd IAT Mean, Fwd IAT Std
 - Bwd IAT Mean, Bwd IAT Std
 - TCP SYN / RST / PSH counts
 - Is_TCP, Is_UDP (1/0)
 - Payload Entropy
 - Payload Distinct Bytes
 - Avg TTL
 - Avg Window Size
 - Unique Destination Ports seen (per source)
"""
from scapy.all import IP, TCP, UDP, Raw
import time
import statistics
from collections import deque, defaultdict
import math

MAX_PKT_RECORD = 500   # bound memory per flow
FLOW_TIMEOUT = 300     # seconds - optional cleanup threshold


def entropy_bytes(b: bytes) -> float:
    """Return Shannon entropy of bytes (0.0..8.0)."""
    if not b:
        return 0.0
    freq = {}
    for x in b:
        freq[x] = freq.get(x, 0) + 1
    ent = 0.0
    total = len(b)
    for v in freq.values():
        p = v / total
        ent -= p * math.log2(p)
    return float(ent)


def safe_int(v, default=0):
    try:
        return int(v)
    except Exception:
        try:
            return int(float(v))
        except Exception:
            return default


def safe_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


class FlowStats:
    def __init__(self, src, dst, sport, dport, proto):
        self.src = str(src)
        self.dst = str(dst)
        self.sport = safe_int(sport)
        self.dport = safe_int(dport)
        self.proto = str(proto)
        self.start_time = time.time()
        self.last_pkt_time = self.start_time

        # packet-level records
        self.pkts = deque(maxlen=MAX_PKT_RECORD)   # packet lengths
        self.times = deque(maxlen=MAX_PKT_RECORD)  # arrival times (for IAT)
        self.total_bytes = 0

        # direction-specific aggregates
        self.fwd_pkts = deque(maxlen=MAX_PKT_RECORD)
        self.bwd_pkts = deque(maxlen=MAX_PKT_RECORD)
        self.fwd_bytes = 0
        self.bwd_bytes = 0

        # flags counts
        self.tcp_syn = 0
        self.tcp_rst = 0
        self.tcp_psh = 0

        # payload statistics
        self.payload_bytes = bytearray()
        self.distinct_bytes = set()

        # other stats
        self.ttl_vals = []
        self.win_vals = []

    def update(self, pkt, direction_forward=True):
        now = time.time()
        self.last_pkt_time = now

        # pkt length robust
        try:
            pkt_len = len(bytes(pkt))
        except Exception:
            pkt_len = safe_int(getattr(pkt, "len", 0))
        self.pkts.append(pkt_len)
        self.times.append(now)
        self.total_bytes += pkt_len

        if direction_forward:
            self.fwd_pkts.append(pkt_len)
            self.fwd_bytes += pkt_len
        else:
            self.bwd_pkts.append(pkt_len)
            self.bwd_bytes += pkt_len

        # TTL and window if present
        try:
            ip = pkt[IP]
            ttl = getattr(ip, "ttl", None)
            if ttl is not None:
                self.ttl_vals.append(safe_int(ttl))
        except Exception:
            pass
        try:
            if TCP in pkt:
                win = getattr(pkt[TCP], "window", None)
                if win is not None:
                    self.win_vals.append(safe_int(win))
        except Exception:
            pass

        # TCP flags
        try:
            if TCP in pkt:
                flags = pkt[TCP].flags
                # scapy flags can be int or FlagValue
                if "S" in str(flags):
                    self.tcp_syn += 1
                if "R" in str(flags):
                    self.tcp_rst += 1
                if "P" in str(flags):
                    self.tcp_psh += 1
        except Exception:
            pass

        # payload bytes (Raw)
        try:
            if Raw in pkt:
                rawb = bytes(pkt[Raw].load)
                if rawb:
                    # keep up to a limit
                    add_len = min(len(rawb), 1024)
                    self.payload_bytes += rawb[:add_len]
                    for b in rawb[:add_len]:
                        self.distinct_bytes.add(b)
        except Exception:
            # best-effort; ignore failures
            pass

    def _safe_stats(self, seq):
        if not seq:
            return 0.0, 0.0, 0.0  # mean, std, count
        try:
            mean = float(sum(seq) / len(seq))
        except Exception:
            mean = 0.0
        try:
            std = float(statistics.pstdev(seq)) if len(seq) > 1 else 0.0
        except Exception:
            std = 0.0
        return mean, std, len(seq)

    def _packet_rate(self):
        dur = max(1e-6, time.time() - self.start_time)
        return float(len(self.pkts) / dur)

    def get_features(self):
        # Flow duration
        duration = max(0.0, time.time() - self.start_time)

        # packet counts and bytes
        pkt_count = len(self.pkts)
        total_bytes = float(self.total_bytes)
        fwd_count = len(self.fwd_pkts)
        bwd_count = len(self.bwd_pkts)

        # averages / stds
        avg_pkt_len = float(sum(self.pkts) / pkt_count) if pkt_count else 0.0
        try:
            pkt_len_std = float(statistics.pstdev(self.pkts)) if pkt_count > 1 else 0.0
        except Exception:
            pkt_len_std = 0.0

        fwd_min = int(min(self.fwd_pkts)) if self.fwd_pkts else 0
        fwd_max = int(max(self.fwd_pkts)) if self.fwd_pkts else 0
        fwd_mean = float(sum(self.fwd_pkts) / len(self.fwd_pkts)) if self.fwd_pkts else 0.0

        # IATs: compute differences on times
        fwd_iat_list = []
        bwd_iat_list = []
        # naive direction-based iat: iterate times and infer direction by comparing lengths in fwd/bwd deques — approximate
        try:
            # build a list of (time, length, dir) - we can't easily know dir for each time here without storing direction tags.
            # For robustness: compute successive diffs overall and use as both fwd/bwd fallback.
            times = list(self.times)
            if len(times) > 1:
                iats = [t2 - t1 for t1, t2 in zip(times, times[1:])]
            else:
                iats = []
            # use general iat stats as fallback
            if iats:
                general_iat_mean = float(sum(iats) / len(iats))
                general_iat_std = float(statistics.pstdev(iats)) if len(iats) > 1 else 0.0
            else:
                general_iat_mean = 0.0
                general_iat_std = 0.0
        except Exception:
            general_iat_mean = 0.0
            general_iat_std = 0.0

        # direction-specific IATs not always available without per-packet direction markers; approximate using same general IAT for both.
        fwd_iat_mean = general_iat_mean
        fwd_iat_std = general_iat_std
        bwd_iat_mean = general_iat_mean
        bwd_iat_std = general_iat_std

        ttl_mean = float(sum(self.ttl_vals) / len(self.ttl_vals)) if self.ttl_vals else 0.0
        win_mean = float(sum(self.win_vals) / len(self.win_vals)) if self.win_vals else 0.0

        payload_entropy = entropy_bytes(bytes(self.payload_bytes)) if self.payload_bytes else 0.0
        payload_distinct = len(self.distinct_bytes)

        packet_rate = self._packet_rate()

        # features dict (names must match training order)
        return {
            "Destination Port": int(self.dport),
            "Flow Duration": float(duration),
            "Flow Packet Count": int(pkt_count),
            "Total Bytes": float(total_bytes),
            "Bytes Fwd": float(self.fwd_bytes),
            "Bytes Bwd": float(self.bwd_bytes),
            "Avg Packet Length": float(avg_pkt_len),
            "Packet Length Std": float(pkt_len_std),
            "Fwd Packet Length Min": int(fwd_min),
            "Fwd Packet Length Max": int(fwd_max),
            "Fwd Packet Length Mean": float(fwd_mean),
            "Packet Rate": float(packet_rate),
            "Fwd IAT Mean": float(fwd_iat_mean),
            "Fwd IAT Std": float(fwd_iat_std),
            "Bwd IAT Mean": float(bwd_iat_mean),
            "Bwd IAT Std": float(bwd_iat_std),
            "TCP SYN Count": int(self.tcp_syn),
            "TCP RST Count": int(self.tcp_rst),
            "TCP PSH Count": int(self.tcp_psh),
            "Is_TCP": 1 if self.proto.upper().startswith("TCP") else 0,
            "Is_UDP": 1 if self.proto.upper().startswith("UDP") else 0,
            "Payload Entropy": float(payload_entropy),
            "Payload Distinct Bytes": int(payload_distinct),
            "Avg TTL": float(ttl_mean),
            "Avg Window Size": float(win_mean),
            # Unique destination ports cannot be computed per-flow alone; placeholder 0 (will set in extractor container)
            "Unique Dest Ports Seen": 0
        }


class FeatureExtractor:
    def __init__(self, enable_unique_dp_track=True):
        # flows keyed by 5-tuple
        self.flows = {}
        # per-src set of dest ports seen (for unique dest ports)
        self.src_to_dports = defaultdict(set)
        self.enable_unique_dp_track = enable_unique_dp_track

    def _make_key(self, src, dst, sport, dport, proto):
        return (str(src), str(dst), safe_int(sport), safe_int(dport), str(proto))

    def process_packet(self, pkt):
        # return features for the flow this packet belongs to (dict) or None
        if IP not in pkt:
            return None

        ip = pkt[IP]
        src = getattr(ip, "src", "")
        dst = getattr(ip, "dst", "")
        ttl = getattr(ip, "ttl", None)

        # transport
        if TCP in pkt:
            proto = "TCP"
            sport = getattr(pkt[TCP], "sport", 0)
            dport = getattr(pkt[TCP], "dport", 0)
            direction_forward = True  # define forward as src->dst for this flow
        elif UDP in pkt:
            proto = "UDP"
            sport = getattr(pkt[UDP], "sport", 0)
            dport = getattr(pkt[UDP], "dport", 0)
            direction_forward = True
        else:
            proto = str(getattr(ip, "proto", "OTHER"))
            sport = 0
            dport = 0
            direction_forward = True

        key = self._make_key(src, dst, sport, dport, proto)

        # if not present try reverse-key (packets in reverse direction)
        if key not in self.flows:
            rev_key = self._make_key(dst, src, dport, sport, proto)
            if rev_key in self.flows:
                # this packet belongs to reverse direction of existing flow
                flow = self.flows[rev_key]
                # mark direction accordingly: this packet is backward
                flow.update(pkt, direction_forward=False)
                features = flow.get_features()
                # update unique dest ports per source mapping
                if self.enable_unique_dp_track:
                    self.src_to_dports[flow.src].add(flow.dport)
                    features["Unique Dest Ports Seen"] = len(self.src_to_dports[flow.src])
                return features
            else:
                # create new flow for this direction
                flow = FlowStats(src, dst, sport, dport, proto)
                self.flows[key] = flow
        else:
            flow = self.flows[key]

        # update flow (forward)
        flow.update(pkt, direction_forward=True)

        # update unique dest ports per source
        if self.enable_unique_dp_track:
            self.src_to_dports[flow.src].add(flow.dport)

        features = flow.get_features()
        if self.enable_unique_dp_track:
            features["Unique Dest Ports Seen"] = len(self.src_to_dports[flow.src])

        return features

    def clear_older_than(self, seconds=FLOW_TIMEOUT):
        now = time.time()
        to_del = []
        for k, v in list(self.flows.items()):
            try:
                if (now - v.last_pkt_time) > seconds:
                    to_del.append(k)
            except Exception:
                to_del.append(k)
        for k in to_del:
            try:
                del self.flows[k]
            except Exception:
                pass

    def num_active_flows(self):
        return len(self.flows)
