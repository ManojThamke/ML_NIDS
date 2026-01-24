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

/* =====================================================
   ALERT INGESTION (Python → Backend)
===================================================== */
router.post("/", createAlert);

/* =====================================================
   DASHBOARD
===================================================== */
router.get("/", getAlerts);
router.get("/stats", getAlertStats);

/* =====================================================
   LOGS (TABLE + SEARCH + PAGINATION)
===================================================== */
router.get("/logs", getLogs);

/* =====================================================
   EXPORT
===================================================== */
router.get("/export", exportLogs);

/* =====================================================
   LOG ANALYTICS
===================================================== */
router.get("/logs/insights", getLogsInsights);
router.get("/logs/timeline", getTrafficTimeline);
router.get("/logs/top-destinations", getTopAttackedDestinations);

module.exports = router;
