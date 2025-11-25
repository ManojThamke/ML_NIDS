#!/usr/bin/env python3
"""
🗓️ Day 32 – Realtime Detector Logger
------------------------------------
✅ Supports two modes:
   1. Test CSV mode (--test_csv logs/realtime_features.csv)
   2. Live sniff mode (--iface "Wi-Fi" --filter "tcp or udp")
python detection-engine\realtime_detector_logger.py --model detection-engine/models/lightgbm_advanced.pkl --iface "Wi-Fi" --filter "tcp or udp" --threshold 0.9 --log logs/realtime_detection_live_lgb.csv
python detection-engine\realtime_detector_logger_multi_thresh.py --model detection-engine/models/realtime_rf.pkl --iface "Wi-Fi" --thresholds 0.5,0.7,0.9 --log logs/realtime_detection_live_rf_multi.csv
python detection-engine\realtime_detector_logger.py --model detection-engine/models/xgboost_advanced.pkl --iface "Wi-Fi" --filter "tcp or udp" --threshold 0.9 --log logs/realtime_detection_live_xgb.csv
xgboost_advanced
📂 Logs are always written to CSV (default: logs/realtime_detection.csv).
💡 Ensures file saves even if interrupted (Ctrl+C).
"""

import os
import sys
import argparse
import datetime
import json
import joblib
import pandas as pd

# 🛰️ Try importing scapy for live sniff
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    SCAPY = True
except Exception:
    SCAPY = False

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))

# 📦 Feature extractor for live packets
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    from feature_extractor import FeatureExtractor
except Exception:
    FeatureExtractor = None


# 🕒 Time helper
def now_iso():
    return datetime.datetime.now().isoformat()


# 🎯 Model Loader
class ModelBundle:
    def __init__(self, path, verbose=False):
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        self.bundle = joblib.load(path)
        self.model = self.bundle.get("model")
        self.scaler = self.bundle.get("scaler")
        self.feature_cols = self.bundle.get("feature_cols") or self.bundle.get("feature_columns")
        if verbose:
            print(f"🔌 Model loaded: {os.path.basename(path)} with {len(self.feature_cols) if self.feature_cols else '?'} features")

    def prepare(self, feat_dict):
        """Align features with model columns"""
        if self.feature_cols:
            row = [feat_dict.get(c, 0.0) for c in self.feature_cols]
            df = pd.DataFrame([row], columns=self.feature_cols)
        else:
            df = pd.DataFrame([feat_dict])
        return df

    def predict(self, feat_dict):
        X = self.prepare(feat_dict)
        try:
            if self.scaler is not None:
                X_proc = self.scaler.transform(X)
            else:
                X_proc = X
        except Exception:
            X_proc = X

        pred = int(self.model.predict(X_proc)[0])
        prob = None
        try:
            if hasattr(self.model, "predict_proba"):
                prob = float(self.model.predict_proba(X_proc)[0][1])
        except Exception:
            pass
        return pred, prob


# ✍️ Append to CSV log
def append_row(log_file, row):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    df = pd.DataFrame([row])
    header = not os.path.exists(log_file)
    df.to_csv(log_file, mode="a", header=header, index=False, encoding="utf-8")


# 📂 Load features from CSV for test mode
def load_features_csv(csv_path):
    df = pd.read_csv(csv_path)
    if "features" in df.columns:  # JSON features column
        return [json.loads(f) if isinstance(f, str) else {} for f in df["features"].fillna("")], df
    else:  # each column is a feature
        return [row.dropna().to_dict() for _, row in df.iterrows()], df


# 🧪 Test Mode
def run_test_mode(bundle, csv_path, threshold, log_file):
    feats, df = load_features_csv(csv_path)
    print(f"📂 Loaded {len(feats)} rows from {csv_path}")
    for i, f in enumerate(feats):
        ts = now_iso()
        pred, prob = bundle.predict(f)
        label = "ATTACK 🚨" if prob is not None and prob >= threshold else "BENIGN ✅"
        row = {
            "timestamp": ts,
            "src": f.get("src", "N/A"),
            "dst": f.get("dst", "N/A"),
            "proto": f.get("proto", "N/A"),
            "pred": pred,
            "prob": prob,
            "label": label,
            "features": json.dumps(f)
        }
        print(f"[{ts}] Row {i} → pred={pred} prob={prob} → {label}")
        append_row(log_file, row)
    print("📝 Test mode complete. Log saved.")


# 🌐 Live Mode
def run_live_mode(bundle, extractor, threshold, log_file, iface, bpf):
    if not SCAPY:
        raise RuntimeError("❌ Scapy not available, cannot run live sniffing.")
    print(f"🛰️ Live sniff started (iface={iface}, filter={bpf}, threshold={threshold})")

    def on_packet(pkt):
        ts = now_iso()
        src = dst = proto = "N/A"
        try:
            if IP in pkt:
                ip = pkt[IP]
                src, dst = ip.src, ip.dst
                proto = "TCP" if TCP in pkt else "UDP" if UDP in pkt else "ICMP"
        except Exception:
            pass

        try:
            f = extractor.process_packet(pkt)
        except Exception:
            return
        if not f:
            return

        pred, prob = bundle.predict(f)
        label = "ATTACK 🚨" if prob is not None and prob >= threshold else "BENIGN ✅"
        row = {
            "timestamp": ts,
            "src": src,
            "dst": dst,
            "proto": proto,
            "pred": pred,
            "prob": prob,
            "label": label,
            "features": json.dumps(f)
        }
        print(f"[{ts}] {proto} {src} -> {dst} → pred={pred} prob={prob} → {label}")
        append_row(log_file, row)

    sniff(iface=iface, prn=on_packet, store=False, filter=bpf)


# 🏁 Main
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="Path to model .pkl/.joblib bundle")
    p.add_argument("--test_csv", help="Run in test mode with features CSV")
    p.add_argument("--iface", help="Interface for live sniffing (e.g., Wi-Fi)")
    p.add_argument("--filter", help="BPF filter (e.g., 'tcp or udp')", default=None)
    p.add_argument("--threshold", type=float, default=0.5, help="Probability threshold")
    p.add_argument("--log", default=os.path.join(ROOT, "logs", "realtime_detection.csv"), help="CSV log path")
    args = p.parse_args()

    print(f"🔌 Loading model: {args.model}")
    bundle = ModelBundle(args.model, verbose=True)
    print(f"📝 Logging to: {args.log}")

    if args.test_csv:
        run_test_mode(bundle, args.test_csv, args.threshold, args.log)
    else:
        if FeatureExtractor is None:
            print("❌ FeatureExtractor not available. Cannot run live mode.")
            sys.exit(1)
        extractor = FeatureExtractor()
        run_live_mode(bundle, extractor, args.threshold, args.log, args.iface, args.filter)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user. Log saved safely.")
# python .\detection-engine\realtime_detector_multi.py --models lgb,rf,xgb,svm --model-paths "detection-engine\models\lightgbm_advanced.pkl,detection-engine\models\realtime_rf.pkl,detection-engine\models\xgboost_advanced.pkl,detection-engine\models\svm.pkl" --iface "Wi-Fi" --filter "tcp or udp" --agg max --smooth 3 --threshold 0.35 --log "logs\realtime_predictions_ensemble_live.csv" --verbose