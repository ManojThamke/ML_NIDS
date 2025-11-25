#!/usr/bin/env python3
"""
realtime_sniffer.py — Real-time sniffer + feature extraction + optional live model prediction

Features:
 - Extracts per-flow features via feature_extractor.FeatureExtractor (same as before).
 - Logs feature rows to CSV when --log-features provided (same columns).
 - Optional: load a model bundle (joblib) and show live prediction label/prob with icon.
 - Small improvements: stable datetime, background cleanup, min-packets before logging.
 - Console shows either plain packet summary or packet summary + model label/prob.

 python detection-engine/realtime_sniffer.py --model-path detection-engine/models/lightbgm_advanced.pkl --iface "Wi-Fi" --filter "tcp or udp" --threshold 0.4 --log-features logs/realtime_features.csv --verbose  

Save as: detection-engine/realtime_sniffer.py
"""
from scapy.all import sniff, IP, TCP, UDP, ICMP
import datetime
import argparse
import os
import sys
import threading
import time
import json
import math
import joblib
import pandas as pd

# allow running from project root or detection engine dir:
HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# local import (feature_extractor.py)
try:
    from feature_extractor import FeatureExtractor
except Exception as e:
    raise SystemExit("feature_extractor.py required — put it in detection-engine/ and try again.")

def pretty_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------- packet summary ----------
def pkt_summary(pkt):
    ts = pretty_time()
    proto = ""
    sport = ""
    dport = ""
    src = ""
    dst = ""

    if IP in pkt:
        ip = pkt[IP]
        src = ip.src or ""
        dst = ip.dst or ""
        if TCP in pkt:
            proto = "TCP"
            sport = getattr(pkt[TCP], 'sport', "") or ""
            dport = getattr(pkt[TCP], 'dport', "") or ""
        elif UDP in pkt:
            proto = "UDP"
            sport = getattr(pkt[UDP], 'sport', "") or ""
            dport = getattr(pkt[UDP], 'dport', "") or ""
        elif ICMP in pkt:
            proto = "ICMP"
        else:
            proto = str(getattr(ip, 'proto', "")) or ""
    else:
        proto = getattr(pkt, "name", "NON-IP")
        src = getattr(pkt, 'src', "") or ""
        dst = getattr(pkt, 'dst', "") or ""

    proto_s = str(proto)
    sport_s = str(sport)
    dport_s = str(dport)
    src_s = str(src)
    dst_s = str(dst)
    proto_field = proto_s.ljust(5)[:5]
    line = f"[{ts}] {proto_field} {src_s}:{sport_s} -> {dst_s}:{dport_s}"
    return line

# ---------- feature extractor ----------
extractor = FeatureExtractor()

# track flow counts for min-packets thresholding
flows_seen = {}

def make_flow_key(pkt):
    if IP not in pkt:
        return None
    ip = pkt[IP]
    proto = "TCP" if TCP in pkt else ("UDP" if UDP in pkt else str(getattr(ip, 'proto', 'OTHER')))
    sport = ""
    dport = ""
    if TCP in pkt:
        sport = getattr(pkt[TCP], "sport", "") or ""
        dport = getattr(pkt[TCP], "dport", "") or ""
    elif UDP in pkt:
        sport = getattr(pkt[UDP], "sport", "") or ""
        dport = getattr(pkt[UDP], "dport", "") or ""
    return (str(ip.src), str(sport), str(ip.dst), str(dport), str(proto))

def ensure_csv_header(path, header_line):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(header_line + "\n")

def safe_get(features, key, default=None):
    if not features:
        return default
    return features.get(key, default)

def background_cleanup(interval_seconds):
    if interval_seconds <= 0:
        return
    while True:
        try:
            time.sleep(interval_seconds)
            try:
                extractor.clear_older_than(seconds=interval_seconds * 2 if interval_seconds > 1 else 300)
            except Exception:
                pass
        except Exception:
            continue

