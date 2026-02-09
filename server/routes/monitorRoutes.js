const express = require("express");
const router = express.Router();

const {
  startMonitoring,
  stopMonitoring,
  getStatus,
} = require("../controllers/monitorController");

/* ======================================================
   MONITORING ROUTES – Phase-2 ML-NIDS
====================================================== */

/**
 * POST /api/monitor/start
 * Starts the Python realtime detection engine
 */
router.post("/start", startMonitoring);

/**
 * POST /api/monitor/stop
 * Stops the running detection engine
 */
router.post("/stop", stopMonitoring);

/**
 * GET /api/monitor/status
 * Returns current monitoring status
 */
router.get("/status", getStatus);

module.exports = router;
