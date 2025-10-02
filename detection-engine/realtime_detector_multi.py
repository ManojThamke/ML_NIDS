#!/usr/bin/env python3
"""
Realtime detector (Day 30) - multi-model loader & runner

Save as: detection-engine/realtime_detector_multi.py

Usage (test CSV):
  python detection-engine\realtime_detector_multi.py --model xgb --test_csv logs/realtime_features.csv --threshold 0.5 --log logs/realtime_predictions_xgb.csv

Usage (live sniff):
  python detection-engine\realtime_detector_multi.py --model rf --iface "Wi-Fi" --filter "tcp or udp" --threshold 0.5 --log logs/realtime_predictions_live_rf.csv
python detection-engine\realtime_detector_multi.py `
  --model rf `
  --iface "Wi-Fi" `
  --filter "tcp or udp" `
  --threshold 0.4 `
  --log logs/realtime_predictions_live_rf.csv `
  --verbose
Notes:
 - Model bundle expected: joblib.dump({"model": <est>, "scaler": <scaler_or_None>, "feature_cols": [...]})
 - Accepts .pkl or .joblib (auto-detects common names)
"""
import os
import sys
import argparse
import datetime
import json
import joblib
import pandas as pd
import math

# optional scapy for live sniff
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    SCAPY = True
except Exception:
    SCAPY = False

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
MODEL_DIR = os.path.join(HERE, "models")

# allow local imports
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    from feature_extractor import FeatureExtractor
except Exception:
    FeatureExtractor = None

def pretty_ts():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def find_model_path(model_choice_or_path):
    # if direct path given
    if model_choice_or_path and os.path.exists(model_choice_or_path):
        return os.path.abspath(model_choice_or_path)

    # otherwise try model_choice guesses
    m = (model_choice_or_path or "").lower()
    candidates = []
    if m in ("rf", "realtime_rf", "realtime-rf"):
        candidates = ["realtime_rf.pkl", "realtime_rf.joblib", "realtime_rf.model", "realtime-rf.pkl"]
    elif m in ("xgb", "xgboost"):
        candidates = ["xgb_model.pkl", "xgb.pkl", "xgboost.pkl", "xgb_model.joblib", "xgboost_advanced.pkl"]
    elif m in ("lgb", "lightgbm", "lgbm"):
        candidates = ["lgb_model.pkl", "lgb.pkl", "lightgbm_advanced.pkl", "lightgbm.pkl", "lgb_model.joblib"]
    else:
        candidates = [m + ext for ext in (".pkl", ".joblib")]

    # check MODEL_DIR
    for c in candidates:
        p = os.path.join(MODEL_DIR, c)
        if os.path.exists(p):
            return os.path.abspath(p)

    # fallback: find any pkl/joblib with model_choice in filename
    try:
        for f in os.listdir(MODEL_DIR):
            if f.lower().endswith((".pkl", ".joblib")) and m in f.lower():
                return os.path.join(MODEL_DIR, f)
    except FileNotFoundError:
        pass

    raise FileNotFoundError(f"No model bundle found for '{model_choice_or_path}' in {MODEL_DIR}. Tried: {candidates}")

class ModelWrapper:
    def __init__(self, path, verbose=False):
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        try:
            bundle = joblib.load(path)
        except Exception as e:
            raise RuntimeError(f"Failed to load model bundle '{path}': {e}")
        self.model = bundle.get("model") or bundle.get("estimator") or bundle.get("clf") or bundle.get("pipeline") or bundle.get("est")
        self.scaler = bundle.get("scaler")
        self.feature_cols = bundle.get("feature_cols") or bundle.get("feature_columns") or bundle.get("feature_columns_list")
        self.path = path
        self.verbose = verbose
        if self.model is None:
            raise ValueError("Loaded bundle doesn't contain 'model'.")
        if self.feature_cols is not None:
            # normalize to strings
            self.feature_cols = [str(c) for c in self.feature_cols]
        elif verbose:
            print("[ModelWrapper] WARNING: no feature_cols found in bundle; loader will rely on CSV keys or positional mapping.")

    def _safe_float(self, v):
        try:
            return float(v)
        except Exception:
            return 0.0

    def prepare_df(self, features: dict):
        """
        Return DataFrame (1 row) with columns ordered as model.feature_cols if available,
        else build from features dict.
        """
        if self.feature_cols:
            row = []
            for c in self.feature_cols:
                # prefer exact key, otherwise case-insensitive match
                if c in features:
                    v = features[c]
                else:
                    # try case-insensitive key match
                    v = None
                    for k in features:
                        if str(k).strip().lower() == str(c).strip().lower():
                            v = features[k]
                            break
                row.append(self._safe_float(v))
            df = pd.DataFrame([row], columns=self.feature_cols)
        else:
            # fallback: make df from features keys (attempt convert values to float)
            df = pd.DataFrame([{k: self._safe_float(v) for k, v in features.items()}])
        return df

    def predict(self, features: dict):
        X_df = self.prepare_df(features)
        # Apply scaler if present. Keep DataFrame columns to preserve feature names where possible.
        X_proc = None
        try:
            if self.scaler is not None:
                arr = self.scaler.transform(X_df)
                # convert to DataFrame if model expects column names
                try:
                    X_proc = pd.DataFrame(arr, columns=X_df.columns)
                except Exception:
                    X_proc = arr
            else:
                # pass DataFrame (some models like LGBM expect feature names)
                X_proc = X_df
        except Exception:
            # fallback: raw values
            X_proc = X_df.values

        # predict
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

