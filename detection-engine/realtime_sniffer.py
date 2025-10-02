# realtime_sniffer.py
"""
python detection-engine\simulate_attack.py udp_flood --target 127.0.0.1 --port 9999 --count 500 --rate 50 --payload 64
python detection-engine\realtime_sniffer.py --show-features --log-features logs/realtime_features.csv
"""
from scapy.all import sniff, IP, TCP, UDP, ICMP
import datetime
import argparse
import os
import sys

# allow running from project root or detection engine dir:
HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# local import (feature_extractor.py) - kept for --show-features and logging of fields
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

    #  Ensure all are strings
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

# Instance of FeatureExtractor (used for --show-features printing and logging)
extractor = FeatureExtractor()

def ensure_csv_header(path, header_line):
    """Create file and write header if file doesn't exist or is empty."""
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w") as fh:
            fh.write(header_line + "\n")

def safe_get_feature(features, key, fallback):
    """Return feature value or fallback. Also handle basic type conversions for formatting."""
    if not features or key not in features:
        return fallback
    return features.get(key, fallback)

def on_packet(pkt, show_features=False, log_features=None):
    try:
        # Always print the packet summary so you still see non-IP / Ether lines
        print(pkt_summary(pkt))

        # optional: show extracted feature dict
        features = None
        try:
            features = extractor.process_packet(pkt)
            if features and show_features:
                feat_str = ", ".join(f"{k}={v}" for k, v in features.items())
                print(f"   >> Features: {feat_str}")
        except Exception as e:
            # Non-fatal: printing feature extraction error but continue
            print(f"[{pretty_time()}] WARN extracting features for display: {e}")

        # LOGGING: only log when packet is TCP or UDP and when extractor returned features
        if log_features:
            if not (TCP in pkt or UDP in pkt):
                # skip non-TCP/UDP packets
                return

            # require features dict to extract the requested fields
            if not features:
                # attempt to extract once more but don't fail the whole app
                try:
                    features = extractor.process_packet(pkt)
                except Exception:
                    features = None

            # If still no features, write a fallback row with zeros/empties
            try:
                ts = pretty_time()

                # Fields you wanted: Destination Port, Flow Duration, Fwd Packet Length Min, Packet Length Std
                dest_port = safe_get_feature(features, "Destination Port", "")
                # Flow Duration and Packet Length Std likely floats; ensure numeric formatting
                flow_duration = safe_get_feature(features, "Flow Duration", 0.0)
                fwd_pkt_len_min = safe_get_feature(features, "Fwd Packet Length Min", 0)
                pkt_len_std = safe_get_feature(features, "Packet Length Std", 0.0)

                # Format values to match example: floats to 6 decimals, ints as-is, empty port as empty
                try:
                    flow_duration_s = f"{float(flow_duration):.6f}"
                except Exception:
                    flow_duration_s = f"{0.0:.6f}"

                try:
                    pkt_len_std_s = f"{float(pkt_len_std):.6f}"
                except Exception:
                    pkt_len_std_s = f"{0.0:.6f}"

                # fwd_pkt_len_min might be int-like
                try:
                    fwd_pkt_len_min_s = str(int(fwd_pkt_len_min))
                except Exception:
                    # keep as string fallback
                    fwd_pkt_len_min_s = str(fwd_pkt_len_min or "")

                dest_port_s = str(dest_port) if dest_port is not None else ""

                # Ensure dir + header
                ensure_csv_header(log_features, "timestamp,Destination Port,Flow Duration,Fwd Packet Length Min,Packet Length Std")

                # append row
                with open(log_features, "a") as fh:
                    fh.write(f"{ts},{dest_port_s},{flow_duration_s},{fwd_pkt_len_min_s},{pkt_len_std_s}\n")

            except Exception as e:
                print(f"[{pretty_time()}] ERROR writing log features: {e}")

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
    parser.add_argument("--show-features", action="store_true", help="Print extracted feature dict for each packet.")
    parser.add_argument("--log-features", help="Append selected extractor fields to CSV files (e.g., logs/realtime_features.csv)")
    args = parser.parse_args()
    main(interface=args.iface, count=args.count, bpf_filter=args.filter, show_features=args.show_features, log_features=args.log_features)
