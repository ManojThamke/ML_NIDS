#!/usr/bin/env python3
"""
realtime_detector_thresh.py  — Day 31

Features:
 - Load model bundle saved via joblib.dump({"model":..., "scaler":..., "feature_cols":[...]})
 - Accepts --model (rf|xgb|lgb or direct basename) or --model-path
 - Test mode (CSV of features) or live sniff mode (requires feature_extractor + scapy)
 - Accepts multiple thresholds (comma separated), e.g. --thresholds 0.5,0.7,0.9
 - Writes CSV log rows and an optional markdown report summarizing detection rates per threshold
 - Friendly console output with icons

Usage (test CSV):
  python detection-engine\realtime_detector_thresh.py --model rf \ --test_csv logs/realtime_features.csv \ --thresholds 0.5,0.7,0.9 \ --log logs/realtime_thresh_rf.csv \   --report-out docs/week5/day31_rf_thresh.md --verbose
    python detection\realtime_detector_thresh.py --model rf \ --iface "Wi-Fi" --filter "tcp or udp" \ --thresholds 0.5,0.7,0.9 \ --log logs\realtime_thresh_live_rf.csv \ --report-out docs\week5\day31_rf_live.md \ --verbose

Usage (live sniff):
  python detection-engine\realtime_detector_thresh.py --model lgb \
    --iface "Wi-Fi" --filter "tcp or udp" \
    --thresholds 0.5,0.7,0.9 --log logs/realtime_thresh_live_lgb.csv --verbose
"""

import os
import sys
import argparse
import datetime
import json
import joblib
import math

import pandas as pd

# optional scapy import (only required for live sniff)
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    SCAPY = True
except Exception:
    SCAPY = False

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
MODEL_DIR = os.path.join(HERE, "models")

# feature_extractor optional (required for live sniff)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    from feature_extractor import FeatureExtractor
except Exception:
    FeatureExtractor = None

# ---------- helpers ----------
def pretty_ts():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def now_iso():
    return datetime.datetime.now().isoformat()

def find_model_path(model_choice, explicit_path=None):
    if explicit_path:
        if os.path.exists(explicit_path):
            return explicit_path
        raise FileNotFoundError(f"Model path not found: {explicit_path}")

    m = model_choice.lower()
    candidates = []
    if m in ("rf", "realtime_rf", "realtime-rf"):
        candidates = ["realtime_rf.pkl", "realtime_rf.joblib", "realtime_rf.model", "realtime-rf.pkl"]
    elif m in ("xgb", "xgboost"):
        candidates = ["xgb_model.pkl", "xgb.pkl", "xgboost.pkl", "xgb_model.joblib", "xgboost_advanced.pkl"]
    elif m in ("lgb", "lightgbm", "lgbm", "lightgbm_advanced"):
        candidates = ["lgb_model.pkl", "lgb.pkl", "lightgbm_advanced.pkl", "lightgbm.pkl", "lgb_model.joblib"]
    else:
        candidates = [model_choice + ext for ext in (".pkl", ".joblib")]

    for c in candidates:
        p = os.path.join(MODEL_DIR, c)
        if os.path.exists(p):
            return p

    # fallback: any pkl/joblib containing the name
    try:
        for f in os.listdir(MODEL_DIR):
            if f.lower().endswith((".pkl", ".joblib")) and model_choice.lower() in f.lower():
                return os.path.join(MODEL_DIR, f)
    except FileNotFoundError:
        pass

    raise FileNotFoundError(f"No model bundle found for choice '{model_choice}' in {MODEL_DIR}. Tried: {candidates}")

