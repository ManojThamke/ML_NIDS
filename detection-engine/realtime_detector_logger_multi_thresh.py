#!/usr/bin/env python3
"""
Realtime Detector Logger — Multi-threshold (Day 33)
--------------------------------------------------
- Supports multiple thresholds: --thresholds 0.5,0.7,0.9
- Test CSV mode and live sniff mode (Scapy).
- Logs timestamp, src, dst, proto, features, pred, prob, and alert@<threshold> columns.
- Emoji/interactive console prints.

Usage (test CSV):
  python detection-engine\realtime_detector_logger_multi_thresh.py \
 --model detection-engine/models/realtime_rf.pkl \
 --test_csv logs/realtime_features.csv \
 --thresholds 0.5,0.7,0.9 \
 --log logs/realtime_detection_test_rf_multi.csv

Usage (live sniff):
  (Run terminal as Admin on Windows)
  python detection-engine\realtime_detector_logger_multi_thresh.py \
    --model detection-engine/models/realtime_rf.pkl \
    --iface "Wi-Fi" --filter "tcp or udp" \
    --thresholds 0.5,0.7,0.9 \
    --log logs/realtime_detection_live_rf_multi.csv

    python detection-engine\realtime_sniffer.py --show-features --filter "tcp or udp" --log-features logs/realtime_features.csv

python detection-engine\realtime_detector_logger_multi_thresh.py --model detection-engine/models/xgboost_advanced.pkl --iface "Wi-Fi" --thresholds 0.5,0.7,0.9 --log logs/realtime_detection_live_xgb_multi.csv

"""
import os
import sys
import argparse
import datetime
import json
import joblib
import pandas as pd
from typing import List

# scapy import optional
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    SCAPY = True
except Exception:
    SCAPY = False

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))

# ensure detection-engine directory on path for feature_extractor import
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    from feature_extractor import FeatureExtractor
except Exception:
    FeatureExtractor = None

# ------------------------------
# Helpers
# ------------------------------
def now_iso():
    return datetime.datetime.now().isoformat()

def parse_thresholds(s: str) -> List[float]:
    parts = [p.strip() for p in s.split(",") if p.strip() != ""]
    floats = []
    for p in parts:
        try:
            floats.append(float(p))
        except Exception:
            raise argparse.ArgumentTypeError(f"Invalid threshold value: {p}")
    if not floats:
        raise argparse.ArgumentTypeError("At least one threshold required.")
    # sort ascending for readability
    return sorted(list(dict.fromkeys(floats)))

# ------------------------------
# Model bundle wrapper
# ------------------------------
class ModelBundle:
    def __init__(self, path, verbose=False):
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        try:
            bundle = joblib.load(path)
        except Exception as e:
            raise RuntimeError(f"Failed loading model bundle: {e}")
        self.model = bundle.get("model") or bundle.get("estimator") or bundle.get("clf") or bundle.get("pipeline")
        self.scaler = bundle.get("scaler")
        self.feature_cols = bundle.get("feature_cols") or bundle.get("feature_columns") or None
        if verbose:
            print(f"🔌 Model loaded: {os.path.basename(path)}  features: {len(self.feature_cols) if self.feature_cols else '?'}")
        if self.model is None:
            raise ValueError("Model bundle missing 'model' object.")

    def _safe_float(self, v):
        try:
            return float(v)
        except Exception:
            return 0.0

    def prepare_df(self, feat: dict):
        # Ensure numeric values and column order matches feature_cols if available
        if self.feature_cols:
            row = []
            for c in self.feature_cols:
                # try case-insensitive lookup
                val = feat.get(c, None)
                if val is None:
                    for k in feat:
                        if str(k).strip().lower() == str(c).strip().lower():
                            val = feat[k]
                            break
                row.append(self._safe_float(val))
            return pd.DataFrame([row], columns=self.feature_cols)
        else:
            # fallback: try convert all keys
            return pd.DataFrame([{k: self._safe_float(v) for k, v in feat.items()}])

    def predict(self, feat: dict):
        X = self.prepare_df(feat)
        # apply scaler if present
        X_proc = X
        try:
            if self.scaler is not None:
                arr = self.scaler.transform(X)
                # preserve column names if possible
                try:
                    X_proc = pd.DataFrame(arr, columns=X.columns)
                except Exception:
                    X_proc = arr
            else:
                X_proc = X
        except Exception:
            X_proc = X
        # predict
        pred = int(self.model.predict(X_proc)[0])
        prob = None
        try:
            if hasattr(self.model, "predict_proba"):
                prob = float(self.model.predict_proba(X_proc)[0][1])
            elif hasattr(self.model, "decision_function"):
                import math
                val = float(self.model.decision_function(X_proc)[0])
                prob = 1.0 / (1.0 + math.exp(-val))
        except Exception:
            prob = None
        return pred, prob

