const express = require("express");
const router = express.Router();
const controller = require("../controllers/detectionController");

/* PYTHON → BACKEND (RAW / LEGACY) */
router.post("/", controller.createDetection);

/* DASHBOARD (OPTIONAL) */
router.get("/recent", controller.getRecentDetections);
router.get("/timeline", controller.getDetectionTimeline);

module.exports = router;
