# detection-engine/feature_extractor_adv.py
"""
PHASE-2 ADVANCED FEATURE EXTRACTOR — UPDATED
- Exactly the 26 features required by Phase-2
- Suppresses per-packet spam by default (reports on maturity)
- Optional periodic reporting and flush-on-timeout
- Stable IAT, rate, entropy calculations
"""

from scapy.all import IP, TCP, UDP, Raw
import time, math, statistics
from collections import defaultdict, deque

MAX_RECORD = 500
EPS = 1e-6

# Phase-2 stability thresholds
MIN_PACKETS_TO_REPORT = 3       # don't report until flow has at least this many packets
MIN_DURATION = 0.001            # min duration (seconds) to compute rate features


# -------------------------
# Utility helpers
# -------------------------
def entropy_bytes(b: bytes) -> float:
    if not b:
        return 0.0
    freq = {}
    for x in b:
        freq[x] = freq.get(x, 0) + 1
    total = len(b)
    ent = 0.0
    for v in freq.values():
        p = v / total
        ent -= p * math.log2(p)
    return float(ent)


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


# -------------------------
# Flow object (per 5-tuple)
# -------------------------
class Flow:
    def __init__(self, src, dst, sport, dport, proto):
        self.src = src
        self.dst = dst
        self.sport = sport
        self.dport = dport
        self.proto = proto

        self.start = time.time()
        self.last = self.start

        # packet-level stores
        self.lengths = deque(maxlen=MAX_RECORD)
        self.times = deque(maxlen=MAX_RECORD)
        self.fwd = deque(maxlen=MAX_RECORD)
        self.bwd = deque(maxlen=MAX_RECORD)

        # flag counters
        self.syn = 0
        self.fin = 0
        self.rst = 0
        self.psh = 0
        self.ack = 0

        # payload, ttl, window
        self.payload = bytearray()
        self.ttls = []
        self.windows = []

        # reporting controls
        self.reported_once = False
        self.last_report_count = 0

    def update(self, pkt, forward=True):
        now = time.time()
        self.last = now

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

        # TCP flags + window
        if TCP in pkt:
            flags = str(pkt[TCP].flags)
            if "S" in flags: self.syn += 1
            if "F" in flags: self.fin += 1
            if "R" in flags: self.rst += 1
            if "P" in flags: self.psh += 1
            if "A" in flags: self.ack += 1
            win = getattr(pkt[TCP], "window", None)
            if win is not None:
                self.windows.append(safe_int(win))

        # TTL
        if IP in pkt:
            ttl = getattr(pkt[IP], "ttl", None)
            if ttl is not None:
                self.ttls.append(safe_int(ttl))

        # Payload bytes (cap to 1024 per packet to save memory)
        if Raw in pkt:
            try:
                raw = bytes(pkt[Raw].load)
                if raw:
                    self.payload.extend(raw[:1024])
            except Exception:
                pass

    def get_26_features(self):
        """Return a dict with the EXACT 26 Phase-2 features."""

        duration_raw = self.last - self.start
        duration = max(EPS, duration_raw)
        pkt_cnt = len(self.lengths)
        total_len = sum(self.lengths)

        # IATs (convert deque to list to allow slicing)
        times = list(self.times)
        if len(times) > 1:
            iats = [t2 - t1 for t1, t2 in zip(times, times[1:])]
            flow_iat_mean = safe_float(sum(iats) / len(iats))
            flow_iat_std = safe_float(statistics.pstdev(iats)) if len(iats) > 1 else 0.0
        else:
            flow_iat_mean = 0.0
            flow_iat_std = 0.0

        # direction-specific IATs (approximation)
        fwd_iat_mean = flow_iat_mean
        bwd_iat_mean = flow_iat_mean

        # length stats
        pkt_len_mean = safe_float(total_len / pkt_cnt) if pkt_cnt else 0.0
        pkt_len_std = safe_float(statistics.pstdev(self.lengths)) if pkt_cnt > 1 else 0.0

        fwd_pkt_len_min = min(self.fwd) if self.fwd else 0
        bwd_pkt_len_min = min(self.bwd) if self.bwd else 0

        # rates (only when flow is mature enough)
        if pkt_cnt >= MIN_PACKETS_TO_REPORT and duration_raw >= MIN_DURATION:
            bytes_per_sec = total_len / duration
            pkts_per_sec = pkt_cnt / duration
        else:
            bytes_per_sec = 0.0
            pkts_per_sec = 0.0

        # entropy + ttl/window
        payload_entropy = entropy_bytes(bytes(self.payload)) if self.payload else 0.0
        ttl_mean = safe_float(sum(self.ttls) / len(self.ttls)) if self.ttls else 0.0
        win_mean = safe_float(sum(self.windows) / len(self.windows)) if self.windows else 0.0

        return {
            # A: Flow-level
            "flow_duration": duration,
            "total_fwd_packets": len(self.fwd),
            "total_bwd_packets": len(self.bwd),
            "total_length_fwd": float(sum(self.fwd)),
            "total_length_bwd": float(sum(self.bwd)),

            # B: Packet length stats
            "pkt_len_mean": pkt_len_mean,
            "pkt_len_std": pkt_len_std,
            "fwd_pkt_len_min": fwd_pkt_len_min,
            "bwd_pkt_len_min": bwd_pkt_len_min,

            # C: IAT
            "flow_iat_mean": flow_iat_mean,
            "flow_iat_std": flow_iat_std,
            "fwd_iat_mean": fwd_iat_mean,
            "bwd_iat_mean": bwd_iat_mean,

            # D: TCP flag counters
            "fin_count": self.fin,
            "syn_count": self.syn,
            "rst_count": self.rst,
            "psh_count": self.psh,
            "ack_count": self.ack,

            # E: Rate features
            "bytes_per_sec": bytes_per_sec,
            "pkts_per_sec": pkts_per_sec,

            # F: Entropy & transport
            "payload_entropy": payload_entropy,
            "ttl": ttl_mean,
            "window_size": win_mean,

            # G: Protocol indicators
            "is_tcp": 1 if self.proto == "TCP" else 0,
            "is_udp": 1 if self.proto == "UDP" else 0,

            # H: Unique behavior (filled by outer extractor)
            "unique_dst_ports_in_flow": 0
        }


