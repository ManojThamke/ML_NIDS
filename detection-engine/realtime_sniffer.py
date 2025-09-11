from scapy.all import sniff, IP, TCP, UDP, ICMP
import datetime
import argparse

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
        proto = pkt.name
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

def on_packet(pkt):
    try:
        line = pkt_summary(pkt)
        print(line)
    except Exception as e:
        # keep sniffer resilent
        print(f"[{pretty_time()}] ERROR parsing packet: {e}")

def main(interface=None, count=0, bpf_filter=None):
    print("Starting sniffer...")
    print(f"interface: {interface or 'default'} Filter: {bpf_filter or 'none'}")
    print("Press Ctrl+C to stop. \n")
    try:
       sniff(iface=interface, prn=on_packet, store=False, count=count, filter=bpf_filter)
    except Exception as e:
        print(f"[{pretty_time()}] Sniffer error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple real-time packet sniffer (Scapy)")
    parser.add_argument("-i", "--iface", help="Interface name to sniff on (optonal).")
    parser.add_argument("-c", "--count", type=int, default=0, help="Number of packets to capture (0 = infinite)")
    parser.add_argument("-f", "--filter", help="BPF filter string.", default=None)
    args = parser.parse_args()
    main(interface=args.iface, count=args.count, bpf_filter=args.filter)