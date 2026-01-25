# tools/sniff_one.py
from scapy.all import sniff, hexdump, IP, TCP, UDP
def pr(pkt):
    if IP in pkt:
        print(pkt.summary())
    else:
        print("NON-IP", pkt.summary())
sniff(count=100, prn=pr)

# python .\detection-engine\realtime_detector_multi.py --models lgb,rf,svm \ --model-paths "detection-engine\models\lightgbm_advanced.pkl,detection-engine\models\realtime_rf.pkl,detection-engine\models\svm.pkl" \ --iface "Wi-Fi" --filter "tcp or udp" --threshold 0.3 --log logs\realtime_predictions_ensemble.csv --verbose