# ------------------------------
# Logging utilities
# ------------------------------
def ensure_log_header(log_file: str, thresholds: List[float], extra_cols: List[str] = None):
    """
    If log file does not exist, create it with header columns:
    timestamp, src, dst, proto, pred, prob, alert@<t1>, alert@<t2>, ..., features
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    if os.path.exists(log_file):
        return
    base_cols = ["timestamp", "src", "dst", "proto", "pred", "prob"]
    thresh_cols = [f"alert@{t:.2f}" for t in thresholds]
    extras = extra_cols or []
    cols = base_cols + thresh_cols + extras + ["features"]
    pd.DataFrame(columns=cols).to_csv(log_file, index=False)

def append_log_row(log_file: str, row: dict):
    # append a single row (safe)
    df = pd.DataFrame([row])
    df.to_csv(log_file, mode="a", header=False, index=False, encoding="utf-8")

# ------------------------------
# CSV loader for test mode
# ------------------------------
def load_features_csv(csv_path: str, model_features=None, verbose=False):
    """
    Returns list of feature dicts. Handles:
     - CSV with a 'features' JSON column
     - CSV with proper header feature columns
     - Headerless numeric CSV (attempt to map to model_features by position)
    """
    if verbose:
        print(f"📁 Loading CSV: {csv_path}")
    try:
        df = pd.read_csv(csv_path, low_memory=False)
    except Exception:
        df = pd.read_csv(csv_path, low_memory=False, engine="python")

    if "features" in df.columns:
        out = []
        for v in df["features"].fillna("").astype(str):
            if v.strip() == "":
                out.append({})
                continue
            try:
                out.append(json.loads(v))
            except Exception:
                try:
                    import ast
                    out.append(ast.literal_eval(v))
                except Exception:
                    out.append({})
        return out

    # If header looks like feature names (alphabetic)
    cols = df.columns.tolist()
    if any(any(ch.isalpha() for ch in str(c)) for c in cols):
        return [row.dropna().to_dict() for _, row in df.iterrows()]

    # headerless numeric CSV -> map by position
    raw = pd.read_csv(csv_path, header=None, low_memory=False)
    if model_features and raw.shape[1] == len(model_features):
        out = []
        for _, r in raw.iterrows():
            d = {model_features[i]: r.iat[i] for i in range(len(model_features))}
            out.append(d)
        return out
    if model_features and raw.shape[1] > len(model_features):
        start = raw.shape[1] - len(model_features)
        out = []
        for _, r in raw.iterrows():
            d = {model_features[i]: r.iat[start + i] for i in range(len(model_features))}
            out.append(d)
        return out

    # fallback to header->dict
    return [row.dropna().to_dict() for _, row in df.iterrows()]

# ------------------------------
# Modes
# ------------------------------
def run_test_mode(bundle: ModelBundle, csv_path: str, thresholds: List[float], log_file: str, verbose=False):
    feats = load_features_csv(csv_path, model_features=bundle.feature_cols, verbose=verbose)
    print(f"📂 Test mode: {len(feats)} feature rows from {csv_path}")
    ensure_log_header(log_file, thresholds)
    for i, f in enumerate(feats):
        ts = now_iso()
        try:
            pred, prob = bundle.predict(f)
        except Exception as e:
            print(f"[{ts}] ⚠️ Prediction error row {i}: {e}")
            continue
        # build row
        row = {
            "timestamp": ts,
            "src": f.get("src", "") or f.get("Source IP", "") or "",
            "dst": f.get("dst", "") or f.get("Destination IP", "") or "",
            "proto": f.get("proto", "") or ""
        }
        row["pred"] = int(pred)
        row["prob"] = float(prob) if prob is not None else ""
        for t in thresholds:
            key = f"alert@{t:.2f}"
            row[key] = int(1 if (prob is not None and prob >= t) else 0)
        row["features"] = json.dumps(f, ensure_ascii=False)
        # console print
        label_summary = ", ".join([f"{t:.2f}:{row[f'alert@{t:.2f}']}" for t in thresholds])
        print(f"[{ts}] row={i} -> pred={pred} prob={prob} | alerts: {label_summary}")
        append_log_row(log_file, row)
    print("✅ Test mode complete. Log appended.")

def run_live_mode(bundle: ModelBundle, extractor, thresholds: List[float], log_file: str, iface: str, bpf: str):
    if not SCAPY:
        raise RuntimeError("Scapy not available — cannot run live mode.")
    ensure_log_header(log_file, thresholds)
    print(f"🛰️ Live sniff starting on iface='{iface or 'default'}' filter='{bpf or 'none'}' thresholds={thresholds}")
    def on_packet(pkt):
        ts = now_iso()
        src = dst = proto = ""
        try:
            if IP in pkt:
                ip = pkt[IP]
                src = getattr(ip, "src", "") or ""
                dst = getattr(ip, "dst", "") or ""
                proto = "TCP" if TCP in pkt else "UDP" if UDP in pkt else "ICMP" if ICMP in pkt else str(getattr(ip, "proto", "IP"))
            else:
                proto = pkt.name if hasattr(pkt, "name") else ""
        except Exception:
            pass
        try:
            f = extractor.process_packet(pkt)
        except Exception as e:
            print(f"[{ts}] ⚠️ Feature extraction error: {e}")
            return
        if not f:
            return
        try:
            pred, prob = bundle.predict(f)
        except Exception as e:
            print(f"[{ts}] ⚠️ Prediction error: {e}")
            return
        row = {"timestamp": ts, "src": src, "dst": dst, "proto": proto}
        row["pred"] = int(pred)
        row["prob"] = float(prob) if prob is not None else ""
        for t in thresholds:
            row[f"alert@{t:.2f}"] = int(1 if (prob is not None and prob >= t) else 0)
        row["features"] = json.dumps(f, ensure_ascii=False)
        label_summary = ", ".join([f"{t:.2f}:{row[f'alert@{t:.2f}']}" for t in thresholds])
        print(f"[{ts}] {proto} {src} -> {dst}  pred={pred} prob={prob} | alerts: {label_summary}")
        append_log_row(log_file, row)
    sniff(iface=iface, prn=on_packet, store=False, filter=bpf)

# ------------------------------
# CLI
# ------------------------------
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="Path to model bundle .pkl/.joblib")
    p.add_argument("--test_csv", help="Run test mode with CSV of features")
    p.add_argument("--iface", help="Network interface for live sniff")
    p.add_argument("--filter", dest="bpf", help="BPF filter string (e.g. 'tcp or udp')")
    p.add_argument("--thresholds", type=parse_thresholds, default="0.5", help="Comma-separated thresholds, e.g. 0.5,0.7,0.9")
    p.add_argument("--log", default=os.path.join(ROOT, "logs", "realtime_detection_multi.csv"), help="CSV log path")
    p.add_argument("--no_extractor", action="store_true", help="Skip FeatureExtractor import (test_csv only)")
    p.add_argument("--verbose", action="store_true", help="Verbose prints")
    args = p.parse_args()

    model_path = os.path.abspath(args.model)
    print(f"🔌 Loading model bundle: {model_path}")
    try:
        bundle = ModelBundle(model_path, verbose=args.verbose)
    except Exception as e:
        print("❌ Failed to load model:", e)
        sys.exit(1)

    thresholds = args.thresholds
    if isinstance(thresholds, str):
        thresholds = parse_thresholds(thresholds)
    print(f"📝 Logging to: {os.path.abspath(args.log)}")
    print(f"🎯 Thresholds: {thresholds}")

    # Test mode
    if args.test_csv:
        run_test_mode(bundle, args.test_csv, thresholds, args.log, verbose=args.verbose)
        return

    # Live mode
    if FeatureExtractor is None and not args.no_extractor:
        print("❌ FeatureExtractor not available. Cannot run live mode. Use --no_extractor only for test CSV mode.")
        sys.exit(1)
    extractor = None if args.no_extractor else FeatureExtractor()
    try:
        run_live_mode(bundle, extractor, thresholds, args.log, iface=args.iface, bpf=args.bpf)
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user. Log file saved.")

if __name__ == "__main__":
    main()
