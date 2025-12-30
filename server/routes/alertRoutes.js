const express = require("express");
const router = express.Router();
const {
  createAlert,
  getAlerts,
  getAlertStats,
  getLogs,
  exportLogs,
  getLogsInsights,
  getTrafficTimeline,
  getTopAttackedDestinations,
} = require("../controllers/alertController");

router.post("/", createAlert);

// Dashboard routes
router.get("/", getAlerts);
router.get("/stats", getAlertStats);

// Logs routes
router.get("/logs", getLogs);
router.get("/export", exportLogs);
router.get("/logs/insights", getLogsInsights);
router.get("/logs/timeline", getTrafficTimeline);
router.get("/logs/top-destinations", getTopAttackedDestinations);


module.exports = router;
