const Alert = require("../models/DetectionLog");

/**
 * ================================
 * DETECTION DISTRIBUTION
 * ATTACK vs BENIGN
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
 * CONFIDENCE BANDS (GLOBAL)
 * ================================
 */
exports.getConfidenceBands = async (req, res) => {
  try {
    const bands = [
      { label: "0–20%", min: 0.0, max: 0.2 },
      { label: "20–40%", min: 0.2, max: 0.4 },
      { label: "40–60%", min: 0.4, max: 0.6 },
      { label: "60–80%", min: 0.6, max: 0.8 },
      { label: "80–100%", min: 0.8, max: 1.0 },
    ];

    const results = [];

    for (const band of bands) {
      const count = await Alert.countDocuments({
        confidence: { $gte: band.min, $lt: band.max },
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

/**
 * ======================================
 * PER-MODEL AVERAGE CONFIDENCE (GLOBAL)
 * ======================================
 */
exports.getPerModelAverageConfidence = async (req, res) => {
  try {
    const pipeline = [
      {
        $project: {
          models: { $objectToArray: "$modelProbabilities" }
        }
      },
      { $unwind: "$models" },
      {
        $group: {
          _id: "$models.k",
          avgConfidence: { $avg: "$models.v" }
        }
      },
      {
        $project: {
          _id: 0,
          model: "$_id",
          avgConfidence: { $round: ["$avgConfidence", 6] }
        }
      },
      { $sort: { avgConfidence: -1 } }
    ];

    const result = await Alert.aggregate(pipeline);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/**
 * ================================
 * MODEL DOMINANCE FREQUENCY
 * ================================
 */
exports.getModelDominanceFrequency = async (req, res) => {
  try {
    const alerts = await Alert.find(
      { modelProbabilities: { $exists: true, $ne: {} } },
      { modelProbabilities: 1 }
    ).lean();

    const dominanceCount = {};
    let total = 0;

    alerts.forEach(alert => {
      const models = alert.modelProbabilities;
      if (!models) return;

      let dominantModel = null;
      let maxConfidence = -1;

      for (const [model, conf] of Object.entries(models)) {
        if (conf > maxConfidence) {
          maxConfidence = conf;
          dominantModel = model;
        }
      }

      if (dominantModel) {
        dominanceCount[dominantModel] =
          (dominanceCount[dominantModel] || 0) + 1;
        total++;
      }
    });

    const result = Object.entries(dominanceCount).map(
      ([model, count]) => ({
        model,
        percent: +((count / total) * 100).toFixed(2),
      })
    );

    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/**
 * ================================
 * MODEL AGREEMENT MATRIX (HEATMAP)
 * ================================
 */
exports.getModelAgreementMatrix = async (req, res) => {
  try {
    const alerts = await Alert.find(
      { modelProbabilities: { $exists: true } },
      { modelProbabilities: 1 }
    ).lean();

    const models = new Set();
    alerts.forEach(a => {
      Object.keys(a.modelProbabilities || {}).forEach(m => models.add(m));
    });

    const modelList = Array.from(models);
    const matrix = {};

    modelList.forEach(m1 => {
      matrix[m1] = {};
      modelList.forEach(m2 => {
        let agree = 0;
        let total = 0;

        alerts.forEach(a => {
          const p = a.modelProbabilities;
          if (p?.[m1] != null && p?.[m2] != null) {
            const l1 = p[m1] >= 0.5 ? "ATTACK" : "BENIGN";
            const l2 = p[m2] >= 0.5 ? "ATTACK" : "BENIGN";
            if (l1 === l2) agree++;
            total++;
          }
        });

        matrix[m1][m2] = total === 0 ? 0 : +((agree / total) * 100).toFixed(2);
      });
    });

    res.json({ models: modelList, matrix });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/**
 * ================================
 * ENSEMBLE vs BEST MODEL (CONFIDENCE)
 * ================================
 */
exports.getEnsembleVsBestModel = async (req, res) => {
  try {
    const alerts = await Alert.find(
      { modelProbabilities: { $exists: true } },
      { confidence: 1, modelProbabilities: 1 }
    )
      .sort({ createdAt: 1 })
      .limit(50);

    const data = alerts.map((alert, idx) => {
      const modelValues = Object.values(alert.modelProbabilities || {});
      const bestModelConfidence = modelValues.length
        ? Math.max(...modelValues)
        : 0;

      return {
        index: idx + 1,
        ensembleConfidence: +(alert.confidence * 100).toFixed(2),
        bestModelConfidence: +(bestModelConfidence * 100).toFixed(2),
      };
    });

    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/**
 * ================================
 * ATTACK TIMELINE
 * ================================
 */
exports.getAttackTimeline = async (req, res) => {
  try {
    const range = req.query.range || "1h";
    const now = new Date();
    const startTime = new Date(now);

    if (range === "1h") startTime.setHours(now.getHours() - 1);
    else if (range === "6h") startTime.setHours(now.getHours() - 6);
    else startTime.setHours(now.getHours() - 24);

    const timeline = await Alert.aggregate([
      {
        $match: {
          finalLabel: "ATTACK",
          createdAt: { $gte: startTime },
        },
      },
      {
        $group: {
          _id: {
            minute: {
              $dateToString: {
                format: "%H:%M",
                date: "$createdAt",
              },
            },
          },
          count: { $sum: 1 },
          avgConfidence: { $avg: "$confidence" },
        },
      },
      { $sort: { "_id.minute": 1 } },
    ]);

    res.json(
      timeline.map(t => ({
        time: t._id.minute,
        attacks: t.count,
        avgConfidence: +(t.avgConfidence * 100).toFixed(2),
      }))
    );
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/**
 * ================================
 * TOP ATTACKED DESTINATIONS
 * ================================
 */
exports.getTopAttackedDestinations = async (req, res) => {
  try {
    const limit = parseInt(req.query.limit || 5);

    const data = await Alert.aggregate([
      { $match: { finalLabel: "ATTACK" } },
      {
        $group: {
          _id: "$destinationIP",
          count: { $sum: 1 },
        },
      },
      { $sort: { count: -1 } },
      { $limit: limit },
    ]);

    res.json(
      data.map(d => ({
        destination: d._id,
        attacks: d.count,
      }))
    );
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
