#!/usr/bin/env python3
"""
Day 31 — realtime_detector_thresh.py with reporting

# Run as Administrator for Windows live sniffing
python detection-engine\realtime_detector_thresh.py --model rf --iface "Wi-Fi" --filter "tcp or udp" --thresholds 0.5,0.7,0.9 --log logs\realtime_predictions_live_rf_thresh.csv --report-out docs\week5\day31_rf_threshold_live_report.md
python detection-engine\realtime_detector_thresh.py --model xgb --iface "Wi-Fi" --filter "tcp or udp" --thresholds 0.5,0.7,0.9 --log logs\realtime_predictions_live_xgb_thresh.csv --report-out docs\week5\day31_xgb_threshold_live_report.md
python detection-engine\realtime_detector_thresh.py --model lgb --iface "Wi-Fi" --filter "tcp or udp" --thresholds 0.5,0.7,0.9 --log logs\realtime_predictions_live_lgb_thresh.csv --report-out docs\week5\day31_lgb_threshold_live_report.md
# Press Ctrl+C when done — the report will be written automatically.


Features:
 - Load model bundles (rf/xgb/lgb or explicit --model-path).
 - Compute probabilities with model.predict_proba (or decision_function->sigmoid).
 - Evaluate multiple thresholds (default: 0.5,0.7,0.9).
 - Print per-packet row and save CSV rows.
 - Optionally create a Markdown report summary (--report-out) after run or on Ctrl+C.
 python detection-engine\realtime_detector_thresh.py --model lgb --test_csv logs\realtime_features.csv --thresholds 0.5,0.7,0.9 --log logs\realtime_predictions_thresh_lgb.csv --report-out docs\week5\day31_lgb_threshold_report.md
 python detection-engine\realtime_detector_thresh.py --model xgb --test_csv logs\realtime_features.csv --thresholds 0.5,0.7,0.9 --log logs\realtime_predictions_thresh_xgb.csv --report-out docs\week5\day31_xgb_threshold_report.md
 python detection-engine\realtime_detector_thresh.py --model rf --test_csv logs\realtime_features.csv --thresholds 0.5,0.7,0.9 --log logs\realtime_predictions_thresh_rf.csv --report-out docs\week5\day31_rf_threshold_report.md
"""
import os
import sys
import argparse
import datetime
import json
import joblib
import math
import pandas as pd
from collections import Counter

# optional scapy
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    SCAPY = True
except Exception:
    SCAPY = False

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
MODEL_DIR = os.path.join(HERE, "models")

# feature extractor for live mode
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    from feature_extractor import FeatureExtractor
except Exception:
    FeatureExtractor = None

def pretty_ts():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------------- model discovery / wrapper ----------------
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

    try:
        for f in os.listdir(MODEL_DIR):
            if f.lower().endswith((".pkl", ".joblib")) and model_choice.lower() in f.lower():
                return os.path.join(MODEL_DIR, f)
    except FileNotFoundError:
        pass

    raise FileNotFoundError(f"No model bundle found for choice '{model_choice}' in {MODEL_DIR}. Tried: {candidates}")

class ModelWrapper:
    def __init__(self, path, verbose=False):
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        try:
            bundle = joblib.load(path)
        except Exception as e:
            raise RuntimeError(f"Failed to load model bundle '{path}': {e}")

        self.model = bundle.get("model") or bundle.get("estimator") or bundle.get("clf") or bundle.get("pipeline")
        self.scaler = bundle.get("scaler")
        self.feature_cols = bundle.get("feature_cols") or bundle.get("feature_columns") or bundle.get("feature_columns_list")
        self.path = path
        self.verbose = verbose

        if self.model is None:
            raise ValueError("Loaded bundle does not contain a 'model' object.")
        if self.feature_cols is not None:
            self.feature_cols = [str(c) for c in self.feature_cols]
        if self.verbose:
            print(f"[ModelWrapper] loaded {os.path.basename(path)} features={len(self.feature_cols) if self.feature_cols else 'unknown'}")

    def _safe_float(self, v):
        try:
            return float(v)
        except Exception:
            return 0.0

    def prepare(self, features: dict):
        if self.feature_cols:
            row = []
            for c in self.feature_cols:
                v = features.get(c, None)
                if v is None:
                    # case-insensitive key match
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
        X = self.prepare(features)
        X_proc = None
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

        try:
            pred = int(self.model.predict(X_proc)[0])
        except Exception as e:
            raise RuntimeError(f"Model predict failed: {e}")

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

# ---------------- logging & CSV loader ----------------
def write_row(log_file, row: dict):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    df = pd.DataFrame([row])
    header = not os.path.exists(log_file)
    df.to_csv(log_file, mode="a", header=header, index=False, encoding="utf-8")

