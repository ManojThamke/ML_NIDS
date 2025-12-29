const { spawn } = require("child_process");
const path = require("path");
const Alert = require("../models/Alert");

let monitorProcess = null;

const detectorPath = path.join(
  __dirname,
  "..",
  "..",
  "detection-engine",
  "realtime_detector_multi.py"
);

const projectRoot = path.join(__dirname, "..", "..");

const startMonitoring = (req, res) => {
  if (monitorProcess) {
    return res.status(400).json({ message: "Monitoring already running" });
  }

  monitorProcess = spawn(
    "python",
    [
      detectorPath,
      "--models", "rf,lgb,xgb,svm,knn,mlp,naive_bayes",
      "--agg", "mean",
      "--smooth", "3",
      "--threshold", "0.4",
      "--iface", "Wi-Fi",
      "--filter", "tcp or udp",
      "--log", "logs/realtime_ensemble_live.csv",
      "--run_mode", "service"
    ],
    {
      cwd: projectRoot,
      shell: false
    }
  );

  monitorProcess.stdout.on("data", async (data) => {
    const text = data.toString().trim();
    console.log(text);

    try {
      const parsed = JSON.parse(text);

      if (parsed.event === "prediction") {
        const d = parsed.data;

        await Alert.create({
          timestamp: parsed.timestamp,
          sourceIP: d.src,
          destinationIP: d.dst,
          modelUsed: "ENSEMBLE",
          probability: d.agg_prob,
          finalLabel: d.alert === 1 ? "ATTACK" : "BENIGN",
        });
      }
    } catch (err) {}
  });

  monitorProcess.stderr.on("data", (data) => {
    console.error("❌", data.toString());
  });

  monitorProcess.on("close", () => {
    monitorProcess = null;
    console.log("🛑 Monitoring stopped");
  });

  res.json({ message: "Monitoring started" });
};

const stopMonitoring = (req, res) => {
  if (!monitorProcess) {
    return res.status(400).json({ message: "Monitoring not running" });
  }

  monitorProcess.kill("SIGINT");
  monitorProcess = null;

  res.json({ message: "Monitoring stopped" });
};

const getStatus = (req, res) => {
  res.json({ running: Boolean(monitorProcess) });
};

module.exports = {
  startMonitoring,
  stopMonitoring,
  getStatus,
};
