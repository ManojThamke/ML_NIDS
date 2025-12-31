const Alert = require("../models/Alert");

/**
 * ================================
 * DETECTION DISTRIBUTION
 * Attack vs Benign
 * ================================
 */
exports.getDetectionDistribution = async (req, res) => {
  try {
    const [attack, benign] = await Promise.all([
      Alert.countDocuments({ finalLabel: "ATTACK" }),
      Alert.countDocuments({ finalLabel: "BENIGN" }),
    ]);

    res.json({
      attack,
      benign,
      total: attack + benign,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/**
 * ================================
 * PROBABILITY CONFIDENCE BANDS
 * ================================
 */
exports.getProbabilityBands = async (req, res) => {
  try {
    const bands = [
      { label: "0-20", min: 0.0, max: 0.2 },
      { label: "20-40", min: 0.2, max: 0.4 },
      { label: "40-60", min: 0.4, max: 0.6 },
      { label: "60-80", min: 0.6, max: 0.8 },
      { label: "80-100", min: 0.8, max: 1.0 },
    ];

    const results = [];

    for (const band of bands) {
      const count = await Alert.countDocuments({
        probability: { $gte: band.min, $lt: band.max },
      });

      results.push({
        range: band.label,
        count,
      });
    }

    res.json(results);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
