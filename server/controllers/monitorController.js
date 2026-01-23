const { spawn } = require("child_process");
const path = require("path");
const Settings = require("../models/Settings");

let monitorProcess = null;

/* ======================================================
   PATH CONFIG
====================================================== */

const detectorPath = path.join(
  __dirname,
  "..",
  "..",
  "detection-engine",
  "realtime_v2",
  "detector_live_capture_v2.py"
);

const projectRoot = path.join(__dirname, "..", "..");

/* ======================================================
   START MONITORING (PHASE-2 SERVICE MODE)
====================================================== */

const startMonitoring = async (req, res) => {
  try {
    if (monitorProcess) {
      return res.status(400).json({
        message: "Monitoring already running",
      });
    }

    const settings = await Settings.findOne().sort({ updatedAt: -1 });

    if (!settings) {
      return res.status(400).json({
        message: "No detection settings found. Configure settings first.",
      });
    }

    /* ================= VALIDATION ================= */

    if (!settings.interface || settings.interface.trim() === "") {
      return res.status(400).json({
        message: "Network interface (iface) is required",
      });
    }

    console.log("🚀 Starting Phase-2 Detector (SERVICE MODE)");
    console.log(settings);

    /* ================= BUILD ARGUMENTS ================= */

    const args = [
      detectorPath,

      // 🔴 REQUIRED on Windows / hotspot
      "--iface",
      settings.interface,

      // Models
      "--models",
      settings.models?.length ? settings.models.join(",") : "all",

      // Voting logic
      "--threshold",
      String(settings.threshold ?? 0.5),

      "--vote",
      String(settings.voteK ?? 3),

      // Flow expiry
      "--timeout",
      String(settings.flowTimeout ?? 10),

      // 🔑 IMPORTANT
      "--run_mode",
      "service"
    ];

    console.log("🐍 Python command:");
    console.log("python", args.join(" "));

    /* ================= SPAWN PYTHON ================= */

    monitorProcess = spawn("python", args, {
      cwd: projectRoot,
      shell: false,
    });

    monitorProcess.stdout.on("data", (data) => {
      console.log("📡 DETECTOR:", data.toString().trim());
    });

    monitorProcess.stderr.on("data", (data) => {
      console.error("❌ DETECTOR ERROR:", data.toString());
    });

    monitorProcess.on("close", (code) => {
      console.log("🛑 Detector stopped. Exit code:", code);
      monitorProcess = null;
    });

    return res.json({
      message: "Phase-2 monitoring started (service mode)",
    });

  } catch (err) {
    console.error("❌ Monitor start failed:", err);
    res.status(500).json({ error: err.message });
  }
};

/* ======================================================
   STOP MONITORING
====================================================== */

const stopMonitoring = (req, res) => {
  if (!monitorProcess) {
    return res.status(400).json({
      message: "Monitoring is not running",
    });
  }

  monitorProcess.kill("SIGINT");
  monitorProcess = null;

  res.json({
    message: "Monitoring stopped",
  });
};

/* ======================================================
   STATUS
====================================================== */

const getStatus = (req, res) => {
  res.json({
    running: Boolean(monitorProcess),
  });
};

module.exports = {
  startMonitoring,
  stopMonitoring,
  getStatus,
};
