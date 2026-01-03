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
/**
 * ======================================
 * PER-MODEL AVERAGE PROBABILITY (GLOBAL)
 * ======================================
 */
exports.getPerModelAverageProbability = async (req, res) => {
  try {
    const pipeline = [
      {
        $project: {
          perModel: { $objectToArray: "$perModel" }
        }
      },
      { $unwind: "$perModel" },
      {
        $group: {
          _id: "$perModel.k",
          avgProbability: { $avg: "$perModel.v" }
        }
      },
      {
        $project: {
          _id: 0,
          model: "$_id",
          avgProbability: { $round: ["$avgProbability", 6] }
        }
      },
      { $sort: { avgProbability: -1 } }
    ];

    const result = await require("../models/Alert").aggregate(pipeline);
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
      { perModel: { $exists: true, $ne: {} } },
      { perModel: 1 }
    ).lean();

    const dominanceCount = {};
    let total = 0;

    alerts.forEach(alert => {
      const models = alert.perModel;
      if (!models || Object.keys(models).length === 0) return;

      let dominantModel = null;
      let maxProb = -1;

      for (const [model, prob] of Object.entries(models)) {
        if (prob > maxProb) {
          maxProb = prob;
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

// HeapMap 
exports.getModelAgreementMatrix = async (req, res) => {
  try {
    const alerts = await Alert.find(
      { perModel: { $exists: true } },
      { perModel: 1, finalLabel: 1 }
    ).lean();

    const models = new Set();
    alerts.forEach(a => {
      Object.keys(a.perModel || {}).forEach(m => models.add(m));
    });

    const modelList = Array.from(models);
    const matrix = {};

    modelList.forEach(m1 => {
      matrix[m1] = {};
      modelList.forEach(m2 => {
        let agree = 0;
        let total = 0;

        alerts.forEach(a => {
          if (a.perModel?.[m1] != null && a.perModel?.[m2] != null) {
            const l1 = a.perModel[m1] >= 0.5 ? "ATTACK" : "BENIGN";
            const l2 = a.perModel[m2] >= 0.5 ? "ATTACK" : "BENIGN";
            if (l1 === l2) agree++;
            total++;
          }
        });

        matrix[m1][m2] = total === 0 ? 0 : +(agree / total * 100).toFixed(2);
      });
    });

    res.json({ models: modelList, matrix });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// Ensemble vs BestModel
exports.getEnsembleVsBestModel = async (req, res) => {
  try {
    const alerts = await Alert.find(
      { perModel: { $exists: true } },
      { probability: 1, perModel: 1, timestamp: 1 }
    )
      .sort({ createdAt: 1 })
      .limit(50); // last 50 alerts (adjustable)

    const data = alerts.map((alert, idx) => {
      const perModelValues = Object.values(alert.perModel || {});
      const bestModelProb = perModelValues.length
        ? Math.max(...perModelValues)
        : 0;

      return {
        index: idx + 1,
        ensemble: +(alert.probability * 100).toFixed(2),
        bestModel: +(bestModelProb * 100).toFixed(2),
      };
    });

    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/**
 * ================================
 * ATTACK TIMELINE (Chart-7)
 * ================================
 */
exports.getAttackTimeline = async (req, res) => {
  try {
    const range = req.query.range || "1h";

    // ⏱ Time window
    const now = new Date();
    let startTime = new Date();

    if (range === "1h") startTime.setHours(now.getHours() - 1);
    else if (range === "6h") startTime.setHours(now.getHours() - 6);
    else startTime.setHours(now.getHours() - 24);

    // 📊 Group attacks by minute
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
          avgProb: { $avg: "$probability" },
        },
      },
      {
        $sort: { "_id.minute": 1 },
      },
    ]);

    res.json(
      timeline.map(t => ({
        time: t._id.minute,
        attacks: t.count,
        avgProb: +(t.avgProb * 100).toFixed(2),
      }))
    );
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/**
 * ================================
 * TOP ATTACKED DESTINATIONS (Chart-8)
 * ================================
 */
exports.getTopAttackedDestinations = async (req, res) => {
  try {
    const limit = parseInt(req.query.limit || 5);

    const data = await Alert.aggregate([
      {
        $match: {
          finalLabel: { $in: ["ATTACK", "Attack", "attack", 1] },
          destinationIP: { $exists: true, $ne: null }
        }
      },

      {
        $sort: { count: -1 },
      },
      {
        $limit: limit,
      },
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
