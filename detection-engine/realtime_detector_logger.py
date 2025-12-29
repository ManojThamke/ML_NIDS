#!/usr/bin/env python3
"""
🗓️ Day 47 – Realtime Detector Logger (Backend Integrated)
--------------------------------------------------------
✅ Supports:
   1. Test CSV mode
   2. Live sniff mode
✅ Logs to CSV
✅ Sends alerts to Backend (POST /alerts)
"""

import os
import sys
import argparse
import datetime
import json
import joblib
import pandas as pd
import requests

# ================= BACKEND CONFIG =================
BACKEND_URL = "http://localhost:5000/alerts"

# ================= SCAPY IMPORT ===================
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    SCAPY = True
except Exception:
    SCAPY = False

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))

# ================= FEATURE EXTRACTOR ==============
if HERE not in sys.path:
    sys.path.insert(0, HERE)

try:
    from feature_extractor import FeatureExtractor
except Exception:
    FeatureExtractor = None

# ================= TIME HELPER ====================
def now_iso():
    return datetime.datetime.now().isoformat()

# ================= MODEL BUNDLE ===================
class ModelBundle:
    def __init__(self, path, verbose=False):
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        self.bundle = joblib.load(path)
        self.model = self.bundle.get("model")
        self.scaler = self.bundle.get("scaler")
        self.feature_cols = self.bundle.get("feature_cols") or self.bundle.get("feature_columns")

        if verbose:
            print(
                f"🔌 Model loaded: {os.path.basename(path)} "
                f"with {len(self.feature_cols) if self.feature_cols else '?'} features"
            )

    def prepare(self, feat_dict):
        if self.feature_cols:
            row = [feat_dict.get(c, 0.0) for c in self.feature_cols]
            return pd.DataFrame([row], columns=self.feature_cols)
        return pd.DataFrame([feat_dict])

    def predict(self, feat_dict):
        X = self.prepare(feat_dict)

        try:
            Xp = self.scaler.transform(X) if self.scaler is not None else X
        except Exception:
            Xp = X

        pred = int(self.model.predict(Xp)[0])
        prob = None
        try:
            if hasattr(self.model, "predict_proba"):
                prob = float(self.model.predict_proba(Xp)[0][1])
        except Exception:
            pass

        return pred, prob

# ================= CSV LOGGER =====================
def append_row(log_file, row):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    df = pd.DataFrame([row])
    header = not os.path.exists(log_file)
    df.to_csv(log_file, mode="a", header=header, index=False, encoding="utf-8")

# ================= BACKEND POST ===================
def send_alert_to_backend(row, model_name):
    payload = {
        "timestamp": row.get("timestamp"),
        "sourceIP": row.get("src"),
        "destinationIP": row.get("dst"),
        "modelUsed": model_name,
        "probability": row.get("prob"),
        "finalLabel": "ATTACK" if "ATTACK" in row.get("label", "") else "BENIGN"
    }

    try:
        res = requests.post(BACKEND_URL, json=payload, timeout=3)
        if res.status_code != 201:
            print("⚠️ Backend rejected alert:", res.text)
    except Exception as e:
        print("⚠️ Backend POST failed:", e)

# ================= TEST MODE ======================
def load_features_csv(csv_path):
    df = pd.read_csv(csv_path)
    if "features" in df.columns:
        return [json.loads(f) for f in df["features"].fillna("{}")], df
    return [row.dropna().to_dict() for _, row in df.iterrows()], df

def run_test_mode(bundle, csv_path, threshold, log_file, model_name):
    feats, _ = load_features_csv(csv_path)
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

        append_row(log_file, row)
        send_alert_to_backend(row, model_name)

        print(f"[{ts}] Row {i} → pred={pred} prob={prob} → {label}")

# ================= LIVE MODE ======================
def run_live_mode(bundle, extractor, threshold, log_file, iface, bpf, model_name):
    if not SCAPY:
        raise RuntimeError("❌ Scapy not available.")

    print(f"🛰️ Live sniff started (iface={iface}, filter={bpf}, threshold={threshold})")

    def on_packet(pkt):
        ts = now_iso()
        src = dst = proto = "N/A"

        if IP in pkt:
            ip = pkt[IP]
            src, dst = ip.src, ip.dst
            proto = "TCP" if TCP in pkt else "UDP" if UDP in pkt else "ICMP"

        try:
            feats = extractor.process_packet(pkt)
        except Exception:
            return

        if not feats:
            return

        pred, prob = bundle.predict(feats)
        label = "ATTACK 🚨" if prob is not None and prob >= threshold else "BENIGN ✅"

        row = {
            "timestamp": ts,
            "src": src,
            "dst": dst,
            "proto": proto,
            "pred": pred,
            "prob": prob,
            "label": label,
            "features": json.dumps(feats)
        }

        append_row(log_file, row)
        send_alert_to_backend(row, model_name)

        print(f"[{ts}] {proto} {src} → {dst} | prob={prob} → {label}")

    sniff(iface=iface, prn=on_packet, store=False, filter=bpf)

# ================= MAIN ===========================
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--test_csv")
    p.add_argument("--iface")
    p.add_argument("--filter", default=None)
    p.add_argument("--threshold", type=float, default=0.5)
    p.add_argument("--log", default=os.path.join(ROOT, "logs", "realtime_detection.csv"))
    args = p.parse_args()

    model_name = os.path.basename(args.model)

    print(f"🔌 Loading model: {args.model}")
    bundle = ModelBundle(args.model, verbose=True)
    print(f"📝 Logging to: {args.log}")

    if args.test_csv:
        run_test_mode(bundle, args.test_csv, args.threshold, args.log, model_name)
    else:
        if FeatureExtractor is None:
            print("❌ FeatureExtractor not available.")
            sys.exit(1)

        extractor = FeatureExtractor()
        run_live_mode(bundle, extractor, args.threshold, args.log, args.iface, args.filter, model_name)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user. Log saved safely.")

# python detection-engine\realtime_detector_logger.py --model detection-engine/models/lightgbm_advanced.pkl --iface "Wi-Fi" --filter "tcp or udp" --threshold 0.9 --log logs/realtime_detection_live_lgb.csv