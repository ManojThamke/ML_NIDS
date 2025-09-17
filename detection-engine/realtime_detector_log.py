import os, sys, datetime, joblib
from scapy.all import sniff, IP, TCP, UDP, ICMP
import pandas as pd

# Local imports
HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from feature_extractor import FeatureExtractor

MODEL_PATH = os.path.join(HERE, "models", "realtime_rf.pkl")
LOG_PATH = os.path.join(HERE, "..", "logs", "realtime_predictions.csv")

def pretty_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Load model bundle
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Model not found!")
bundle = joblib.load(MODEL_PATH)
model = bundle.get("model")
scaler = bundle.get("scaler")   
feature_cols = bundle.get("feature_cols")
if model is None or feature_cols is None:
    raise ValueError("Model bundle missing required components!")

print("Model loaded. Features:", feature_cols)

# Prepare log file 
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
if not os.path.exists(LOG_PATH):
    with open(LOG_PATH, "w") as fh:
        fh.write("timestamp,src,dst,proto,dst_port,"+ "Destination Port,Flow Duration,Fwd Packet Length Min, Packet Length Std," + "pred_label,pred_prob\n")

# Extractor
extractor = FeatureExtractor()

def predict_from_features_dict(features: dict):
    # Build DataFrame row with coreect ordering and scale safely
    X_df = pd.DataFrame([[features[c] for c in feature_cols]], columns=feature_cols)
    for c in feature_cols:
        X_df[c] = pd.to_numeric(X_df[c], errors='coerce')
    X_df = X_df.fillna(0)
    if scaler is not None:
        X_scaled = X_df.values
    pred = int(model.predict(X_scaled)[0])
    prob = float(model.predict_proba(X_scaled)[0][1]) if hasattr(model, "predict_proba") else None
    return pred, prob

def on_packet(pkt):
    ts = pretty_time()

    # basic network fields
    if IP in pkt:
        ip = pkt[IP]
        src = getattr(ip, "src", "")
        dst = getattr(ip, "dst", "")
        proto = "TCP" if TCP in pkt else "UDP" if UDP in pkt else"ICMP" if ICMP in pkt else "IP"
        src_port = getattr(pkt[TCP], "sport", "") if TCP in pkt else getattr(pkt[UDP], "sport", "") if UDP in pkt else ""
        dst_port = getattr(pkt[TCP], "dport", "") if TCP in pkt else getattr(pkt[UDP], "dport", "") if UDP in pkt else ""
    else:
        return
    
    features = extractor.process_packet(pkt)
    if not features:
        return
    
    # Predict
    try:
        pred, prob = predict_from_features_dict(features)
    except Exception as e:
        print(f"[{ts}] Error in prediction: {e}")
        return
    
    label = "BENIGN" if pred == 0 else "ATTACK"
    prob_str = f"{prob:.4f}" if prob is not None else ""

    # print short
    print(f"[{ts}] {proto} {src}:{src_port} -> {dst}:{dst_port} => {label} ({prob_str})")

    # append to csv
    try:
        with open(LOG_PATH, "a") as fh:
            fh.write(f"{ts},{src},{dst},{proto},{src_port},{dst_port},"
                     f"{features['Destination Port']},{features['Flow Duration']:.6f},"
                     f"{features['Fwd Packet Length Min']},{features['Packet Length Std']:.6f},"
                     f"{pred},{prob_str}\n")
    except Exception as e:
        print(f"[{ts}] Error logging prediction: {e}")

def main(interface=None, count=0, bpf_filter=None):
    print("Starting realtime detector...")
    print("Log file:", LOG_PATH)
    try:
        sniff(iface=interface, prn=on_packet, store=False, count=count, filter=bpf_filter)
    except KeyboardInterrupt:
        print("\nStopped (CTRT+C)")
    except Exception as e:
        print(f"[{pretty_time()}] Sniffer error: {e}")

if __name__ == "__main__":
    main()