class ModelWrapper:
    """Load model bundle, prepare rows in correct feature order, predict + proba."""
    def __init__(self, path, verbose=False):
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        self.verbose = verbose
        try:
            bundle = joblib.load(path)
        except Exception as e:
            raise RuntimeError(f"Failed to load model bundle '{path}': {e}")
        # accept several key names
        self.model = bundle.get("model") or bundle.get("estimator") or bundle.get("clf") or bundle.get("pipeline") or bundle.get("est")
        self.scaler = bundle.get("scaler")
        self.feature_cols = bundle.get("feature_cols") or bundle.get("feature_columns") or bundle.get("feature_columns_list")
        self.path = path
        if self.model is None:
            raise ValueError("Model bundle doesn't contain a 'model' object.")
        if self.feature_cols is not None:
            self.feature_cols = [str(c) for c in self.feature_cols]
        if self.verbose:
            print(f"ℹ️  Loaded model: {os.path.basename(path)}  features: {len(self.feature_cols) if self.feature_cols else 'unknown'}")

    def _safe_float(self, v):
        try:
            return float(v)
        except Exception:
            return 0.0

    def prepare(self, features: dict):
        """Return DataFrame with single row in feature order model expects (if available)."""
        if self.feature_cols:
            row = []
            for c in self.feature_cols:
                # try direct key, otherwise case-insensitive match
                if c in features:
                    v = features[c]
                else:
                    # try to find matching key ignoring whitespace/case
                    v = None
                    for k in features:
                        if str(k).strip().lower() == str(c).strip().lower():
                            v = features[k]
                            break
                row.append(self._safe_float(v) if v is not None else 0.0)
            df = pd.DataFrame([row], columns=self.feature_cols)
        else:
            df = pd.DataFrame([{k: self._safe_float(v) for k, v in features.items()}])
        return df

    def predict_with_proba(self, features: dict):
        """Return (pred, prob) where prob is probability of positive class or None if not available."""
        X = self.prepare(features)
        # apply scaler if present, try to preserve DataFrame column names for models that expect them
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

# ---------- logging helpers ----------
def write_log_row(log_file, row: dict):
    os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
    df = pd.DataFrame([row])
    header = not os.path.exists(log_file)
    df.to_csv(log_file, mode="a", header=header, index=False, encoding="utf-8")

# ---------- CSV loader for test mode ----------
def load_features_from_csv(csv_path, model_feature_cols=None, verbose=False):
    """
    Return list of feature dicts. Handles:
      - CSV containing a 'features' JSON column
      - CSV with header columns -> each row becomes dict
      - Headerless / malformed -> map columns by position to model_feature_cols if provided
    """
    if verbose:
        print(f"🔎 Loading CSV: {csv_path}")
    try:
        df = pd.read_csv(csv_path, low_memory=False)
    except Exception:
        df = pd.read_csv(csv_path, low_memory=False, engine="python")

    # Case A: features JSON
    if "features" in df.columns:
        out = []
        for v in df["features"].fillna("").astype(str):
            if v.strip() == "":
                out.append({})
                continue
            parsed = {}
            try:
                parsed = json.loads(v)
            except Exception:
                try:
                    parsed = json.loads(v.replace("'", '"'))
                except Exception:
                    try:
                        import ast
                        parsed = ast.literal_eval(v)
                    except Exception:
                        parsed = {}
            out.append(parsed if isinstance(parsed, dict) else {})
        if verbose:
            print(f"📂 Parsed {len(out)} rows from features column")
        return out

    # Case B: header present (alphabetic column names)
    cols = df.columns.tolist()
    if any(any(ch.isalpha() for ch in str(c)) for c in cols):
        out = [row.dropna().to_dict() for _, row in df.iterrows()]
        if verbose:
            print(f"📂 Using header columns as features ({len(cols)} columns). Rows: {len(out)}")
        return out

    # Case C: headerless / numeric header -> map by position if model_feature_cols given
    raw = pd.read_csv(csv_path, header=None, low_memory=False)
    if model_feature_cols and raw.shape[1] == len(model_feature_cols):
        out = []
        for _, r in raw.iterrows():
            out.append({model_feature_cols[i]: r.iat[i] for i in range(len(model_feature_cols))})
        if verbose:
            print(f"📂 Mapped headerless CSV to model_feature_cols. Rows: {len(out)}")
        return out

    if model_feature_cols and raw.shape[1] > len(model_feature_cols):
        start = raw.shape[1] - len(model_feature_cols)
        out = []
        for _, r in raw.iterrows():
            out.append({model_feature_cols[i]: r.iat[start + i] for i in range(len(model_feature_cols))})
        if verbose:
            print(f"📂 Mapped last-N columns to model_feature_cols. Rows: {len(out)}")
        return out

    # fallback
    out = [row.dropna().to_dict() for _, row in df.iterrows()]
    if verbose:
        print(f"📂 Fallback loaded rows: {len(out)}")
    return out