def load_features_for_model(csv_path, model_feature_cols=None, verbose=False):
    try:
        df = pd.read_csv(csv_path, low_memory=False)
    except Exception:
        df = pd.read_csv(csv_path, low_memory=False, engine="python")

    if "features" in df.columns:
        out = []
        for v in df["features"].fillna("").astype(str):
            if not v.strip():
                out.append({})
                continue
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
        return out

    cols = df.columns.tolist()
    if any(any(ch.isalpha() for ch in str(c)) for c in cols):
        return [r.dropna().to_dict() for _, r in df.iterrows()]

    raw = pd.read_csv(csv_path, header=None, low_memory=False)
    if model_feature_cols and raw.shape[1] == len(model_feature_cols):
        out = []
        for _, r in raw.iterrows():
            d = {model_feature_cols[i]: r.iat[i] for i in range(len(model_feature_cols))}
            out.append(d)
        return out

    if model_feature_cols and raw.shape[1] > len(model_feature_cols):
        start = raw.shape[1] - len(model_feature_cols)
        out = []
        for _, r in raw.iterrows():
            d = {model_feature_cols[i]: r.iat[start + i] for i in range(len(model_feature_cols))}
            out.append(d)
        return out

    return [r.dropna().to_dict() for _, r in df.iterrows()]

# ---------------- report generator ----------------
def summarize_log_csv(log_file, thresholds, md_out=None):
    if not os.path.exists(log_file):
        print(f"[Report] log file not found: {log_file}")
        return None
    df = pd.read_csv(log_file, low_memory=False)
    total = len(df)
    out = {
        "log_file": log_file,
        "total_rows": total,
        "thresholds": {},
    }
    for t in thresholds:
        key = f"alert_{t:.2f}"
        if key in df.columns:
            cnt = int(df[key].sum())
        else:
            # try computing from 'prob' column
            if "prob" in df.columns:
                cnt = int((df["prob"].fillna(0).astype(float) >= t).sum())
            else:
                cnt = 0
        rate = cnt / total if total > 0 else 0.0
        out["thresholds"][f"{t:.2f}"] = {"alerts": cnt, "rate": rate}

    # top destination ports for alerted rows (best-effort)
    dest_col_candidates = ["Destination Port", "dst_port", "dst", "dport", "dst_port:"]  # flexible
    top_ports = Counter()
    if "features" in df.columns:
        for v in df["features"].dropna().astype(str):
            try:
                parsed = json.loads(v)
            except Exception:
                try:
                    parsed = json.loads(v.replace("'", '"'))
                except Exception:
                    parsed = {}
            if not isinstance(parsed, dict):
                continue
            # look for common keys
            for k in ("Destination Port", "Dest Port", "dport", "dst_port", "dst"):
                if k in parsed:
                    try:
                        top_ports[int(parsed[k])]
                    except Exception:
                        pass
            # fallback: if numeric keys exist, attempt to find a likely port (53,443, etc)
            for kk, vv in parsed.items():
                try:
                    ival = int(float(vv))
                    if 0 <= ival <= 65535:
                        top_ports[ival] += 1
                except Exception:
                    continue
    top = top_ports.most_common(10)

    out["top_ports_alerts"] = top
    # write markdown if requested
    if md_out:
        os.makedirs(os.path.dirname(md_out), exist_ok=True)
        with open(md_out, "w", encoding="utf-8") as fh:
            fh.write(f"# Realtime Predictions Summary\n\n")
            fh.write(f"- Log file: `{log_file}`\n")
            fh.write(f"- Generated: {pretty_ts()}\n\n")
            fh.write(f"## Totals\n\n- Rows: {total}\n\n")
            fh.write("## Alerts by threshold\n\n")
            fh.write("| threshold | alerts | alert_rate |\n")
            fh.write("|---:|---:|---:|\n")
            for thr, info in out["thresholds"].items():
                fh.write(f"| {thr} | {info['alerts']} | {info['rate']:.6f} |\n")
            fh.write("\n## Top destination ports seen in features (best-effort)\n\n")
            if top:
                fh.write("| port | count |\n|---:|---:|\n")
                for p, c in top:
                    fh.write(f"| {p} | {c} |\n")
            else:
                fh.write("No port info parsed from features.\n")
        print(f"[Report] Markdown summary written to: {md_out}")
    return out

# ---------------- modes ----------------
def run_test_mode(wrapper: ModelWrapper, csv_path, thresholds, log_file, report_out=None, verbose=False):
    feats = load_features_for_model(csv_path, model_feature_cols=wrapper.feature_cols, verbose=verbose)
    print(f"[Test] rows loaded: {len(feats)} from {csv_path}")
    for i, f in enumerate(feats):
        ts = pretty_ts()
        try:
            pred, prob = wrapper.predict_with_proba(f)
            row = {
                "timestamp": ts,
                "row": i,
                "pred": int(pred),
                "prob": float(prob) if prob is not None else ""
            }
            for t in thresholds:
                key = f"alert_{t:.2f}"
                row[key] = int(1 if (prob is not None and prob >= t) else 0)
            row["features"] = json.dumps(f, ensure_ascii=False)
            if verbose:
                print(f"[{ts}] row={i} pred={pred} prob={prob} " + " ".join([f"{t:.2f}:{row[f'alert_{t:.2f}']}" for t in thresholds]))
            write_row(log_file, row)
        except Exception as e:
            print(f"[{ts}] ERROR row {i}: {e}")

    if report_out:
        summarize_log_csv(log_file, thresholds, md_out=report_out)
        print("[Test] report written.")