def write_log_row(log_file, row: dict):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    df = pd.DataFrame([row])
    header = not os.path.exists(log_file)
    df.to_csv(log_file, mode="a", header=header, index=False, encoding="utf-8")

# Robust CSV loader for test mode
def load_features_from_csv(csv_path, model_feature_cols=None, verbose=False):
    """
    Returns list_of_feature_dicts.
    Handles:
      - CSV with 'features' JSON column
      - CSV with header (named columns)
      - Headerless positional CSV: map by model_feature_cols (if provided)
    """
    if verbose:
        print("[loader] reading CSV:", csv_path)
    try:
        df = pd.read_csv(csv_path, low_memory=False)
    except Exception:
        df = pd.read_csv(csv_path, low_memory=False, engine="python")

    # If there's a 'features' column with JSON strings -> parse
    if "features" in df.columns:
        out = []
        for v in df["features"].fillna("").astype(str):
            if v.strip() == "":
                out.append({})
                continue
            try:
                parsed = json.loads(v)
                if isinstance(parsed, dict):
                    out.append(parsed)
                    continue
            except Exception:
                pass
            # fallback attempts
            try:
                parsed = json.loads(v.replace("'", '"'))
                out.append(parsed if isinstance(parsed, dict) else {})
            except Exception:
                try:
                    import ast
                    parsed = ast.literal_eval(v)
                    out.append(parsed if isinstance(parsed, dict) else {})
                except Exception:
                    out.append({})
        if verbose:
            print(f"[loader] parsed {len(out)} 'features' rows")
        return out

    # If header contains alphabetic names -> treat header as feature names
    cols = df.columns.tolist()
    if any(any(ch.isalpha() for ch in str(c)) for c in cols):
        out = []
        for _, r in df.iterrows():
            out.append(r.dropna().to_dict())
        if verbose:
            print(f"[loader] header-based features used ({len(cols)} columns). Rows: {len(out)}")
        return out

    # Headerless numeric-like CSV -> map by model_feature_cols (if provided)
    raw = pd.read_csv(csv_path, header=None, low_memory=False)
    if model_feature_cols and raw.shape[1] == len(model_feature_cols):
        out = []
        for _, r in raw.iterrows():
            d = {model_feature_cols[i]: r.iat[i] for i in range(len(model_feature_cols))}
            out.append(d)
        if verbose:
            print("[loader] mapped headerless CSV to model_feature_cols (exact match)")
        return out
    if model_feature_cols and raw.shape[1] > len(model_feature_cols):
        # take last N columns (common if timestamp/index present first)
        start = raw.shape[1] - len(model_feature_cols)
        out = []
        for _, r in raw.iterrows():
            d = {model_feature_cols[i]: r.iat[start + i] for i in range(len(model_feature_cols))}
            out.append(d)
        if verbose:
            print("[loader] mapped last-N columns to model_feature_cols")
        return out

    # fallback: convert rows to dict using whatever header exists
    out = []
    for _, r in df.iterrows():
        out.append(r.dropna().to_dict())
    if verbose:
        print("[loader] fallback used; rows:", len(out))
    return out

