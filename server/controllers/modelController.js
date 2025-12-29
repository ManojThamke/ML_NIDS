const ModelMetric = require("../models/ModelMetric");

exports.getModelMetrics = async (req, res) => {
  const metrics = await ModelMetric.find().sort({ accuracy: -1 });
  res.json(metrics);
};