# ---------- run modes ----------
def run_test_mode(wrapper: ModelWrapper, csv_path, thresholds, log_file, report_out=None, verbose=False):
    feats = load_features_from_csv(csv_path, model_feature_cols=wrapper.feature_cols, verbose=verbose)
    n = len(feats)
    print(f"🔎 Test mode — rows: {n}  CSV: {csv_path}")
    # counters per threshold
    counters = {t: {"alerts": 0, "rows": 0} for t in thresholds}

    for i, f in enumerate(feats):
        ts = now_iso()
        try:
            pred, prob = wrapper.predict_with_proba(f)
            # for display and logging, show prob as float or empty
            prob_val = prob if prob is not None else ""
            # evaluate each threshold
            for t in thresholds:
                alert = 1 if (prob is not None and prob >= t) else 0
                counters[t]["alerts"] += alert
            # increment rows
            for t in thresholds:
                counters[t]["rows"] += 1
            # write a single canonical row including all thresholds? We'll include prob only and later compute report.
            row = {
                "timestamp": ts,
                "row": i,
                "pred": int(pred),
                "prob": prob_val,
                "features": json.dumps(f, ensure_ascii=False)
            }
            if verbose:
                print(f"🕒 [{pretty_ts()}] row={i} pred={pred} prob={prob_val}  keys={list(f.keys())[:6]}")
            write_log_row(log_file, row)
        except Exception as e:
            print(f"⚠️ [{pretty_ts()}] ERROR row {i}: {e}")

    # produce summary report if asked
    if report_out:
        os.makedirs(os.path.dirname(report_out), exist_ok=True)
        with open(report_out, "w", encoding="utf-8") as fh:
            fh.write(f"# Day 31 — Threshold Report\n\n")
            fh.write(f"CSV tested: `{csv_path}`\n")
            fh.write(f"Rows processed: {n}\n\n")
            fh.write("## Threshold summary\n\n")
            fh.write("| threshold | alerts | alert_rate |\n")
            fh.write("|---:|---:|---:|\n")
            for t in thresholds:
                rows = counters[t]["rows"]
                alerts = counters[t]["alerts"]
                rate = alerts / rows if rows else 0.0
                fh.write(f"| {t:.2f} | {alerts} | {rate:.6f} |\n")
        print(f"📄 Test summary saved: {report_out}")

    print("✅ Test mode complete.")

def run_live_mode(wrapper: ModelWrapper, extractor, thresholds, log_file, iface=None, bpf=None, count=0, report_out=None, verbose=False):
    if not SCAPY:
        raise RuntimeError("Scapy not available — install scapy to use live sniff mode.")
    if extractor is None:
        raise RuntimeError("FeatureExtractor not provided for live mode.")

    print(f"🚀 Starting live capture  iface={iface or 'default'}  filter={bpf or 'none'}  thresholds={thresholds}")
    # counters for report (running)
    counters = {t: {"alerts": 0, "rows": 0} for t in thresholds}

    def on_packet(pkt):
        ts = now_iso()
        # basic src/dst/proto
        try:
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
                print(f"⚠️ [{pretty_ts()}] feature extraction error: {e}")
            return

        try:
            pred, prob = wrapper.predict_with_proba(features)
            prob_val = prob if prob is not None else ""
            # update counters
            for t in thresholds:
                alert = 1 if (prob is not None and prob >= t) else 0
                counters[t]["alerts"] += alert
                counters[t]["rows"] += 1
            # write
            row = {
                "timestamp": ts,
                "src": src,
                "dst": dst,
                "proto": proto,
                "pred": int(pred),
                "prob": prob_val,
                "features": json.dumps(features, ensure_ascii=False)
            }
            dp = features.get("Destination Port", "")
            sp = features.get("Source Port", "")
            print(f"[{pretty_ts()}] {proto} {src}:{sp} -> {dst}:{dp}  pred={pred} prob={prob_val} alerts={ {round(t,2): counters[t]['alerts'] for t in thresholds} }")
            write_log_row(log_file, row)
        except Exception as e:
            print(f"⚠️ [{pretty_ts()}] ERROR predicting: {e}")

    try:
        sniff(iface=iface, prn=on_packet, store=False, count=count, filter=bpf)
    except KeyboardInterrupt:
        print("\n⛔ Live capture interrupted by user (KeyboardInterrupt).")
    finally:
        # on exit, optionally write a small summary report
        if report_out:
            os.makedirs(os.path.dirname(report_out), exist_ok=True)
            with open(report_out, "w", encoding="utf-8") as fh:
                fh.write(f"# Day 31 — Live Threshold Report\n\n")
                fh.write(f"Interface: {iface or 'default'}  Filter: {bpf or 'none'}\n")
                fh.write(f"Model: {os.path.basename(wrapper.path)}\n")
                fh.write(f"Capture stopped: {now_iso()}\n\n")
                fh.write("## Threshold summary\n\n")
                fh.write("| threshold | alerts | rows | alert_rate |\n")
                fh.write("|---:|---:|---:|---:|\n")
                for t in thresholds:
                    rows = counters[t]["rows"]
                    alerts = counters[t]["alerts"]
                    rate = alerts / rows if rows else 0.0
                    fh.write(f"| {t:.2f} | {alerts} | {rows} | {rate:.6f} |\n")
            print(f"📄 Live report saved: {report_out}")

