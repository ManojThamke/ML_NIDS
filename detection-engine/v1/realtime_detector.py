import os, sys, datetime, joblib
from scapy.all import sniff, IP, TCP, UDP, ICMP
import pandas as pd

# Local imports
HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from feature_extractor import FeatureExtractor

MODEL_PATH = os.path.join(HERE, "models", "realtime_rf.pkl")

def pretty_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Load model
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Model not found!")

bundle = joblib.load(MODEL_PATH)
model = bundle.get("model")
scaler = bundle.get("scaler")
feature_cols = bundle.get("feature_cols")

if model is None or feature_cols is None:
    raise ValueError("Model file missing required fields.")

print(f"Model loaded. Feature used: {feature_cols}")

# Create extractor
extractor = FeatureExtractor()

def predict_from_features(features: dict):
    """Return model prediction + probability"""
    try:
        X_df = pd.DataFrame([[features[c] for c in feature_cols]], columns=feature_cols)
    except KeyError as e:
        raise KeyError(f"Missing feature key: {e}. Available keys: {list(features.keys())}")
    
    # handles NaNs safetly
    for c in feature_cols:
        X_df[c] = pd.to_numeric(X_df[c], errors="coerce")
    if X_df.isna().any(axis=None):
        X_df = X_df.fillna(0)

    # pass Dataframe or ndarray directly
    if scaler is not None:
        X_scaled = scaler.transform(X_df)
    else:
        X_scaled = X_df.values

    pred = int(model.predict(X_scaled)[0])
    prob = float(model.predict_proba(X_scaled)[0][1]) if hasattr(model, "predict_proba") else None
    return pred, prob

def on_packet(pkt):
    ts = pretty_time()

    # Basec packet summary
    if IP in pkt:
        ip = pkt[IP]
        src = ip.src
        dst = ip.dst
        sport = pkt[TCP].sport if TCP in pkt else pkt[UDP].sport if UDP in pkt else ""
        dport = pkt[TCP].dport if TCP in pkt else pkt[UDP].dport if UDP in pkt else ""
        proto = "TCP" if TCP in pkt else "UDP" if UDP in pkt else "ICMP" if ICMP in pkt else "IP"

        print(f"[{ts}] {proto} {src}:{sport} -> {src}:{dport}")
    
    else:
        return # Skip non-ip packets
    
    # Extract features
    features = extractor.process_packet(pkt)
    if not features:
        return
    
    # Predict
    try:
        pred, prob = predict_from_features(features)
        label = "BENIGN ✅" if pred == 0 else "ATTACK 🚨"
        prob_str = f"{prob:.2f}" if prob is not None else ""

        print(f"    >>Features: {features}")
        print(f"    >>Prediction: {label} (prob={prob_str})")

    except Exception as e:
        print(f"[{ts}] ERROR Predicting: {e}")

def main(interface=None, count=0, bpf_filter=None):
    print("Starting Real-Time Detector...")
    print(f"interface: {interface or 'default'} | Filter: {bpf_filter or 'none'}")

    try:
        sniff(iface=interface, prn=on_packet, store=False, count=count, filter=bpf_filter)
    except KeyboardInterrupt:
        print("\n For Stopping detector press CTRL+C")
    except Exception as e:
        print(f"[{pretty_time()}] Sniffer error: {e}")

if __name__ == "__main__":
    main()