def run_test_mode(wrapper: ModelWrapper, csv_path, threshold, log_file, verbose=False):
    feats = load_features_from_csv(csv_path, model_feature_cols=wrapper.feature_cols, verbose=verbose)
    print(f"Test mode: {len(feats)} rows from {csv_path}")
    for i, f in enumerate(feats):
        ts = pretty_ts()
        try:
            pred, prob = wrapper.predict(f)
            alert = 1 if (prob is not None and prob >= threshold) or (prob is None and pred == 1) else 0
            row = {
                "timestamp": ts,
                "row": i,
                "pred": int(pred),
                "prob": float(prob) if prob is not None else "",
                "alert": int(alert),
                "features": json.dumps(f, ensure_ascii=False)
            }
            if verbose:
                print(f"[{ts}] row={i} pred={pred} prob={prob} alert={alert}")
            write_log_row(log_file, row)
        except Exception as e:
            print(f"[{ts}] ERROR row {i}: {e}")

def run_live_mode(wrapper: ModelWrapper, extractor, threshold, log_file, iface=None, bpf=None, count=0, verbose=False):
    if not SCAPY:
        raise RuntimeError("Scapy not available for live mode. Run with --test_csv on this machine or install scapy.")
    print(f"Starting live capture (model={os.path.basename(wrapper.path)}) iface={iface or 'default'} filter={bpf or 'none'} threshold={threshold}")
    def on_packet(pkt):
        ts = pretty_ts()
        try:
            # basic network summary
            if IP in pkt:
                ip = pkt[IP]
                src = getattr(ip, "src", "") or ""
                dst = getattr(ip, "dst", "") or ""
                proto = "TCP" if TCP in pkt else "UDP" if UDP in pkt else "ICMP" if ICMP in pkt else str(getattr(ip, "proto", "IP"))
            else:
                src = dst = proto = ""
        except Exception:
            src = dst = proto = ""
        try:
            features = extractor.process_packet(pkt)
            if not features:
                return
        except Exception as e:
            if verbose:
                print(f"[{ts}] feature extraction error: {e}")
            return
        try:
            pred, prob = wrapper.predict(features)
            alert = 1 if (prob is not None and prob >= threshold) or (prob is None and pred == 1) else 0
            row = {
                "timestamp": ts,
                "src": src,
                "dst": dst,
                "proto": proto,
                "pred": int(pred),
                "prob": float(prob) if prob is not None else "",
                "alert": int(alert),
                "features": json.dumps(features, ensure_ascii=False)
            }
            dp = features.get("Destination Port", "")
            sp = features.get("Source Port", "")
            print(f"[{ts}] {proto} {src}:{sp} -> {dst}:{dp}  pred={pred} prob={prob} alert={alert}")
            write_log_row(log_file, row)
        except Exception as e:
            print(f"[{ts}] ERROR predicting: {e}")

    sniff(iface=iface, prn=on_packet, store=False, count=count, filter=bpf)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="rf", help="Model choice: rf|xgb|lgb or direct path to bundle")
    p.add_argument("--model-path", help="Alternate: explicit model bundle path (overrides --model)")
    p.add_argument("--threshold", type=float, default=0.5, help="Alert threshold on probability")
    p.add_argument("--test_csv", help="Run in test mode from CSV (no sniff).")
    p.add_argument("--log", default=os.path.join(ROOT, "logs", "realtime_predictions.csv"), help="CSV log file (append)")
    p.add_argument("--iface", help="Interface name for live sniffing")
    p.add_argument("--filter", dest="bpf", help="BPF filter e.g. 'tcp or udp'", default=None)
    p.add_argument("--count", type=int, default=0, help="Packet count for sniff (0 = infinite)")
    p.add_argument("--no_extractor", action="store_true", help="Skip importing feature_extractor for live mode (useful for test_csv)")
    p.add_argument("--verbose", action="store_true", help="Verbose output")
    args = p.parse_args()

    # determine model path
    model_path = None
    if args.model_path:
        model_path = args.model_path
    else:
        model_path = find_model_path(args.model)

    try:
        wrapper = ModelWrapper(model_path, verbose=args.verbose)
    except Exception as e:
        print("Failed to load model bundle:", e)
        sys.exit(1)

    if args.test_csv:
        run_test_mode(wrapper, args.test_csv, args.threshold, args.log, verbose=args.verbose)
        print("Test mode complete.")
        return

    # live mode requires feature_extractor
    if FeatureExtractor is None and not args.no_extractor:
        print("feature_extractor missing. Install or pass --no_extractor and use --test_csv instead.")
        sys.exit(1)

    extractor = None if args.no_extractor else FeatureExtractor()
    try:
        run_live_mode(wrapper, extractor, args.threshold, args.log, iface=args.iface, bpf=args.bpf, count=args.count, verbose=args.verbose)
    except KeyboardInterrupt:
        print("\nStopped by user (KeyboardInterrupt).")
    except Exception as e:
        print("Live mode error:", e)

if __name__ == "__main__":
    main()