# ---------- CLI ----------
def parse_thresholds(s: str):
    parts = [p.strip() for p in s.split(",") if p.strip() != ""]
    out = []
    for p in parts:
        try:
            v = float(p)
            if v < 0 or v > 1:
                raise ValueError()
            out.append(v)
        except Exception:
            raise argparse.ArgumentTypeError(f"Invalid threshold value: {p}. Must be between 0 and 1.")
    return out

def main():
    p = argparse.ArgumentParser(description="Realtime detector with multi-threshold probability logging")
    p.add_argument("--model", default="rf", help="Model choice (rf|xgb|lgb) or basename. Use --model-path to give full path.")
    p.add_argument("--model-path", help="Direct path to model bundle (.pkl/.joblib) overrides --model")
    p.add_argument("--thresholds", default="0.5", help="Comma-separated thresholds, e.g. 0.5,0.7,0.9")
    p.add_argument("--test_csv", help="Run in test mode using a CSV of features (no live sniffing).")
    p.add_argument("--log", default=os.path.join(ROOT, "logs", "realtime_thresh_predictions.csv"), help="CSV file to write predictions")
    p.add_argument("--report-out", help="Optional markdown report file to save summary")
    p.add_argument("--iface", help="Interface for live sniffing (requires scapy and feature_extractor)")
    p.add_argument("--filter", dest="bpf", help="BPF filter for sniff (e.g. 'tcp or udp')", default=None)
    p.add_argument("--count", type=int, default=0, help="Packet count for sniff (0 = infinite)")
    p.add_argument("--no_extractor", action="store_true", help="Skip importing feature_extractor (only valid for test_csv)")
    p.add_argument("--verbose", action="store_true", help="Verbose output")
    args = p.parse_args()

    # parse thresholds
    try:
        thresholds = parse_thresholds(args.thresholds)
    except Exception as e:
        print(f"⚠️ Invalid thresholds: {e}")
        sys.exit(1)

    # model selection
    try:
        model_path = args.model_path if args.model_path else find_model_path(args.model, None)
    except Exception as e:
        print(f"❌ Model selection error: {e}")
        sys.exit(1)

    # load model wrapper
    try:
        wrapper = ModelWrapper(model_path, verbose=args.verbose)
    except Exception as e:
        print(f"❌ Failed to load model bundle: {e}")
        sys.exit(1)

    print(f"🔌 Loaded model: {os.path.basename(wrapper.path)}")
    print(f"📝 Logging to: {os.path.abspath(args.log)}")
    print(f"🔎 Running TEST CSV mode: {args.test_csv}" if args.test_csv else f"🔎 Running LIVE mode (iface={args.iface})")
    print(f"🔎 Thresholds: {thresholds}")

    # Test CSV mode
    if args.test_csv:
        run_test_mode(wrapper, args.test_csv, thresholds, args.log, report_out=args.report_out, verbose=args.verbose)
        return

    # Live mode: require extractor unless --no_extractor
    if FeatureExtractor is None and not args.no_extractor:
        print("❌ feature_extractor not found — cannot run live mode. Use --no_extractor only with --test_csv.")
        sys.exit(1)

    extractor = None if args.no_extractor else FeatureExtractor()
    try:
        run_live_mode(wrapper, extractor, thresholds, args.log, iface=args.iface, bpf=args.bpf, count=args.count, report_out=args.report_out, verbose=args.verbose)
    except Exception as e:
        print(f"❌ Live mode error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
