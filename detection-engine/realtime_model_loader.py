# detection-engine/realtime_model_loader.py
"""
Realtime Model Loader & Runner (Day 29)

Usage (live sniff):
  python realtime_model_loader.py --model detection-engine/models/realtime_rf.pkl \
      --threshold 0.5 --log ../logs/realtime_predictions.csv

Usage (test from csv of features):
  python realtime_model_loader.py --model detection-engine/models/realtime_rf.pkl \
      --test_csv ../logs/realtime_features.csv --threshold 0.5

Notes:
- Expects model bundles saved with joblib.dump({"model": model, "scaler": scaler, "feature_cols": [...]})
  but will accept several common key names (feature_columns, feature_cols).
- Writes CSV with columns: timestamp,src,dst,proto,features_json,pred,prob,alert (0/1)
"""
import os
import sys
import argparse
import datetime
import json
import joblib
import pandas as pd
from pathlib import Path

# scapy import is optional if you only want test_csv mode
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    SCAPY_AVAILABLE = True
except Exception:
    SCAPY_AVAILABLE = False

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))

# local feature extractor (your project has this file)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    from feature_extractor import FeatureExtractor
except Exception as e:
    FeatureExtractor = None
    # We will still allow test_csv mode without FeatureExtractor

def pretty_time():
    return datetime.datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class RealtimeModel:
    def __init__(self, model_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        self.bundle = joblib.load(model_path)
        # common key names
        self.model = self.bundle.get("model") or self.bundle.get("estimator") or self.bundle.get("clf") or self.bundle.get("pipeline")
        self.scaler = self.bundle.get("scaler")
        self.feature_cols = self.bundle.get("feature_cols") or self.bundle.get("feature_columns") or self.bundle.get("feature_columns_list")
        # fallback: if user saved only a model without feature list, try to accept it but warn
        if self.model is None:
            raise ValueError("Loaded bundle does not contain a 'model' object.")
        if self.feature_cols is None:
            print("WARNING: No feature list found in model bundle. You must pass features in correct order.")
            self.feature_cols = None

    def prepare_row(self, features: dict):
        """
        Given a dict of feature_name -> value, return a 2D array / dataframe ready for model.
        Ensures column order matches feature_cols if available; fills missing with 0.
        """
        if self.feature_cols:
            row = []
            for c in self.feature_cols:
                v = features.get(c)
                # if not present, fill 0
                if v is None:
                    row.append(0.0)
                else:
                    try:
                        row.append(float(v))
                    except Exception:
                        # last resort: try numeric conversion, else 0
                        try:
                            row.append(float(str(v).strip()))
                        except Exception:
                            row.append(0.0)
            # create DataFrame with same column names (helps scaler if expecting names)
            df = pd.DataFrame([row], columns=self.feature_cols)
        else:
            # feature order unknown: use insertion order of dict
            df = pd.DataFrame([features])
        return df

    def predict(self, features: dict):
        """
        Returns: pred (int 0/1), prob (float or None)
        """
        X = self.prepare_row(features)
        # apply scaler if present and if scaler expects same columns (scaler could be pipeline)
        try:
            if self.scaler is not None:
                # scaler.transform accepts DataFrame or ndarray
                X_scaled = self.scaler.transform(X)
            else:
                # if model is a pipeline, it may include scaler; so pass as-is
                X_scaled = X.values
        except Exception:
            # fallback: try model directly on X (it might be a pipeline)
            X_scaled = X.values

        try:
            pred = int(self.model.predict(X_scaled)[0])
        except Exception as e:
            # if predict fails, raise
            raise RuntimeError(f"Model predict failed: {e}")

        prob = None
        try:
            if hasattr(self.model, "predict_proba"):
                prob = float(self.model.predict_proba(X_scaled)[0][1])
            elif hasattr(self.model, "decision_function"):
                # map decision to [0,1] via sigmoid for approximate probability
                import math
                val = float(self.model.decision_function(X_scaled)[0])
                prob = 1.0 / (1.0 + math.exp(-val))
        except Exception:
            prob = None

        return pred, prob

def write_log_row(log_file, row: dict):
    # ensure logs directory exists for relative path
    log_path = os.path.abspath(log_file)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    df_row = pd.DataFrame([row])
    header = not os.path.exists(log_path)
    df_row.to_csv(log_path, mode="a", header=header, index=False)

def load_features_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    # expect one column per feature (or a 'features' JSON column)
    # if features column exists, parse JSON
    if "features" in df.columns:
        parsed = df["features"].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
        return parsed.tolist(), df
    else:
        # convert each row to dict
        return [row.dropna().to_dict() for _, row in df.iterrows()], df

def live_sniff_loop(model_obj: RealtimeModel, extractor: FeatureExtractor, threshold: float, log_file: str, iface=None, bpf_filter=None, count=0):
    if not SCAPY_AVAILABLE:
        raise RuntimeError("Scapy not available on this environment. Install scapy to use live sniff mode.")

    print(f"Starting live sniff. Interface: {iface or 'default'}, Filter: {bpf_filter or 'none'}, Threshold: {threshold}")
    def on_packet(pkt):
        ts = datetime.datetime.now().isoformat()
        # basic src/dst/proto
        proto = ""
        src = ""
        dst = ""
        try:
            if IP in pkt:
                ip = pkt[IP]
                src = getattr(ip, "src", "") or ""
                dst = getattr(ip, "dst", "") or ""
                if TCP in pkt:
                    proto = "TCP"
                elif UDP in pkt:
                    proto = "UDP"
                elif ICMP in pkt:
                    proto = "ICMP"
                else:
                    proto = str(getattr(ip, "proto", "IP"))
            else:
                proto = pkt.name if hasattr(pkt, "name") else "NONIP"
        except Exception:
            proto = "UNKNOWN"
        # extract features via extractor
        try:
            features = extractor.process_packet(pkt)
            if not features:
                return
        except Exception as e:
            print(f"[{ts}] feature extraction error: {e}")
            return

        try:
            pred, prob = model_obj.predict(features)
            alert = 1 if (prob is not None and prob >= threshold) or (prob is None and pred==1) else 0
            row = {
                "timestamp": ts,
                "src": src,
                "dst": dst,
                "proto": proto,
                "features": json.dumps(features),
                "pred": int(pred),
                "prob": float(prob) if prob is not None else "",
                "alert": int(alert)
            }
            print(f"[{ts}] {proto} {src} -> {dst}  >> pred={pred} prob={prob} alert={alert}")
            write_log_row(log_file, row)
        except Exception as e:
            print(f"[{ts}] ERROR predicting: {e}")

    sniff(iface=iface, prn=on_packet, store=False, count=count, filter=bpf_filter)

def test_mode_from_csv(model_obj: RealtimeModel, csv_path: str, threshold: float, log_file: str):
    feats_list, raw_df = load_features_from_csv(csv_path)
    for i, features in enumerate(feats_list):
        ts = datetime.datetime.now().isoformat()
        try:
            pred, prob = model_obj.predict(features)
            alert = 1 if (prob is not None and prob >= threshold) or (prob is None and pred==1) else 0
            row = {
                "timestamp": ts,
                "row": i,
                "features": json.dumps(features),
                "pred": int(pred),
                "prob": float(prob) if prob is not None else "",
                "alert": int(alert)
            }
            print(f"[{ts}] row={i} pred={pred} prob={prob} alert={alert}")
            write_log_row(log_file, row)
        except Exception as e:
            print(f"[{ts}] ERROR predicting row {i}: {e}")

def main():
    p = argparse.ArgumentParser(description="Realtime model loader and runner")
    p.add_argument("--model", required=True, help="Path to model .pkl or .joblib bundle")
    p.add_argument("--threshold", type=float, default=0.5, help="Probability threshold for alert (default 0.5)")
    p.add_argument("--log", default=os.path.join("..", "logs", "realtime_predictions.csv"), help="CSV file to append predictions")
    p.add_argument("--iface", help="Interface to sniff on (live mode)")
    p.add_argument("--filter", dest="bpf", help="BPF filter for sniff (e.g. 'tcp or udp')")
    p.add_argument("--count", type=int, default=0, help="Number of packets to capture (0 = infinite)")
    p.add_argument("--test_csv", help="If provided, run in test mode using CSV of features instead of live sniffing")
    p.add_argument("--no_extractor", action="store_true", help="If set, do not import feature_extractor (useful for test_csv that already has features)")
    args = p.parse_args()

    model_path = os.path.abspath(args.model)
    print("Loading model:", model_path)
    model_obj = RealtimeModel(model_path)

    # If test_csv and bundle missing feature list, allow test mode anyway.
    if args.test_csv:
        print("Running test mode from CSV:", args.test_csv)
        test_mode_from_csv(model_obj, args.test_csv, args.threshold, args.log)
        print("Test mode complete.")
        return

    # Live mode: need FeatureExtractor available unless user opted out
    if FeatureExtractor is None and not args.no_extractor:
        raise SystemExit("feature_extractor not importable. Ensure detection-engine/feature_extractor.py exists and is on PYTHONPATH.")

    extractor = None
    if not args.no_extractor:
        extractor = FeatureExtractor()
    else:
        print("No extractor requested. Running live mode without feature extraction is not supported.")

    # run live sniff
    try:
        live_sniff_loop(model_obj, extractor, args.threshold, args.log, iface=args.iface, bpf_filter=args.bpf, count=args.count)
    except KeyboardInterrupt:
        print("Stopped by user (KeyboardInterrupt).")
    except Exception as e:
        print("Runtime error in live sniff:", e)

if __name__ == "__main__":
    main()

