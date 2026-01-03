const ModelMetric = require("../models/ModelMetric");

/**
 * GET /api/models/metrics
 * Full metrics for models page
 */
exports.getModelMetrics = async (req, res) => {
  try {
    const metrics = await ModelMetric.find().sort({ accuracy: -1 });
    res.json(metrics);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/**
 * GET /api/models/summary
 * Lightweight metrics (future use)
 */
exports.getModelSummary = async (req, res) => {
  try {
    const metrics = await ModelMetric.find(
      {},
      { modelName: 1, precision: 1, recall: 1, _id: 0 }
    );
    res.json(metrics);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
