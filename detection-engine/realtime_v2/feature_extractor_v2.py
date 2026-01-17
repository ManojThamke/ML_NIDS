# detection-engine/realtime_v2/feature_extractor_v2.py
# =====================================================
# Phase-2 Realtime Feature Extractor (CICIDS2018)
# Features are LOCKED to offline training schema
# =====================================================

import time
import numpy as np


# =====================================================
# LOCKED FEATURE ORDER (MUST MATCH OFFLINE TRAINING)
# =====================================================
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
    Maintains statistics for a single 5-tuple network flow
    and extracts CICIDS2018-compatible realtime features.
    """

    def __init__(self, dst_port: int):
        self.dst_port = dst_port

        # Timing
        self.start_time = time.time()
        self.last_seen = self.start_time
        self.last_fwd_time = None

        # Packet counts
        self.fwd_packets = 0
        self.bwd_packets = 0

        # Packet lengths
        self.fwd_lengths = []
        self.bwd_lengths = []

        # Inter-arrival times
        self.flow_iats = []
        self.fwd_iats = []

    # --------------------------------------------------
    # Forward packet update
    # --------------------------------------------------
    def update_forward(self, pkt_len: int):
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

    # --------------------------------------------------
    # Backward packet update
    # --------------------------------------------------
    def update_backward(self, pkt_len: int):
        now = time.time()

        # Flow IAT
        self.flow_iats.append(now - self.last_seen)
        self.last_seen = now

        self.bwd_packets += 1
        self.bwd_lengths.append(pkt_len)

    # --------------------------------------------------
    # Feature extraction (LOCKED ORDER)
    # --------------------------------------------------
    def extract_features(self):
        """
        Returns feature vector in EXACT order used during
        offline training and scaler fitting.
        """

        flow_duration = max(time.time() - self.start_time, 1e-6)

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

        # 🔒 FINAL FEATURE VECTOR (DO NOT CHANGE ORDER)
        return [
            self.dst_port,          # Destination Port
            flow_duration,          # Flow Duration
            self.fwd_packets,       # Total Fwd Packets
            self.bwd_packets,       # Total Backward Packets
            total_fwd_len,          # Total Length of Fwd Packets
            total_bwd_len,          # Total Length of Bwd Packets
            fwd_len_min,            # Fwd Packet Length Min
            fwd_len_mean,           # Fwd Packet Length Mean
            pkt_len_std,            # Packet Length Std
            flow_iat_mean,          # Flow IAT Mean
            fwd_iat_mean,           # Fwd IAT Mean
            down_up_ratio            # Down/Up Ratio
        ]