def run_live_mode(wrapper: ModelWrapper, extractor, thresholds, log_file, report_out=None, iface=None, bpf=None, count=0, verbose=False):
    if not SCAPY:
        raise RuntimeError("Scapy not available for live mode. Install scapy to run live capture.")
    print(f"[Live] model={os.path.basename(wrapper.path)} iface={iface or 'default'} filter={bpf or 'none'} thresholds={[f'{t:.2f}' for t in thresholds]}")
    def on_packet(pkt):
        ts = pretty_ts()
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
                print(f"[{ts}] feature extraction error: {e}")
            return

        try:
            pred, prob = wrapper.predict_with_proba(features)
            row = {
                "timestamp": ts,
                "src": src,
                "dst": dst,
                "proto": proto,
                "pred": int(pred),
                "prob": float(prob) if prob is not None else ""
            }
            for t in thresholds:
                key = f"alert_{t:.2f}"
                row[key] = int(1 if (prob is not None and prob >= t) else 0)
            row["features"] = json.dumps(features, ensure_ascii=False)
            dp = features.get("Destination Port", "")
            sp = features.get("Source Port", "")
            print(f"[{ts}] {proto} {src}:{sp} -> {dst}:{dp}  pred={pred} prob={prob} " + " ".join([f"{t:.2f}:{row[f'alert_{t:.2f}']}" for t in thresholds]))
            write_row(log_file, row)
        except Exception as e:
            print(f"[{ts}] ERROR predicting: {e}")

    try:
        sniff(iface=iface, prn=on_packet, store=False, count=count, filter=bpf)
    except KeyboardInterrupt:
        print("\n[Live] stopped by user (KeyboardInterrupt).")
        if report_out:
            summarize_log_csv(log_file, thresholds, md_out=report_out)
            print("[Live] report written on stop.")
    except Exception as e:
        print("[Live] sniff error:", e)
        if report_out:
            summarize_log_csv(log_file, thresholds, md_out=report_out)
            print("[Live] report written on error.")

# ---------------- CLI ----------------
def parse_thresholds(s: str):
    parts = [p.strip() for p in s.split(",") if p.strip()]
    vals = []
    for p in parts:
        try:
            v = float(p)
            if v < 0 or v > 1:
                raise ValueError
            vals.append(round(v, 2))
        except Exception:
            raise argparse.ArgumentTypeError(f"Invalid threshold value: {p}")
    return sorted(set(vals))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="rf", help="Model choice: rf|xgb|lgb or a custom basename. Alternatively use --model-path")
    p.add_argument("--model-path", help="Direct path to model bundle (.pkl/.joblib) overrides --model")
    p.add_argument("--thresholds", default="0.5,0.7,0.9", help="Comma-separated thresholds (0.0-1.0). Example: 0.5,0.7,0.9")
    p.add_argument("--test_csv", help="Run in test mode using features CSV (no sniff).")
    p.add_argument("--log", default=os.path.join(ROOT, "logs", "realtime_predictions_thresh.csv"), help="CSV log file to append predictions")
    p.add_argument("--report-out", help="Optional markdown report output (writes at end of test mode or on Ctrl+C for live mode)")
    p.add_argument("--iface", help="Interface name for live sniffing (optional)")
    p.add_argument("--filter", dest="bpf", help="BPF filter string for sniff (e.g. 'tcp or udp')", default=None)
    p.add_argument("--count", type=int, default=0, help="Packet count (0 = infinite)")
    p.add_argument("--no_extractor", action="store_true", help="Skip importing feature_extractor for live mode (useful for test_csv only)")
    p.add_argument("--verbose", action="store_true", help="Verbose output")
    args = p.parse_args()

    try:
        thresholds = parse_thresholds(args.thresholds)
    except Exception as e:
        print("Invalid thresholds:", e)
        sys.exit(1)

    try:
        model_path = find_model_path(args.model, args.model_path)
    except Exception as e:
        print("Model selection error:", e)
        sys.exit(1)

    try:
        wrapper = ModelWrapper(model_path, verbose=args.verbose)
    except Exception as e:
        print("Failed to create model wrapper:", e)
        sys.exit(1)

    if args.test_csv:
        run_test_mode(wrapper, args.test_csv, thresholds, args.log, report_out=args.report_out, verbose=args.verbose)
        print("[Test] finished.")
        return

    if FeatureExtractor is None and not args.no_extractor:
        print("feature_extractor not found — cannot run live mode. Use --no_extractor for test csv only.")
        sys.exit(1)

    extractor = None if args.no_extractor else FeatureExtractor()
    run_live_mode(wrapper, extractor, thresholds, args.log, report_out=args.report_out, iface=args.iface, bpf=args.bpf, count=args.count, verbose=args.verbose)

if __name__ == "__main__":
    main()
