const express = require("express");
const router = express.Router();
const { getModelMetrics, getModelSummary } = require("../controllers/modelController");

router.get("/metrics", getModelMetrics);
router.get("/summary", getModelSummary);

module.exports = router;
