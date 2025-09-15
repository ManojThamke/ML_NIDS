from scapy.all import sniff, IP, TCP, UDP, ICMP
import datetime
import argparse
import os
import sys

# allow running from project root or detection engine dir:
HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# local import (feature_extractor.py)
from feature_extractor import FeatureExtractor

def pretty_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def pkt_summary(pkt):
    ts = pretty_time()

    proto = ""
    sport = ""
    dport = ""
    src = ""
    dst = ""

    if IP in pkt:
        ip = pkt[IP]
        src = ip.src or ""
        dst = ip.dst or ""

        if TCP in pkt:
            proto = "TCP"
            sport = getattr(pkt[TCP], 'sport', "") or ""
            dport = getattr(pkt[TCP], 'dport', "") or ""
        elif UDP in pkt:
            proto = "UDP"
            sport = getattr(pkt[UDP], 'sport', "") or ""
            dport = getattr(pkt[UDP], 'dport', "") or ""
        elif ICMP in pkt:
            proto = "ICMP"
        else:
            proto = str(getattr(ip, 'proto', "")) or ""
    else:
        proto = getattr(pkt, "name", "NON-IP")
        src = getattr(pkt, 'src', "") or ""
        dst = getattr(pkt, 'dst', "") or ""

    #  Ensure all re strings
    proto_s = str(proto)
    sport_s = str(sport)
    dport_s = str(dport)
    src_s = str(src)
    dst_s = str(dst)

    # Align/protect fields using ljust
    proto_field = proto_s.ljust(5)[:5]
    src_field = src_s
    dst_field = dst_s

    # Build a compact printable line
    line = f"[{ts}] {proto_field} {src_field}:{sport_s} -> {dst_field}:{dport_s}"
    return line

# Instance of FeatureExtractor
extractor = FeatureExtractor()

def on_packet(pkt, show_features=False, log_features=None):
    try:
       print(pkt_summary(pkt))

    # Extract features
       try:
           features = extractor.process_packet(pkt)
           if features and show_features:
               feat_str = ", ".join(f"{k}={v}" for k, v in features.items())
               print(f"   >> Features: {feat_str}")
            
            # optionally append to a csv-like files for later analysis
           if features and log_features:
               ts = pretty_time()
               #ensure directory exists
               os.makedirs(os.path.dirname(log_features), exist_ok=True)
               with open(log_features, "a") as fh:
                   fh.write(f"{ts},{features['Destination Port']},{features['Flow Duration']:.6f},"
                             f"{features['Fwd Packet Length Min']},{features['Packet Length Std']:.6f}\n")
       except Exception as e:
           print(f"[{pretty_time()}] ERROR extracting features: {e}")

    except Exception as e:
       print(f"[{pretty_time()}] ERROR processing packet: {e}")

def main(interface=None, count=0, bpf_filter=None, show_features=True, log_features=None):
    print("Starting sniffer...")
    print(f"interface: {interface or 'default'} Filter: {bpf_filter or 'none'} Show-features: {show_features}")
    print("Press Ctrl+C to stop. \n")
    try:
        sniff(iface=interface,
              prn=lambda pkt: on_packet(pkt, show_features=show_features, log_features=log_features),
              store=False,
              count=count,
              filter=bpf_filter)
    except KeyboardInterrupt:
        print("\nStopping sniffing (KeyboardInterrupt).")
    except Exception as e:
        print(f"[{pretty_time()}] ERROR in sniffing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-time Network Sniffer with Feature Extraction")
    parser.add_argument("-i", "--iface", help="Interface name to sniff on.")
    parser.add_argument("-c", "--count", type=int, default=0, help="Number of packets to capture (0 = infinite).")
    parser.add_argument("-f", "--filter", help="BPF filter string (e.g., 'tcp or udp').", default=None)
    parser.add_argument("--show-features", action="store_true", help="Print extracted feature dict for each packet. ")
    parser.add_argument("--log-features", help="Append extractor features to CSV files (e.g., logs/realtime_features.csv)")
    args = parser.parse_args()
    main(interface=args.iface, count=args.count, bpf_filter=args.filter, show_features=args.show_features, log_features=args.log_features)
