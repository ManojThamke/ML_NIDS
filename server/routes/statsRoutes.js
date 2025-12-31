const express = require("express");
const router = express.Router();
const {
  getDetectionDistribution,
  getProbabilityBands,
} = require("../controllers/statsController");

router.get("/detection-distribution", getDetectionDistribution);
router.get("/probability-bands", getProbabilityBands);

module.exports = router;