# -------------------------
# Extractor controller
# -------------------------
class FeatureExtractorAdv:
    def __init__(self, report_once=True, report_every=0, idle_timeout=60):
        """
        report_once: if True -> report only the first time a flow becomes 'mature' (>= MIN_PACKETS_TO_REPORT)
        report_every: if >0 -> also allow periodic reports every `report_every` packets after maturity
        idle_timeout: seconds of inactivity to consider a flow expired for flush
        """
        self.flows = {}
        self.unique_ports = defaultdict(set)
        self.report_once = bool(report_once)
        self.report_every = int(report_every)
        self.idle_timeout = int(idle_timeout)

    def _key(self, src, dst, sport, dport, proto):
        return (src, dst, sport, dport, proto)

    def process(self, pkt):
        """
        Process one packet. Returns feature dict only when reporting conditions are met,
        otherwise returns None to suppress noisy per-packet outputs.
        """
        if IP not in pkt:
            return None

        ip = pkt[IP]
        src, dst = ip.src, ip.dst

        if TCP in pkt:
            proto = "TCP"
            sport, dport = pkt[TCP].sport, pkt[TCP].dport
        elif UDP in pkt:
            proto = "UDP"
            sport, dport = pkt[UDP].sport, pkt[UDP].dport
        else:
            return None

        key = self._key(src, dst, sport, dport, proto)
        rev = self._key(dst, src, dport, sport, proto)

        # create flow if new
        if key not in self.flows and rev not in self.flows:
            self.flows[key] = Flow(src, dst, sport, dport, proto)

        flow = self.flows[key] if key in self.flows else self.flows[rev]

        forward = (key in self.flows)
        flow.update(pkt, forward)

        # update unique dest ports seen by source
        self.unique_ports[src].add(dport)

        pkt_cnt = len(flow.lengths)

        # Not mature yet => no report
        if pkt_cnt < MIN_PACKETS_TO_REPORT:
            return None

        # If report_once mode: report only the first time flow matures
        if self.report_once:
            if not flow.reported_once:
                flow.reported_once = True
                feats = flow.get_26_features()
                feats["unique_dst_ports_in_flow"] = len(self.unique_ports[src])
                flow.last_report_count = pkt_cnt
                return feats
            # already reported once -> fallthrough to periodic check

        # Periodic reporting if configured
        if self.report_every and (pkt_cnt - flow.last_report_count) >= self.report_every:
            feats = flow.get_26_features()
            feats["unique_dst_ports_in_flow"] = len(self.unique_ports[src])
            flow.last_report_count = pkt_cnt
            return feats

        # Default: suppress output
        return None

    def clear_older_than_flush(self, seconds=None):
        """
        Flush flows idle for `seconds` (default: self.idle_timeout) and return list of (key, features).
        Use to write remaining flows to disk before shutdown or periodically.
        """
        if seconds is None:
            seconds = self.idle_timeout
        now = time.time()
        flushed = []
        to_delete = []

        for key, flow in list(self.flows.items()):
            try:
                if (now - flow.last) > seconds:
                    feats = flow.get_26_features()
                    feats["unique_dst_ports_in_flow"] = len(self.unique_ports.get(flow.src, set()))
                    flushed.append((key, feats))
                    to_delete.append(key)
            except Exception:
                to_delete.append(key)

        for k in to_delete:
            try:
                del self.flows[k]
            except:
                pass

        return flushed

    def num_active_flows(self):
        return len(self.flows)
