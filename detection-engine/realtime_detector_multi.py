#!/usr/bin/env python3
"""
Realtime detector (multi-model) - detection-engine/realtime_detector_multi.py

Features:
 - Load multiple model bundles (joblib .pkl/.joblib) by name or explicit paths
 - Each bundle expected keys: {"model": estimator, "scaler": scaler or None, "feature_cols": [...]}
 - Per-model smoothing (moving average), aggregation strategies: max|mean|weighted
 - Test mode (CSV) and live sniff mode (Scapy)
 - Friendly icon-based console prints + robust CSV parsing

 perfect command:
 python detection-engine\realtime_detector_multi.py --models rf,lgb,xgb,svm --agg mean --smooth 3 --threshold 0.5 --iface "Wi-Fi" --filter "tcp or udp" --log logs\realtime_ensemble_live.csv --verbose

 python detection-engine\realtime_detector_multi.py --models rf,lgb,xgb,svm,naive_bayes,knn,mlp --agg mean --smooth 3 --threshold 0.5 --iface "Wi-Fi" --filter "tcp or udp" --log logs\realtime_ensemble_live.csv --verbose

"""

import os
import sys
import argparse
import datetime
import json
import joblib
import pandas as pd
import math
from collections import deque
import signal

# ignore stdout encoding errors
sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
# Scapy optional for live mode
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    SCAPY = True
except Exception:
    SCAPY = False

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
MODEL_DIR = os.path.join(HERE, "models")

# local import for feature extraction (live mode)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    from feature_extractor import FeatureExtractor
except Exception:
    FeatureExtractor = None

# Graceful Shutdoun
RUNNING = True

def shutdown_handler(signum, frame):
    global RUNNING
    RUNNING = False
    emit_event("status", {"message": "Monitoring stopped"})


signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

# ---------- Utilities ----------
def now_ts():
    # return ISO-like timestamp for logs and prints
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

ICON_INFO = "[INFO]"
ICON_ALERT = "[ALERT]"
ICON_OK = "[OK]"
ICON_WARN = "[WARN]"
ICON_PACKET = "[PKT]"


# Backend-friendly JSON Event Emitter
def emit_event(event_type, payload):
    """
    Emits structured JSON events for backend/frontend
    """
    print(json.dumps({
        "event": event_type,
        "timestamp": now_ts(),
        "data": payload
    }), flush=True)

# ---------- Safe print ----------
def safe_print(msg):
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "ignore").decode(), flush=True)


# ---------- Model path finding ----------
def find_model_path(choice):
    # If path exists, return absolute
    if not choice:
        raise FileNotFoundError("Empty model choice")
    if os.path.exists(choice):
        return os.path.abspath(choice)
    m = choice.lower()
    candidates = []
    if m in ("rf", "realtime_rf", "realtime-rf"):
        candidates = ["realtime_rf.pkl", "realtime_rf.joblib", "realtime_rf.model"]
    elif m in ("xgb", "xgboost"):
        candidates = ["xgb_model.pkl", "xgb.pkl", "xgboost.pkl", "xgboost_advanced.pkl"]
    elif m in ("lgb", "lightgbm", "lgbm"):
        candidates = ["lgb_model.pkl", "lgb.pkl", "lightgbm_advanced.pkl", "lightgbm.pkl"]
    elif m in ("svm",):
        candidates = ["svm.pkl", "svm.joblib"]
    else:
        candidates = [choice + ext for ext in (".pkl", ".joblib")]

    for c in candidates:
        p = os.path.join(MODEL_DIR, c)
        if os.path.exists(p):
            return os.path.abspath(p)

    # fallback: any file containing model substring
    try:
        for f in os.listdir(MODEL_DIR):
            if f.lower().endswith((".pkl", ".joblib")) and m in f.lower():
                return os.path.join(MODEL_DIR, f)
    except FileNotFoundError:
        pass

    raise FileNotFoundError(f"No model bundle found for '{choice}' in {MODEL_DIR}. Tried: {candidates}")

