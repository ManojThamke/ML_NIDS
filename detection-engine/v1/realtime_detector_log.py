import os, sys, datetime, joblib, argparse
from scapy.all import sniff, IP, TCP, UDP, ICMP
import pandas as pd

HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from feature_extractor import FeatureExtractor

MODEL_PATH = os.path.join(HERE, "models", "realtime_rf.pkl")
LOG_PATH   = os.path.abspath(os.path.join(HERE, "..", "logs", "realtime_predictions.csv"))

def pretty_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# CLI
parser = argparse.ArgumentParser()
parser.add_argument("--prob-threshold", type=float, default=None,
                    help="If set, final_label = 1 when pred_prob >= prob_threshold. If omitted, use model label.")
parser.add_argument("-i","--iface", default=None)
parser.add_argument("-c","--count", type=int, default=0)
parser.add_argument("-f","--filter", default=None)
args = parser.parse_args()

# Load model
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Model not found! Train model first.")
bundle = joblib.load(MODEL_PATH)
model = bundle.get("model")
scaler = bundle.get("scaler")
feature_cols = bundle.get("feature_cols")
if model is None or feature_cols is None:
    raise ValueError("Model bundle missing fields.")

print("Model loaded. Features:", feature_cols)
print("Logging predictions to:", LOG_PATH)
print("Using prob-threshold:", args.prob_threshold)

# prepare log file header
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
if not os.path.exists(LOG_PATH):
    with open(LOG_PATH, "w") as fh:
        fh.write("timestamp,src,dst,proto,src_port,dst_port,")
        fh.write("Destination Port,Flow Duration,Fwd Packet Length Min,Packet Length Std,")
        fh.write("pred_label,pred_prob,final_label\n")

extractor = FeatureExtractor()

def predict_from_features_dict(features: dict):
    X_df = pd.DataFrame([[features[c] for c in feature_cols]], columns=feature_cols)
    for c in feature_cols:
        X_df[c] = pd.to_numeric(X_df[c], errors="coerce")
    X_df = X_df.fillna(0)
    if scaler is not None:
        X_scaled = scaler.transform(X_df)
    else:
        X_scaled = X_df.values
    pred = int(model.predict(X_scaled)[0])
    prob = float(model.predict_proba(X_scaled)[0][1]) if hasattr(model, "predict_proba") else None
    return pred, prob

def on_packet(pkt):
    ts = pretty_time()
    if IP in pkt:
        ip = pkt[IP]
        src = getattr(ip, "src","")
        dst = getattr(ip, "dst","")
        proto = "TCP" if TCP in pkt else "UDP" if UDP in pkt else "ICMP" if ICMP in pkt else "IP"
        src_port = getattr(pkt[TCP],"sport","") if TCP in pkt else getattr(pkt[UDP],"sport","") if UDP in pkt else ""
        dst_port = getattr(pkt[TCP],"dport","") if TCP in pkt else getattr(pkt[UDP],"dport","") if UDP in pkt else ""
    else:
        return

    features = extractor.process_packet(pkt)
    if not features:
        return

    try:
        pred, prob = predict_from_features_dict(features)
    except Exception as e:
        print(f"[{ts}] ERROR predicting: {e}")
        return

    # apply threshold if provided
    if prob is not None and args.prob_threshold is not None:
        final_label = 1 if prob >= args.prob_threshold else 0
    else:
        final_label = pred

    label_str = "ATTACK" if final_label==1 else "BENIGN"
    prob_str = f"{prob:.4f}" if prob is not None else ""

    print(f"[{ts}] {proto} {src}:{src_port} -> {dst}:{dst_port}  => {label_str} (prob={prob_str})")

    # append CSV line
    try:
        with open(LOG_PATH, "a") as fh:
            fh.write(f"{ts},{src},{dst},{proto},{src_port},{dst_port},"
                     f"{features['Destination Port']},{features['Flow Duration']:.6f},"
                     f"{features['Fwd Packet Length Min']},{features['Packet Length Std']:.6f},"
                     f"{pred},{prob_str},{final_label}\n")
    except Exception as e:
        print(f"[{ts}] ERROR logging: {e}")

def main():
    try:
        sniff(iface=args.iface, prn=on_packet, store=False, count=args.count, filter=args.filter)
    except KeyboardInterrupt:
        print("\nStopped (Ctrl+C).")
    except Exception as e:
        print(f"[{pretty_time()}] Sniffer error: {e}")

if __name__ == "__main__":
    main()
