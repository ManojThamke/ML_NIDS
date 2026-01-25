const express = require("express");
const router = express.Router();

const {
  createAlert,
  getAlerts,
  getAlertStats,
  getLogs,
  exportLogs,
  getLogsInsights,
  getAlertTimeline,
  getAlertTopDestinations,
} = require("../controllers/alertController");

router.post("/", createAlert);
router.get("/", getAlerts);
router.get("/stats", getAlertStats);

router.get("/logs", getLogs);
router.get("/export", exportLogs);

router.get("/logs/insights", getLogsInsights);
router.get("/logs/timeline", getAlertTimeline);
router.get("/logs/top-destinations", getAlertTopDestinations);

module.exports = router;