# ---------- Model wrapper ----------
class ModelWrapper:
    def __init__(self, path, verbose=False):
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        try:
            bundle = joblib.load(path)
        except Exception as e:
            raise RuntimeError(f"Failed to load model bundle '{path}': {e}")
        # Accept different possible keys
        self.model = bundle.get("model") or bundle.get("estimator") or bundle.get("clf") or bundle.get("pipeline") or bundle.get("est")
        self.scaler = bundle.get("scaler")
        self.feature_cols = bundle.get("feature_cols") or bundle.get("feature_columns") or bundle.get("feature_columns_list")
        self.path = path
        self.verbose = verbose
        if self.model is None:
            raise ValueError("Loaded bundle does not contain a model estimator.")
        if self.feature_cols is not None:
            self.feature_cols = [str(c) for c in self.feature_cols]
        if self.verbose:
            print(f"{ICON_LOAD} Loaded: {os.path.basename(path)}  features: {len(self.feature_cols) if self.feature_cols else 'unknown'}")

    def _safe_float(self, v):
        try:
            return float(v)
        except Exception:
            return 0.0

    def prepare(self, features: dict):
        # Return DataFrame 1-row ordered to feature_cols if present
        if self.feature_cols:
            row = []
            for c in self.feature_cols:
                # prefer exact key; otherwise case-insensitive match
                if c in features:
                    v = features[c]
                else:
                    v = None
                    for k in features:
                        if str(k).strip().lower() == str(c).strip().lower():
                            v = features[k]
                            break
                row.append(self._safe_float(v))
            return pd.DataFrame([row], columns=self.feature_cols)
        else:
            return pd.DataFrame([{k: self._safe_float(v) for k, v in features.items()}])

    def predict(self, features: dict):
        X = self.prepare(features)
        # try scaler
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
            X_proc = X.values
        # predict and probability
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

# ---------- Smoothing buffer ----------
class SmoothBuf:
    def __init__(self, window=1):
        self.window = max(1, int(window))
        self.buf = deque(maxlen=self.window)
    def add(self, v):
        self.buf.append(float(v))
    def avg(self):
        if not self.buf:
            return 0.0
        return sum(self.buf) / len(self.buf)

# ---------- Logging ----------
def write_row(log_file, row: dict):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    df = pd.DataFrame([row])
    header = not os.path.exists(log_file)
    df.to_csv(log_file, mode="a", header=header, index=False, encoding="utf-8")

# ---------- CSV loader ----------
def load_features_for_model(csv_path, model_feature_cols=None, verbose=False):
    if verbose:
        print(f"{ICON_INFO} Reading CSV: {csv_path}")
    try:
        df = pd.read_csv(csv_path, low_memory=False)
    except Exception:
        df = pd.read_csv(csv_path, low_memory=False, engine="python")
    # case: 'features' JSON column
    if "features" in df.columns:
        out = []
        for v in df["features"].fillna("").astype(str):
            if v.strip() == "":
                out.append({})
                continue
            parsed = None
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
            print(f"{ICON_INFO} Parsed {len(out)} rows from 'features' column")
        return out
    # header has alphabetic names => header columns are features
    cols = df.columns.tolist()
    if any(any(ch.isalpha() for ch in str(c)) for c in cols):
        out = []
        for _, r in df.iterrows():
            out.append(r.dropna().to_dict())
        if verbose:
            print(f"{ICON_INFO} Using header columns as features ({len(cols)} cols). Rows: {len(out)}")
        return out
    # headerless numeric-like CSV -> try map by model_feature_cols
    raw = pd.read_csv(csv_path, header=None, low_memory=False)
    if model_feature_cols and raw.shape[1] == len(model_feature_cols):
        out = []
        for _, r in raw.iterrows():
            d = {model_feature_cols[i]: r.iat[i] for i in range(len(model_feature_cols))}
            out.append(d)
        if verbose:
            print(f"{ICON_INFO} Mapped headerless CSV to model_feature_cols (exact match).")
        return out
    if model_feature_cols and raw.shape[1] > len(model_feature_cols):
        start = raw.shape[1] - len(model_feature_cols)
        out = []
        for _, r in raw.iterrows():
            d = {model_feature_cols[i]: r.iat[start + i] for i in range(len(model_feature_cols))}
            out.append(d)
        if verbose:
            print(f"{ICON_INFO} Mapped last-N columns to model_feature_cols.")
        return out
    # fallback
    out = []
    for _, r in df.iterrows():
        out.append(r.dropna().to_dict())
    if verbose:
        print(f"{ICON_INFO} Fallback used; rows: {len(out)}")
    return out

