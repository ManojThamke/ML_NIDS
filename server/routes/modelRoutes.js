const express = require("express");
const router = express.Router();
const { getModelMetrics } = require("../controllers/modelController");

router.get("/", getModelMetrics);

module.exports = router;
