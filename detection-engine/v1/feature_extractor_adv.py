# detection-engine/feature_extractor_adv.py
"""
PHASE-2 ADVANCED FEATURE EXTRACTOR (FINAL + CLEAN)
Produces EXACT 26 Phase-2 features.
Safe for real-time streaming + logger + MERN backend.
"""

from scapy.all import IP, TCP, UDP, Raw
import time, math, statistics
from collections import defaultdict, deque

# -----------------------------------------------------
# GLOBAL CONSTANTS (fix for NameError)
# -----------------------------------------------------
EPS = 1e-6                    # prevent divide-by-zero
MAX_RECORD = 500              # max packets to remember per flow
MIN_PACKETS_TO_REPORT = 3     # suppress immature flows
MIN_DURATION = 0.001          # seconds minimum for rate features
PAYLOAD_MIN_BYTES = 16        # minimum payload for entropy
MAX_PAYLOAD_KEEP = 1024       # cap raw payload

# -----------------------------------------------------
# UTILITY FUNCTIONS
# -----------------------------------------------------
def entropy_bytes(b: bytes) -> float:
    """Shannon entropy of payload (0–8)."""
    if not b:
        return 0.0
    freq = {}
    for x in b:
        freq[x] = freq.get(x, 0) + 1
    total = len(b)
    e = 0.0
    for v in freq.values():
        p = v / total
        e -= p * math.log2(p)
    return e

def safe_int(x, default=0):
    try:
        return int(x)
    except:
        return default

def safe_float(x, default=0.0):
    try:
        return float(x)
    except:
        return default

