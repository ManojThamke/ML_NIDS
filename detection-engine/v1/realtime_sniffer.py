#!/usr/bin/env python3
"""
realtime_sniffer.py — Real-time sniffer + phase-2 feature extraction + optional live model prediction

Phase-2 updates:
 - Accepts advanced FeatureExtractor (many features).
 - Logs features as JSON (safe) or optionally as a flattened CSV (--flat).
 - Uses model.feature_cols if available for flat CSV order.
 - Keeps min-packets gating, background cleanup, and optional model prediction.

Usage examples:
  python detection-engine/realtime_sniffer.py --log-features logs/realtime_features.csv --iface "Wi-Fi" --filter "tcp or udp"
  python detection-engine/realtime_sniffer.py --log-features logs/realtime_features_flat.csv --flat --iface "Wi-Fi"
  python detection-engine/realtime_sniffer.py --model-path detection-engine/models/realtime_rf.pkl --threshold 0.4 --log-features logs/realtime_features.csv --verbose
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

HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Import the Phase-2 extractor you provided
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

# ---------- extractor + flow gating ----------
extractor = FeatureExtractor()

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

# ---------- background cleanup ----------
def background_cleanup(interval_seconds):
    if interval_seconds <= 0:
        return
    while True:
        try:
            time.sleep(interval_seconds)
            try:
                extractor.clear_older_than(seconds=max(300, interval_seconds*2))
            except Exception:
                pass
        except Exception:
            continue

# ---------- simple model wrapper ----------
class SimpleModelWrapper:
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
                # case-insensitive fallback
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

# ---------- CSV helpers ----------
def ensure_dir_for(path):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)

def append_json_row(path, ts, features):
    ensure_dir_for(path)
    header = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", encoding="utf-8") as fh:
        if header:
            fh.write("timestamp,features\n")
        # write JSON safely, escape double quotes inside JSON by using json.dumps for the features field
        row_json = json.dumps(features, ensure_ascii=False)
        # ensure to escape quotes within CSV properly by wrapping in double quotes
        fh.write(f"{ts},\"{row_json.replace('\"', '\"\"')}\"\n")

def write_flat_header(path, columns):
    ensure_dir_for(path)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(",".join(columns) + "\n")

def append_flat_row(path, columns, features):
    ensure_dir_for(path)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        write_flat_header(path, columns)
    row = []
    for c in columns:
        v = features.get(c, "")
        if isinstance(v, str):
            # escape commas / newlines
            v = v.replace("\n", " ").replace("\r", " ")
            v = v.replace(",", ";")
        row.append(str(v))
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(",".join(row) + "\n")

# ---------- main per-packet handler ----------
def on_packet(pkt, show_features=False, log_features=None, min_packets=2,
              debug=False, model_wrapper=None, threshold=0.5, flat=False, flat_columns=None):
    try:
        base_line = pkt_summary(pkt)
        label_line = ""
        features = None
        try:
            features = extractor.process_packet(pkt)
        except Exception as e:
            if debug:
                print(f"[{pretty_time()}] WARN feature extraction: {e}")
            features = None

        # model live prediction
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

        # print to console
        print(base_line + label_line)
        if features and show_features:
            try:
                feat_str = ", ".join(f"{k}={v}" for k, v in features.items())
                print("   →", feat_str)
            except Exception:
                pass

        # logging (only for TCP/UDP)
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

            ts = pretty_time()

            # default JSON logging (safe and recommended)
            if not flat:
                append_json_row(log_features, ts, features or {})
            else:
                # flat mode: need a column list
                cols = flat_columns
                if cols is None and model_wrapper and model_wrapper.feature_cols:
                    cols = ["timestamp"] + list(model_wrapper.feature_cols)
                if cols is None and features:
                    # first observed key ordering
                    cols = ["timestamp"] + list(features.keys())
                if cols is None:
                    # fallback to a minimal flat row
                    cols = ["timestamp", "Destination Port", "Flow Duration", "Fwd Packet Length Min", "Packet Length Std"]
                # ensure timestamp and values
                row_feats = {}
                row_feats["timestamp"] = ts
                for c in cols:
                    if c == "timestamp":
                        continue
                    row_feats[c] = features.get(c, "")
                append_flat_row(log_features, cols, row_feats)

    except Exception as e:
        print(f"[{pretty_time()}] ERROR processing packet: {e}")

# ---------- CLI / main ----------
def main(interface=None, count=0, bpf_filter=None, show_features=True, log_features=None,
         min_packets=2, debug=False, cleanup_interval=60, model_path=None, threshold=0.5,
         verbose=False, flat=False, flat_columns=None):
    print("📡 Starting sniffer...")
    print(f"   Interface: {interface or 'default'}  Filter: {bpf_filter or 'none'}  Min-packets: {min_packets}")
    if log_features:
        print(f"📝 Logging feature rows to: {os.path.abspath(log_features)} (flat={flat})")
    if model_path:
        print(f"🔌 Loading model for live prediction: {os.path.abspath(model_path)}")
    # start cleanup thread
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
                                       threshold=threshold,
                                       flat=flat,
                                       flat_columns=flat_columns),
              store=False,
              count=count,
              filter=bpf_filter)
    except KeyboardInterrupt:
        print("\n⛔ Stopped by user (KeyboardInterrupt).")
    except Exception as e:
        print(f"[{pretty_time()}] ERROR in sniffing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Realtime sniffer with Phase-2 feature extraction and optional live model prediction")
    parser.add_argument("-i", "--iface", help="Interface name to sniff on.")
    parser.add_argument("-c", "--count", type=int, default=0, help="Number of packets to capture (0 = infinite).")
    parser.add_argument("-f", "--filter", help="BPF filter string (e.g., 'tcp or udp').", default=None)
    parser.add_argument("--show-features", action="store_true", help="Print extracted feature dict for each packet.")
    parser.add_argument("--log-features", help="Append extractor features to CSV files (e.g., logs/realtime_features.csv)")
    parser.add_argument("--min-packets", type=int, default=2, help="Minimum packets seen in a flow before logging (default 2).")
    parser.add_argument("--debug", action="store_true", help="Print debug info about CSV rows before writing.")
    parser.add_argument("--cleanup-interval", type=int, default=60, help="Background cleanup interval in seconds (0 disables).")
    parser.add_argument("--model", help="Local model basename in detection-engine/models (e.g., 'realtime_rf' or 'lgb') or use --model-path")
    parser.add_argument("--model-path", help="Direct path to model bundle (.pkl/.joblib) overrides --model")
    parser.add_argument("--threshold", type=float, default=0.5, help="Probability threshold for ATTACK label when model present")
    parser.add_argument("--verbose", action="store_true", help="Verbose model loading output")
    parser.add_argument("--flat", action="store_true", help="Write flat CSV columns instead of JSON features (training-friendly)")
    parser.add_argument("--flat-columns", help="Comma-separated column names to force for flat CSV (overrides model feature order)")
    args = parser.parse_args()

    model_path = None
    if args.model_path:
        model_path = args.model_path
    elif args.model:
        md = args.model.lower()
        candidates = [f"{md}.pkl", f"{md}.joblib", f"{md}_model.pkl", f"{md}_model.joblib", md + ".model"]
        models_dir = os.path.join(HERE, "models")
        for c in candidates:
            p = os.path.join(models_dir, c)
            if os.path.exists(p):
                model_path = p
                break
        if model_path is None and os.path.exists(models_dir):
            for f in os.listdir(models_dir):
                if f.lower().endswith((".pkl", ".joblib")) and md in f.lower():
                    model_path = os.path.join(models_dir, f)
                    break
        if model_path is None:
            print(f"⚠️  Model '{args.model}' not found in {models_dir}. Continuing without model.")
            model_path = None

    flat_cols = None
    if args.flat_columns:
        flat_cols = [c.strip() for c in args.flat_columns.split(",") if c.strip()]

    main(interface=args.iface, count=args.count, bpf_filter=args.filter,
         show_features=args.show_features, log_features=args.log_features,
         min_packets=args.min_packets, debug=args.debug, cleanup_interval=args.cleanup_interval,
         model_path=model_path, threshold=args.threshold, verbose=args.verbose,
         flat=args.flat, flat_columns=flat_cols)