# ---------- Aggregation ----------
def aggregate(per_model_probs, agg="max", weights=None):
    # per_model_probs: list of (name, prob) where prob may be None
    probs = [0.0 if p is None else float(p) for _, p in per_model_probs]
    if not probs:
        return 0.0
    if agg == "max":
        return max(probs)
    if agg == "mean":
        return sum(probs) / len(probs)
    if agg == "weighted":
        if not weights or len(weights) != len(probs):
            return sum(probs) / len(probs)
        w = [float(x) for x in weights]
        s = sum(w)
        if s == 0:
            return sum(probs) / len(probs)
        return sum(p * (wi / s) for p, wi in zip(probs, w))
    return max(probs)

# ---------- Test mode: multi-model ----------
def run_test_mode(wrappers, csv_path, threshold, log_file, smoothers, agg, weights, verbose=False):
    feats = load_features_for_model(csv_path, model_feature_cols=wrappers[0][1].feature_cols if wrappers and wrappers[0][1].feature_cols else None, verbose=verbose)
    print(f"{ICON_INFO} Test mode: {len(feats)} rows from {csv_path}")
    for i, f in enumerate(feats):
        ts = now_ts()
        per_model = []
        try:
            for name, wrap in wrappers:
                try:
                    pred, prob = wrap.predict(f)
                except Exception as e:
                    pred, prob = 0, None
                # update smoother
                smoothers[name].add(0.0 if prob is None else prob)
                per_model.append((name, smoothers[name].avg()))
            agg_prob = aggregate(per_model, agg=agg, weights=weights)
            alert = 1 if agg_prob >= threshold else 0
            row = {
                "timestamp": ts,
                "row": i,
                "agg_prob": float(round(agg_prob, 6)),
                "alert": int(alert),
                "per_model": json.dumps({n: round(s, 6) for n, s in per_model}, ensure_ascii=False),
                "features": json.dumps(f, ensure_ascii=False)
            }
            if verbose:
                print(f"[{ts}] row={i} agg={agg_prob:.6f} alert={alert} per_model={ {n: round(s,6) for n,s in per_model} }")
            write_row(log_file, row)
        except Exception as e:
            print(f"[{ts}] ERROR row {i}: {e}")

# ---------- Live mode: multi-model ----------
def run_live_mode(wrappers, extractor, threshold, log_file, smoothers,
                  agg, weights, run_mode,
                  iface=None, bpf=None, count=0, verbose=False):

    if not SCAPY:
        raise RuntimeError("Scapy not available for live mode.")

    names = [n for n, _ in wrappers]

    emit_event("status", {
        "message": "Monitoring started",
        "models": names,
        "threshold": threshold
    })

    print(f"{ICON_INFO} Starting live capture (models={','.join(names)}) "
          f"iface={iface or 'default'} filter={bpf or 'none'} threshold={threshold}")

    def on_packet(pkt):
        if not RUNNING:
            return

        ts = now_ts()

        try:
            if IP in pkt:
                ip = pkt[IP]
                src = getattr(ip, "src", "")
                dst = getattr(ip, "dst", "")
                proto = (
                    "TCP" if TCP in pkt else
                    "UDP" if UDP in pkt else
                    "ICMP" if ICMP in pkt else "IP"
                )
            else:
                return
        except Exception:
            return

        try:
            features = extractor.process_packet(pkt)
            if not features:
                return
        except Exception as e:
            if verbose:
                print(f"{ICON_WARN} [{ts}] feature extraction error: {e}")
            return

        per_model = []
        for name, wrap in wrappers:
            try:
                _, prob = wrap.predict(features)
            except Exception:
                prob = None

            smoothers[name].add(0.0 if prob is None else prob)
            per_model.append((name, smoothers[name].avg()))

        agg_prob = aggregate(per_model, agg=agg, weights=weights)
        alert = 1 if agg_prob >= threshold else 0

        event_payload = {
            "src": src,
            "dst": dst,
            "proto": proto,
            "agg_prob": round(agg_prob, 6),
            "alert": alert,
            "per_model": {n: round(p, 6) for n, p in per_model}
        }

        if run_mode == "service":
            emit_event("prediction", {
                "src": src,
                "dst": dst,
                "proto": proto,
                "agg_prob": round(agg_prob, 6),
                "alert": alert,
                "per_model": {n: round(p,6) for n,p in per_model}
            })
        else:
            status_icon = ICON_ALERT if alert else ICON_OK
            print(f"[{ts}] {ICON_PACKET} {proto} {src} -> {dst} "
                  f"agg_prob={agg_prob:.6f} alert={alert} {status_icon}")

        write_row(log_file, {
            "timestamp": ts,
            "src": src,
            "dst": dst,
            "proto": proto,
            "agg_prob": round(agg_prob, 6),
            "alert": alert,
            "per_model": json.dumps(event_payload["per_model"]),
            "features": json.dumps(features)
        })

    sniff(
        iface=iface,
        prn=on_packet,
        store=False,
        count=count,
        filter=bpf,
        stop_filter=lambda _: not RUNNING
    )