# -----------------------------------------------------
# FLOW OBJECT
# -----------------------------------------------------
class Flow:
    """Holds per-flow packet stats + computes the 26 features."""
    def __init__(self, src, dst, sport, dport, proto):
        self.src = src
        self.dst = dst
        self.sport = sport
        self.dport = dport
        self.proto = proto

        self.start = time.time()
        self.last = self.start

        # lists
        self.lengths = deque(maxlen=MAX_RECORD)
        self.times = deque(maxlen=MAX_RECORD)

        self.fwd = deque(maxlen=MAX_RECORD)
        self.bwd = deque(maxlen=MAX_RECORD)

        # flags
        self.syn = 0
        self.fin = 0
        self.rst = 0
        self.psh = 0
        self.ack = 0

        # payload
        self.payload = bytearray()

        # ttl / window
        self.ttls = []
        self.windows = []

    # -------------------------------------------------
    def update(self, pkt, forward=True):
        now = time.time()
        self.last = now

        # packet length
        try:
            ln = len(bytes(pkt))
        except:
            ln = safe_int(getattr(pkt, "len", 0))

        self.lengths.append(ln)
        self.times.append(now)

        if forward:
            self.fwd.append(ln)
        else:
            self.bwd.append(ln)

        # TTL
        if IP in pkt:
            ttl = getattr(pkt[IP], "ttl", None)
            if ttl:
                self.ttls.append(safe_int(ttl))

        # Window + Flags
        if TCP in pkt:
            flags = str(pkt[TCP].flags)

            if "S" in flags: self.syn += 1
            if "F" in flags: self.fin += 1
            if "R" in flags: self.rst += 1
            if "P" in flags: self.psh += 1
            if "A" in flags: self.ack += 1

            win = getattr(pkt[TCP], "window", None)
            if win:
                self.windows.append(safe_int(win))

        # Payload
        if Raw in pkt:
            raw = bytes(pkt[Raw].load)
            if raw:
                self.payload.extend(raw[:MAX_PAYLOAD_KEEP])

    # -------------------------------------------------
    def get_26_features(self):
        """Return a dict of EXACT 26 Phase-2 features."""
        duration = max(EPS, self.last - self.start)

        # Packet stats
        pkt_cnt = len(self.lengths)
        total_len = sum(self.lengths)

        pkt_mean = safe_float(total_len / pkt_cnt) if pkt_cnt else 0.0
        pkt_std = safe_float(statistics.pstdev(self.lengths)) if pkt_cnt > 1 else 0.0

        fwd_min = min(self.fwd) if self.fwd else 0
        bwd_min = min(self.bwd) if self.bwd else 0

        # IAT
        times = list(self.times)
        if len(times) > 1:
            iats = [t2 - t1 for t1, t2 in zip(times, times[1:])]
            iat_mean = safe_float(sum(iats) / len(iats))
            iat_std = safe_float(statistics.pstdev(iats)) if len(iats) > 1 else 0.0
        else:
            iat_mean = 0.0
            iat_std = 0.0

        fwd_iat_mean = iat_mean
        bwd_iat_mean = iat_mean

        # Rates
        if pkt_cnt >= MIN_PACKETS_TO_REPORT and duration >= MIN_DURATION:
            bytes_per_sec = total_len / duration
            pkts_per_sec = pkt_cnt / duration
        else:
            bytes_per_sec = 0.0
            pkts_per_sec = 0.0

        # Entropy
        if len(self.payload) >= PAYLOAD_MIN_BYTES:
            payload_entropy = entropy_bytes(bytes(self.payload))
        else:
            payload_entropy = 0.0

        ttl_mean = safe_float(sum(self.ttls) / len(self.ttls)) if self.ttls else 0.0
        win_mean = safe_float(sum(self.windows) / len(self.windows)) if self.windows else 0.0

        return {
            # ----- Flow stats -----
            "flow_duration": duration,
            "total_fwd_packets": len(self.fwd),
            "total_bwd_packets": len(self.bwd),
            "total_length_fwd": float(sum(self.fwd)),
            "total_length_bwd": float(sum(self.bwd)),

            # ----- Packet length -----
            "pkt_len_mean": pkt_mean,
            "pkt_len_std": pkt_std,
            "fwd_pkt_len_min": fwd_min,
            "bwd_pkt_len_min": bwd_min,

            # ----- IAT -----
            "flow_iat_mean": iat_mean,
            "flow_iat_std": iat_std,
            "fwd_iat_mean": fwd_iat_mean,
            "bwd_iat_mean": bwd_iat_mean,

            # ----- Flags -----
            "fin_count": self.fin,
            "syn_count": self.syn,
            "rst_count": self.rst,
            "psh_count": self.psh,
            "ack_count": self.ack,

            # ----- Rates -----
            "bytes_per_sec": bytes_per_sec,
            "pkts_per_sec": pkts_per_sec,

            # ----- Others -----
            "payload_entropy": payload_entropy,
            "ttl": ttl_mean,
            "window_size": win_mean,

            # Protocol
            "is_tcp": 1 if self.proto == "TCP" else 0,
            "is_udp": 1 if self.proto == "UDP" else 0,

            # Filled by extractor
            "unique_dst_ports_in_flow": 0
        }

# -----------------------------------------------------
# EXTRACTOR (REPORT + UNIQUE PORTS)
# -----------------------------------------------------
class FeatureExtractorAdv:
    def __init__(self, report_once=True, report_every=0):
        self.flows = {}
        self.unique_ports = defaultdict(set)
        self.report_once = report_once
        self.report_every = report_every

    def _key(self, s, d, sp, dp, proto):
        return (s, d, sp, dp, proto)

    def process(self, pkt):
        if IP not in pkt:
            return None

        src, dst = pkt[IP].src, pkt[IP].dst

        if TCP in pkt:
            proto = "TCP"
            sp, dp = pkt[TCP].sport, pkt[TCP].dport
        elif UDP in pkt:
            proto = "UDP"
            sp, dp = pkt[UDP].sport, pkt[UDP].dport
        else:
            return None

        k = self._key(src, dst, sp, dp, proto)
        rk = self._key(dst, src, dp, sp, proto)

        if k not in self.flows and rk not in self.flows:
            self.flows[k] = Flow(src, dst, sp, dp, proto)

        flow = self.flows[k] if k in self.flows else self.flows[rk]
        forward = (k in self.flows)

        flow.update(pkt, forward)

        # Unique ports
        self.unique_ports[src].add(dp)

        feats = flow.get_26_features()
        feats["unique_dst_ports_in_flow"] = len(self.unique_ports[src])

        return feats
