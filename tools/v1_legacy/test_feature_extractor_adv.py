# tools/test_feature_extractor_adv.py

import sys, os, pprint, traceback
from scapy.all import sniff

# -------------------------------------------
# FIX IMPORT for folder with hyphen: detection-engine
# -------------------------------------------

# Project root directory (ML_NIDS/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Add detection-engine folder manually (because '-' breaks module import)
DETECTION_ENGINE_PATH = os.path.join(PROJECT_ROOT, "detection-engine")
sys.path.append(DETECTION_ENGINE_PATH)

# Import the extractor directly from the file
from feature_extractor_adv import FeatureExtractorAdv

# -------------------------------------------
# TEST EXTRACTOR
# -------------------------------------------

fe = FeatureExtractorAdv()

def on_packet(pkt):
    try:
        feats = fe.process(pkt)
        if not feats:
            return  # ignore packets without features

        print("\n================ FEATURE SAMPLE ================")

        # Print ALL 26 features sorted alphabetically
        for k in sorted(feats.keys()):
            print(f"{k:30}: {feats[k]}")

    except Exception as e:
        print("❌ Error processing packet:", e)
        traceback.print_exc()

if __name__ == "__main__":
    # Update iface as required for your system
    IFACE = "Wi-Fi"   # or "Ethernet", "wlan0", etc.

    print(f"[*] Starting Phase-2 Extractor Test on interface: {IFACE}")
    print("[*] Sniffing... press Ctrl+C to stop.\n")

    sniff(prn=on_packet, store=False, filter="tcp or udp", iface=IFACE)
