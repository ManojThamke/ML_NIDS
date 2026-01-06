# detection-engine/realtime_v2/feature_extractor_v2.py

import time
import numpy as np
from collections import defaultdict

# ================================
# LOCKED REALTIME FEATURES
# ================================
REALTIME_FEATURES = [
    "Destination Port",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Fwd Packet Length Min",
    "Fwd Packet Length Mean",
    "Packet Length Std",
    "Flow IAT Mean",
    "Fwd IAT Mean",
    "Down/Up Ratio"
]


class FlowStats:
    """
    Holds statistics for a single network flow
    """

    def __init__(self, dst_port):
        self.dst_port = dst_port

        # Timing
        self.start_time = time.time()
        self.last_seen = self.start_time

        # Packet counts
        self.fwd_packets = 0
        self.bwd_packets = 0

        # Lengths
        self.fwd_lengths = []
        self.bwd_lengths = []

        # Inter-arrival times
        self.flow_iats = []
        self.fwd_iats = []

        self.last_fwd_time = None

    def update_forward(self, pkt_len):
        now = time.time()

        # Flow IAT
        self.flow_iats.append(now - self.last_seen)
        self.last_seen = now

        # Forward IAT
        if self.last_fwd_time is not None:
            self.fwd_iats.append(now - self.last_fwd_time)

        self.last_fwd_time = now

        self.fwd_packets += 1
        self.fwd_lengths.append(pkt_len)

    def update_backward(self, pkt_len):
        now = time.time()

        # Flow IAT
        self.flow_iats.append(now - self.last_seen)
        self.last_seen = now

        self.bwd_packets += 1
        self.bwd_lengths.append(pkt_len)

    def extract_features(self):
        """
        Returns a feature vector in EXACT training order
        """
        duration = max(time.time() - self.start_time, 1e-6)

        total_fwd_len = sum(self.fwd_lengths)
        total_bwd_len = sum(self.bwd_lengths)

        fwd_len_min = min(self.fwd_lengths) if self.fwd_lengths else 0
        fwd_len_mean = np.mean(self.fwd_lengths) if self.fwd_lengths else 0

        all_lengths = self.fwd_lengths + self.bwd_lengths
        pkt_len_std = np.std(all_lengths) if all_lengths else 0

        flow_iat_mean = np.mean(self.flow_iats) if self.flow_iats else 0
        fwd_iat_mean = np.mean(self.fwd_iats) if self.fwd_iats else 0

        down_up_ratio = (
            self.bwd_packets / self.fwd_packets
            if self.fwd_packets > 0 else 0
        )

        return [
            self.dst_port,
            duration,
            self.fwd_packets,
            self.bwd_packets,
            total_fwd_len,
            total_bwd_len,
            fwd_len_min,
            fwd_len_mean,
            pkt_len_std,
            flow_iat_mean,
            fwd_iat_mean,
            down_up_ratio
        ]