# ---------- model support (optional) ----------
class SimpleModelWrapper:
    """
    Lightweight wrapper expecting joblib bundle with keys:
      {"model": <estimator|pipeline>, "scaler": optional, "feature_cols": [...]}
    Wrapper will attempt to preserve column names for models that expect them.
    """
    def __init__(self, path, verbose=False):
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        self.verbose = verbose
        try:
            bundle = joblib.load(path)
        except Exception as e:
            raise RuntimeError(f"Failed to load model bundle: {e}")
        self.model = bundle.get("model") or bundle.get("estimator") or bundle.get("clf") or bundle.get("pipeline")
        self.scaler = bundle.get("scaler")
        self.feature_cols = bundle.get("feature_cols") or bundle.get("feature_columns") or bundle.get("feature_columns_list")
        if self.feature_cols is not None:
            self.feature_cols = [str(c) for c in self.feature_cols]
        if self.model is None:
            raise ValueError("Loaded bundle has no 'model' object.")
        if self.verbose:
            print(f"ℹ️  Model loaded: {os.path.basename(path)} features: {len(self.feature_cols) if self.feature_cols else 'unknown'}")

    def _safe_float(self, v):
        try:
            return float(v)
        except Exception:
            return 0.0

    def prepare(self, features: dict):
        if self.feature_cols:
            row = []
            for c in self.feature_cols:
                # case-insensitive lookup fallback
                if c in features:
                    v = features[c]
                else:
                    v = None
                    for k in features:
                        if str(k).strip().lower() == str(c).strip().lower():
                            v = features[k]; break
                row.append(self._safe_float(v) if v is not None else 0.0)
            df = pd.DataFrame([row], columns=self.feature_cols)
        else:
            df = pd.DataFrame([{k: self._safe_float(v) for k, v in features.items()}])
        return df

    def predict_with_proba(self, features: dict):
        X = self.prepare(features)
        try:
            if self.scaler is not None:
                arr = self.scaler.transform(X)
                try:
                    X_proc = pd.DataFrame(arr, columns=X.columns)
                except Exception:
                    X_proc = arr
            else:
                X_proc = X
        except Exception:
            X_proc = X
        pred = int(self.model.predict(X_proc)[0])
        prob = None
        try:
            if hasattr(self.model, "predict_proba"):
                prob = float(self.model.predict_proba(X_proc)[0][1])
            elif hasattr(self.model, "decision_function"):
                val = float(self.model.decision_function(X_proc)[0])
                prob = 1.0 / (1.0 + math.exp(-val))
        except Exception:
            prob = None
        return pred, prob

# ---------- file write helper ----------
def append_features_csv(path, ts, dest_port, flow_duration, fwd_min, pkt_std):
    ensure_csv_header(path, "timestamp,Destination Port,Flow Duration,Fwd Packet Length Min,Packet Length Std")
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(f"{ts},{dest_port},{flow_duration:.6f},{fwd_min},{pkt_std:.6f}\n")
    except Exception as e:
        print(f"[{pretty_time()}] ERROR writing features CSV: {e}")

# ---------- main per-packet handler ----------
def on_packet(pkt, show_features=False, log_features=None, min_packets=2,
              debug=False, model_wrapper=None, threshold=0.5):
    try:
        # print base summary
        base_line = pkt_summary(pkt)
        label_line = ""  # will be set if we have model
        features = None
        try:
            features = extractor.process_packet(pkt)
        except Exception as e:
            if debug:
                print(f"[{pretty_time()}] WARN feature extraction: {e}")
            features = None

        # If model present, predict and show icon + label
        if model_wrapper and features:
            try:
                pred, prob = model_wrapper.predict_with_proba(features)
                prob_s = f"{prob:.6f}" if prob is not None else "N/A"
                if prob is not None and prob >= threshold:
                    icon = "🔴"
                    label = "ATTACK"
                else:
                    icon = "🟢"
                    label = "BENIGN"
                label_line = f"  {icon} {label} (p={prob_s})"
            except Exception as e:
                label_line = f" ⚠️ pred-error:{e}"

        # print combined
        print(base_line + label_line)

        # optionally print feature contents
        if features and show_features:
            try:
                feat_str = ", ".join(f"{k}={v}" for k, v in features.items())
                print("   →", feat_str)
            except Exception:
                pass

        # logging features to CSV (only for TCP/UDP to reduce noise)
        if log_features:
            if not (TCP in pkt or UDP in pkt):
                return

            key = make_flow_key(pkt)
            if key:
                flows_seen[key] = flows_seen.get(key, 0) + 1
                seen = flows_seen[key]
            else:
                seen = 0

            if seen < (min_packets or 1):
                return

            # prefer feature values but fallback to packet fields
            dest_port = safe_get(features, "Destination Port", "")
            if dest_port in (None, ""):
                if TCP in pkt:
                    dest_port = getattr(pkt[TCP], "dport", "") or ""
                elif UDP in pkt:
                    dest_port = getattr(pkt[UDP], "dport", "") or ""
                else:
                    dest_port = ""

            try:
                flow_duration = float(safe_get(features, "Flow Duration", 0.0) or 0.0)
            except Exception:
                flow_duration = 0.0
            try:
                fwd_min = int(safe_get(features, "Fwd Packet Length Min", 0) or 0)
            except Exception:
                fwd_min = 0
            try:
                pkt_std = float(safe_get(features, "Packet Length Std", 0.0) or 0.0)
            except Exception:
                pkt_std = 0.0

            ts = pretty_time()
            if debug:
                print(f"[DEBUG] write: {ts},{dest_port},{flow_duration:.6f},{fwd_min},{pkt_std:.6f}")
            append_features_csv(log_features, ts, dest_port, flow_duration, fwd_min, pkt_std)

    except Exception as e:
        print(f"[{pretty_time()}] ERROR processing packet: {e}")

