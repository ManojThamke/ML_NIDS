import platform
import time

# ===============================
# ALERT CONFIG
# ===============================

# Cooldown to avoid alert spam (seconds)
ALERT_COOLDOWN = 10
_last_alert_time = 0


def _beep():
    """
    ONE long loud alert beep (Level 2 - simple & strong)
    """

    system = platform.system()

    if system == "Windows":
        try:
            import winsound

            # 🔊 Single long high-frequency beep
            winsound.Beep(3500, 1500)  # frequency (Hz), duration (ms)

        except Exception:
            print("\a")

    else:
        # Linux / Mac fallback
        print("\a")
        time.sleep(0.5)
        print("\a")



def trigger_alert(payload: dict):
    """
    Trigger alert ONLY for HIGH severity ATTACKS
    """

    global _last_alert_time

    hybrid_label = payload.get("hybridLabel")
    severity = payload.get("severity")

    # 🚫 Safety check (VERY IMPORTANT)
    if hybrid_label != "ATTACK" or severity != "HIGH":
        return

    now = time.time()

    # 🚫 Cooldown check
    if now - _last_alert_time < ALERT_COOLDOWN:
        return

    _last_alert_time = now

    # ===============================
    # ALERT OUTPUT
    # ===============================

    print("\n🚨🚨🚨 HIGH SEVERITY ATTACK DETECTED 🚨🚨🚨")
    print(f"Source IP      : {payload.get('sourceIP')}")
    print(f"Destination IP : {payload.get('destinationIP')}")
    print(f"Destination Port : {payload.get('dstPort')}")
    print(f"Confidence     : {round(payload.get('confidence', 0), 4)}")
    print(f"Attack Votes   : {payload.get('attackVotes')}")
    print("🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨")

    # 🔊 LOUD ALERT
    _beep()
