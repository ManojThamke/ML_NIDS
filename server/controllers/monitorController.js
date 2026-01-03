const { spawn } = require("child_process");
const path = require("path");
const Alert = require("../models/Alert");
const Settings = require("../models/Settings");

let monitorProcess = null;

const detectorPath = path.join(
  __dirname,
  "..",
  "..",
  "detection-engine",
  "realtime_detector_multi.py"
);

const projectRoot = path.join(__dirname, "..", "..");

const startMonitoring = async (req, res) => {
  if (monitorProcess) {
    return res.status(400).json({ message: "Monitoring already running" });
  }

  const settings = await Settings.findOne().sort({ updatedAt: -1 });

  if (!settings) {
    return res.status(400).json({
      message: "No detection settings found. Please configure settings first.",
    });
  }

  console.log("🚀 Starting detector with settings:", settings);

  /* ================= BUILD ARGUMENTS ================= */
  const args = [
    detectorPath,
    "--models", settings.models.join(","),
    "--agg", settings.aggregation,
    "--smooth", String(settings.smoothing),
    "--threshold", String(settings.threshold),
    "--log", "logs/realtime_ensemble_live.csv",
    "--run_mode", "service",
  ];

  // ✅ ONLY add iface if real value exists
  if (settings.interface && settings.interface.trim() !== "") {
    args.push("--iface", settings.interface);
  }

  console.log("🐍 Python args:", args);

  monitorProcess = spawn("python", args, {
    cwd: projectRoot,
    shell: false,
  });

  monitorProcess.stdout.on("data", async (data) => {
    const text = data.toString().trim();
    console.log(text);
  });

  monitorProcess.stderr.on("data", (data) => {
    console.error("❌ Detector error:", data.toString());
  });

  monitorProcess.on("close", (code) => {
    console.log("🛑 Monitoring stopped. Exit code:", code);
    monitorProcess = null;
  });

  res.json({ message: "Monitoring started with saved settings" });
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
