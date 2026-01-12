import os
import shutil
from datetime import datetime

# ===============================
# PATH CONFIG
# ===============================

LOG_DIR = "logs"
EXPORT_DIR = "exports"

SOURCE_LOG = os.path.join(LOG_DIR, "realtime_v2_log.csv")

# Ensure export directory exists
os.makedirs(EXPORT_DIR, exist_ok=True)

# Timestamped export file (NEVER overwrite)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
EXPORT_FILE = os.path.join(
    EXPORT_DIR,
    f"experiment_export_{timestamp}.csv"
)

# ===============================
# EXPORT LOGIC
# ===============================

def export_logs():
    if not os.path.exists(SOURCE_LOG):
        print("❌ No log file found to export.")
        return

    # COPY log file (do NOT modify original)
    shutil.copy2(SOURCE_LOG, EXPORT_FILE)

    print("✅ Logs exported successfully!")
    print(f"📄 Source : {SOURCE_LOG}")
    print(f"📦 Export : {EXPORT_FILE}")
    print("ℹ️ Original log file remains unchanged (append-based logging).")


if __name__ == "__main__":
    export_logs()