# ---------- CLI & main ----------
def main(interface=None, count=0, bpf_filter=None, show_features=True, log_features=None,
         min_packets=2, debug=False, cleanup_interval=60, model_path=None, threshold=0.5, verbose=False):
    print("📡 Starting sniffer...")
    print(f"   Interface: {interface or 'default'}  Filter: {bpf_filter or 'none'}  Min-packets: {min_packets}")
    if log_features:
        print(f"📝 Logging feature rows to: {os.path.abspath(log_features)}")
    if model_path:
        print(f"🔌 Loading model for live prediction: {os.path.abspath(model_path)}")
    # start background cleanup
    if cleanup_interval and cleanup_interval > 0:
        t = threading.Thread(target=background_cleanup, args=(cleanup_interval,), daemon=True)
        t.start()

    model_wrapper = None
    if model_path:
        try:
            model_wrapper = SimpleModelWrapper(model_path, verbose=verbose)
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            model_wrapper = None

    try:
        sniff(iface=interface,
              prn=lambda pkt: on_packet(pkt,
                                       show_features=show_features,
                                       log_features=log_features,
                                       min_packets=min_packets,
                                       debug=debug,
                                       model_wrapper=model_wrapper,
                                       threshold=threshold),
              store=False,
              count=count,
              filter=bpf_filter)
    except KeyboardInterrupt:
        print("\n⛔ Stopped by user (KeyboardInterrupt).")
    except Exception as e:
        print(f"[{pretty_time()}] ERROR in sniffing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Realtime sniffer with feature extraction and optional live model prediction")
    parser.add_argument("-i", "--iface", help="Interface name to sniff on.")
    parser.add_argument("-c", "--count", type=int, default=0, help="Number of packets to capture (0 = infinite).")
    parser.add_argument("-f", "--filter", help="BPF filter string (e.g., 'tcp or udp').", default=None)
    parser.add_argument("--show-features", action="store_true", help="Print extracted feature dict for each packet.")
    parser.add_argument("--log-features", help="Append extractor features to CSV files (e.g., logs/realtime_features.csv)")
    parser.add_argument("--min-packets", type=int, default=2, help="Minimum packets seen in a flow before logging (default 2).")
    parser.add_argument("--debug", action="store_true", help="Print debug info about CSV rows before writing.")
    parser.add_argument("--cleanup-interval", type=int, default=60, help="Background cleanup interval in seconds (0 disables).")
    parser.add_argument("--model", help="Local model bundle basename in detection-engine/models (e.g., 'realtime_rf' or 'lgb') or full --model-path")
    parser.add_argument("--model-path", help="Direct path to model bundle (.pkl/.joblib) overrides --model")
    parser.add_argument("--threshold", type=float, default=0.5, help="Probability threshold for ATTACK label when model present")
    parser.add_argument("--verbose", action="store_true", help="Verbose model loading output")
    args = parser.parse_args()

    # resolve model path if provided
    model_path = None
    if args.model_path:
        model_path = args.model_path
    elif args.model:
        # attempt to find model file in detection-engine/models by common names
        md = args.model.lower()
        candidates = [f"{md}.pkl", f"{md}.joblib", f"{md}_model.pkl", f"{md}_model.joblib", md + ".model"]
        models_dir = os.path.join(HERE, "models")
        for c in candidates:
            p = os.path.join(models_dir, c)
            if os.path.exists(p):
                model_path = p
                break
        # fallback to any pkl/joblib containing md
        if model_path is None and os.path.exists(models_dir):
            for f in os.listdir(models_dir):
                if f.lower().endswith((".pkl", ".joblib")) and md in f.lower():
                    model_path = os.path.join(models_dir, f)
                    break
        if model_path is None:
            print(f"⚠️  Model '{args.model}' not found in {models_dir}. Continuing without model.")
            model_path = None

    main(interface=args.iface, count=args.count, bpf_filter=args.filter,
         show_features=args.show_features, log_features=args.log_features,
         min_packets=args.min_packets, debug=args.debug, cleanup_interval=args.cleanup_interval,
         model_path=model_path, threshold=args.threshold, verbose=args.verbose)