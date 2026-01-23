const express = require("express");
const router = express.Router();
const controller = require("../controllers/detectionController");

/* =====================================================
   PYTHON → BACKEND
===================================================== */
router.post("/", controller.createDetection);

/* =====================================================
   DASHBOARD
===================================================== */
router.get("/recent", controller.getRecentDetections);
router.get("/stats", controller.getStats);

/* =====================================================
   LOGS & ANALYTICS
===================================================== */
router.get("/logs", controller.getLogs);
router.get("/export", controller.exportLogs);
router.get("/timeline", controller.getTrafficTimeline);

module.exports = router;
