const express = require("express");
const {
  startMonitoring,
  stopMonitoring,
  getStatus,
} = require("../controllers/monitorController");

const router = express.Router();

router.post("/start", startMonitoring);
router.post("/stop", stopMonitoring);
router.get("/status", getStatus);

module.exports = router;