# ---------- Load multiple wrappers ----------
def load_wrappers(models_csv, model_paths_csv=None, verbose=False):
    models = [m.strip() for m in models_csv.split(",") if m.strip()]
    explicit_paths = None
    if model_paths_csv:
        explicit_paths = [p.strip() for p in model_paths_csv.split(",") if p.strip()]
        if len(explicit_paths) != len(models):
            raise ValueError("--model-paths must match --models count")
    wrappers = []
    for i, m in enumerate(models):
        if explicit_paths:
            p = explicit_paths[i]
        else:
            p = find_model_path(m)
        if verbose:
            print(f"{ICON_LOAD} Loading model '{m}' -> {p}")
        wrappers.append((m, ModelWrapper(p, verbose=verbose)))
    return wrappers

# ---------- Main ----------
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--models", default="rf", help="Comma list e.g. 'lgb,rf,xgb,svm' or single model name")
    p.add_argument("--model-paths", help="Optional comma-separated explicit paths (must match models count)")
    p.add_argument("--agg", choices=["max","mean","weighted"], default="max", help="Aggregation mode")
    p.add_argument("--weights", help="Comma weights for weighted aggregation (matches models order)")
    p.add_argument("--smooth", type=int, default=1, help="Smoothing window (moving average) over last N probs")
    p.add_argument("--threshold", type=float, default=0.5, help="Alert threshold on aggregated probability")
    p.add_argument("--test_csv", help="Run test mode from CSV (no sniff)")
    p.add_argument("--log", default=os.path.join(ROOT, "logs", "realtime_predictions_ensemble.csv"), help="CSV log file to append")
    p.add_argument("--iface", help="Interface name for sniff (e.g. 'Wi-Fi')")
    p.add_argument("--filter", dest="bpf", help="BPF filter string (e.g. 'tcp or udp')", default=None)
    p.add_argument("--count", type=int, default=0, help="Packet count for sniff (0=infinite)")
    p.add_argument("--no_extractor", action="store_true", help="Skip importing feature_extractor for live mode (useful for test_csv)")
    p.add_argument("--verbose", action="store_true", help="Verbose output")
    p.add_argument("--run_mode",choices=["cli", "service"],default="cli",help="cli = terminal mode, service = backend controlled mode")

    args = p.parse_args()

    try:
        wrappers = load_wrappers(args.models, args.model_paths, verbose=args.verbose)
    except Exception as e:
        print(f"{ICON_WARN} Model load error: {e}")
        sys.exit(1)

    # prepare smoothers
    smoothers = {name: SmoothBuf(args.smooth) for name,_ in wrappers}

    # parse weights
    weights = None
    if args.weights:
        weights = [float(x) for x in args.weights.split(",")]

    # run test mode if requested
    if args.test_csv:
        print(f"{ICON_INFO} Test CSV mode -> {args.test_csv}")
        run_test_mode(wrappers, args.test_csv, args.threshold, args.log, smoothers, args.agg, weights, verbose=args.verbose)
        print(f"{ICON_OK} Test mode done.")
        return

    # live mode: need feature_extractor unless user explicitly skips
    if FeatureExtractor is None and not args.no_extractor:
        print(f"{ICON_WARN} feature_extractor not found — cannot run live mode. Use --no_extractor with --test_csv or provide feature_extractor.py")
        sys.exit(1)
    extractor = None if args.no_extractor else FeatureExtractor()

    # run live
    try:
        run_live_mode(
            wrappers,
            extractor,
            args.threshold,
            args.log,
            smoothers,
            args.agg,
            weights,
            args.run_mode,          # ✅ PASS IT HERE
            iface=args.iface,
            bpf=args.bpf,
            count=args.count,
            verbose=args.verbose
        )

    except KeyboardInterrupt:
        print(f"\n{ICON_INFO} Stopped by user (KeyboardInterrupt).")
    except Exception as e:
        print(f"{ICON_WARN} Live mode error: {e}")

if __name__ == "__main__":
    main()
