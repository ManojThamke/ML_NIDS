const Alert = require("../models/Alert");
const { Parser } = require("json2csv");

/* =====================================================
   CREATE ALERT (Python → Backend)
   POST /api/alerts
===================================================== */
exports.createAlert = async (req, res) => {
  try {
    const alert = new Alert(req.body);
    const savedAlert = await alert.save();
    res.status(201).json(savedAlert);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

/* =====================================================
   DASHBOARD TABLE (LATEST ONLY)
   GET /api/alerts
   ⚠️ LIMITED ON PURPOSE
===================================================== */
exports.getAlerts = async (req, res) => {
  try {
    const alerts = await Alert.find()
      .sort({ createdAt: -1 })
      .limit(10)
      .lean(); // ⚡ performance

    res.status(200).json(alerts);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

/* =====================================================
   DASHBOARD STATS (FULL DATABASE)
   GET /api/alerts/stats
===================================================== */
exports.getAlertStats = async (req, res) => {
  try {
    const [total, attack, benign] = await Promise.all([
      Alert.countDocuments(),
      Alert.countDocuments({ finalLabel: "ATTACK" }),
      Alert.countDocuments({ finalLabel: "BENIGN" }),
    ]);

    res.json({
      total,
      attack,
      benign,
      attackPercent: total ? ((attack / total) * 100).toFixed(1) : 0,
      benignPercent: total ? ((benign / total) * 100).toFixed(1) : 0,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/* =====================================================
   SOC LOGS API (FILTER + SEARCH + PAGINATION)
   GET /api/alerts/logs
===================================================== */
exports.getLogs = async (req, res) => {
  try {
    let {
      page = 1,
      limit = 50,
      label,
      minProb,
      maxProb,
      search,
    } = req.query;

    // ✅ sanitize inputs
    page = Math.max(parseInt(page), 1);
    limit = Math.min(parseInt(limit), 200); // prevent abuse

    const query = {};

    // 🔍 Label filter
    if (label) {
      query.finalLabel = label.toUpperCase();
    }

    // 📊 Probability range
    if (minProb || maxProb) {
      query.probability = {};
      if (minProb !== undefined) query.probability.$gte = Number(minProb);
      if (maxProb !== undefined) query.probability.$lte = Number(maxProb);
    }

    // 🔎 IP Search (safe regex)
    if (search) {
      const safeSearch = search.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      query.$or = [
        { sourceIP: { $regex: safeSearch, $options: "i" } },
        { destinationIP: { $regex: safeSearch, $options: "i" } },
      ];
    }

    const [logs, total] = await Promise.all([
      Alert.find(query)
        .sort({ createdAt: -1 })
        .skip((page - 1) * limit)
        .limit(limit)
        .lean(),
      Alert.countDocuments(query),
    ]);

    res.json({
      logs,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit),
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

/* ===============Export Logs=========================*/

exports.exportLogs = async (req, res) => {
  try {
    const {
      label,
      minProb,
      maxProb,
      search,
      format = "csv",
      range,
      onlyAttack,
    } = req.query;

    const query = {};

    /* ===== Label ===== */
    if (label) query.finalLabel = label.toUpperCase();

    if (onlyAttack === "true") {
      query.finalLabel = "ATTACK";
    }

    /* ===== Probability ===== */
    if (minProb || maxProb) {
      query.probability = {};
      if (minProb) query.probability.$gte = Number(minProb);
      if (maxProb) query.probability.$lte = Number(maxProb);
    }

    /* ===== Time Range ===== */
    if (range) {
      const now = Date.now();
      let startTime;

      switch (range) {
        case "1h":
          startTime = new Date(now - 60 * 60 * 1000);
          break;
        case "24h":
          startTime = new Date(now - 24 * 60 * 60 * 1000);
          break;
        case "7d":
          startTime = new Date(now - 7 * 24 * 60 * 60 * 1000);
          break;
        case "30d":
          startTime = new Date(now - 30 * 24 * 60 * 60 * 1000);
          break;
      }

      if (startTime) {
        query.createdAt = { $gte: startTime };
      }
    }

    /* ===== IP Search ===== */
    if (search) {
      const safeSearch = search.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      query.$or = [
        { sourceIP: { $regex: safeSearch, $options: "i" } },
        { destinationIP: { $regex: safeSearch, $options: "i" } },
      ];
    }

    /* ===== Fetch ALL matching logs (NO LIMIT) ===== */
    const logs = await Alert.find(query)
      .sort({ createdAt: -1 })
      .lean();

    /* ===== JSON ===== */
    if (format === "json") {
      res.setHeader("Content-Type", "application/json");
      res.setHeader(
        "Content-Disposition",
        "attachment; filename=traffic_logs.json"
      );
      return res.status(200).send(JSON.stringify(logs));
    }

    /* ===== CSV ===== */
    const fields = [
      "timestamp",
      "sourceIP",
      "destinationIP",
      "probability",
      "finalLabel",
    ];

    const parser = new Parser({ fields });
    const csv = parser.parse(logs);

    res.setHeader("Content-Type", "text/csv");
    res.setHeader(
      "Content-Disposition",
      "attachment; filename=traffic_logs.csv"
    );
    return res.status(200).send(csv);

  } catch (error) {
    console.error("Export error:", error);
    res.status(500).json({ error: error.message });
  }
};


/**
 * =====================================================
 * LOGS INSIGHTS (SOC AGGREGATION)
 * GET /api/alerts/logs/insights
 * =====================================================
 */
exports.getLogsInsights = async (req, res) => {
  const [
    topSourceIPs,
    topDestinationIPs,
    attackCount,
    benignCount,
    highRiskCount,
  ] = await Promise.all([
    Alert.aggregate([{ $group: { _id: "$sourceIP", count: { $sum: 1 } } }, { $sort: { count: -1 } }, { $limit: 5 }]),
    Alert.aggregate([{ $group: { _id: "$destinationIP", count: { $sum: 1 } } }, { $sort: { count: -1 } }, { $limit: 5 }]),
    Alert.countDocuments({ finalLabel: "ATTACK" }),
    Alert.countDocuments({ finalLabel: "BENIGN" }),
    Alert.countDocuments({ probability: { $gte: 0.7 } }),
  ]);

  res.json({
    topSourceIPs,
    topDestinationIPs,
    attackCount,
    benignCount,
    highRiskCount,
  });
};

/**
 * =====================================================
 * TOP ATTACKED DESTINATIONS (GLOBAL)
 * GET /api/alerts/logs/top-destinations
 * =====================================================
 */
exports.getTopAttackedDestinations = async (req, res) => {
  try {
    const data = await Alert.aggregate([
      { $match: { finalLabel: "ATTACK" } }, // only attacks
      {
        $group: {
          _id: "$destinationIP",
          count: { $sum: 1 }
        }
      },
      { $sort: { count: -1 } },
      { $limit: 5 }
    ]);

    res.json(data.map(d => ({
      destination: d._id,
      count: d.count
    })));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};


/**
 * =====================================================
 * Traffic Timeline (Aligned & UTC Safe)
 * GET /api/alerts/logs/timeline?range=1h|2h|24h|7d|30d|1y
 * =====================================================
 */
exports.getTrafficTimeline = async (req, res) => {
  try {
    const { range = "1h" } = req.query;

    const now = new Date();
    let startTime;
    let bucketSize; // milliseconds

    switch (range) {
      case "1h":
        startTime = new Date(now.getTime() - 60 * 60 * 1000);
        bucketSize = 60 * 1000; // 1 minute
        break;

      case "2h":
        startTime = new Date(now.getTime() - 2 * 60 * 60 * 1000);
        bucketSize = 2 * 60 * 1000;
        break;

      case "24h":
        startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        bucketSize = 5 * 60 * 1000;
        break;

      case "7d":
        startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        bucketSize = 60 * 60 * 1000;
        break;

      case "30d":
        startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        bucketSize = 6 * 60 * 60 * 1000;
        break;

      case "1y":
        startTime = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
        bucketSize = 24 * 60 * 60 * 1000;
        break;

      default:
        startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        bucketSize = 5 *60 * 1000;
    }

    const data = await Alert.aggregate([
      { $match: { createdAt: { $gte: startTime } } },
      {
        $project: {
          bucket: {
            $toDate: {
              $subtract: [
                { $toLong: "$createdAt" },
                { $mod: [{ $toLong: "$createdAt" }, bucketSize] }
              ],
            },
          },
        },
      },
      {
        $group: {
          _id: "$bucket",
          count: { $sum: 1 }
        },
      },
      { $sort: { _id: 1 } },
    ]);

    res.json(
      data.map(d => ({
        timestamp: new Date(d._id),
        count: d.count,
      }))
    );
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
