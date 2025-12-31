const Alert = require("../models/Alert");
const { Parser } = require("json2csv");

/* =====================================================
   CREATE ALERT (Python → Backend)
   POST /api/alerts
   ✅ Parses per_model & features safely
===================================================== */
exports.createAlert = async (req, res) => {
  try {
    const body = { ...req.body };

    // ✅ FIX: per_model may already be an object
    if (body.per_model) {
      if (typeof body.per_model === "string") {
        body.perModel = JSON.parse(body.per_model);
      } else {
        body.perModel = body.per_model;
      }
      delete body.per_model;
    }

    // ✅ FIX: features may already be an object
    if (body.features) {
      if (typeof body.features === "string") {
        body.features = JSON.parse(body.features);
      }
    }

    const alert = new Alert(body);
    const savedAlert = await alert.save();

    res.status(201).json(savedAlert);
  } catch (error) {
    console.error("Create alert error:", error);
    res.status(400).json({ error: error.message });
  }
};


/* =====================================================
   DASHBOARD TABLE (LATEST ONLY)
===================================================== */
exports.getAlerts = async (req, res) => {
  try {
    const alerts = await Alert.find()
      .sort({ createdAt: -1 })
      .limit(10)
      .lean();

    res.status(200).json(alerts);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

/* =====================================================
   DASHBOARD STATS (GLOBAL)
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
   LOGS API (FILTER + SEARCH + PAGINATION)
===================================================== */
exports.getLogs = async (req, res) => {
  try {
    let { page = 1, limit = 50, label, minProb, maxProb, search } = req.query;

    page = Math.max(parseInt(page), 1);
    limit = Math.min(parseInt(limit), 200);

    const query = {};

    if (label) query.finalLabel = label.toUpperCase();

    if (minProb || maxProb) {
      query.probability = {};
      if (minProb) query.probability.$gte = Number(minProb);
      if (maxProb) query.probability.$lte = Number(maxProb);
    }

    if (search) {
      const safe = search.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      query.$or = [
        { sourceIP: { $regex: safe, $options: "i" } },
        { destinationIP: { $regex: safe, $options: "i" } },
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

/* =====================================================
   EXPORT LOGS (FULL DATASET – FAST)
===================================================== */
exports.exportLogs = async (req, res) => {
  try {
    const { label, minProb, maxProb, search, format = "csv", range, onlyAttack } =
      req.query;

    const query = {};

    if (label) query.finalLabel = label.toUpperCase();
    if (onlyAttack === "true") query.finalLabel = "ATTACK";

    if (minProb || maxProb) {
      query.probability = {};
      if (minProb) query.probability.$gte = Number(minProb);
      if (maxProb) query.probability.$lte = Number(maxProb);
    }

    if (range) {
      const now = Date.now();
      const map = {
        "1h": 60 * 60 * 1000,
        "24h": 24 * 60 * 60 * 1000,
        "7d": 7 * 24 * 60 * 60 * 1000,
        "30d": 30 * 24 * 60 * 60 * 1000,
      };
      if (map[range]) {
        query.createdAt = { $gte: new Date(now - map[range]) };
      }
    }

    if (search) {
      const safe = search.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      query.$or = [
        { sourceIP: { $regex: safe, $options: "i" } },
        { destinationIP: { $regex: safe, $options: "i" } },
      ];
    }

    const logs = await Alert.find(query).sort({ createdAt: -1 }).lean();

    if (format === "json") {
      res.setHeader("Content-Type", "application/json");
      res.setHeader(
        "Content-Disposition",
        "attachment; filename=traffic_logs.json"
      );
      return res.send(logs);
    }

    const fields = [
      "timestamp",
      "sourceIP",
      "destinationIP",
      "probability",
      "finalLabel",
    ];

    const csv = new Parser({ fields }).parse(logs);

    res.setHeader("Content-Type", "text/csv");
    res.setHeader(
      "Content-Disposition",
      "attachment; filename=traffic_logs.csv"
    );
    res.send(csv);
  } catch (error) {
    console.error("Export error:", error);
    res.status(500).json({ error: error.message });
  }
};

/* =====================================================
   GLOBAL LOGS INSIGHTS
===================================================== */
exports.getLogsInsights = async (req, res) => {
  try {
    const [
      topSourceIPs,
      topDestinationIPs,
      attackCount,
      benignCount,
      highRiskCount,
    ] = await Promise.all([
      Alert.aggregate([
        { $group: { _id: "$sourceIP", count: { $sum: 1 } } },
        { $sort: { count: -1 } },
        { $limit: 5 },
      ]),
      Alert.aggregate([
        { $group: { _id: "$destinationIP", count: { $sum: 1 } } },
        { $sort: { count: -1 } },
        { $limit: 5 },
      ]),
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
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/* =====================================================
   TOP ATTACKED DESTINATIONS (GLOBAL)
===================================================== */
exports.getTopAttackedDestinations = async (req, res) => {
  try {
    const data = await Alert.aggregate([
      { $match: { finalLabel: "ATTACK" } },
      { $group: { _id: "$destinationIP", count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $limit: 5 },
    ]);

    res.json(
      data.map((d) => ({
        destination: d._id,
        count: d.count,
      }))
    );
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/* =====================================================
   TRAFFIC TIMELINE (ALIGNED & STABLE)
===================================================== */
exports.getTrafficTimeline = async (req, res) => {
  try {
    const { range = "1h" } = req.query;

    const now = Date.now();
    const config = {
      "1h": { ms: 60 * 60 * 1000, bucket: 60 * 1000 },
      "2h": { ms: 2 * 60 * 60 * 1000, bucket: 2 * 60 * 1000 },
      "24h": { ms: 24 * 60 * 60 * 1000, bucket: 5 * 60 * 1000 },
      "7d": { ms: 7 * 24 * 60 * 60 * 1000, bucket: 60 * 60 * 1000 },
      "30d": { ms: 30 * 24 * 60 * 60 * 1000, bucket: 6 * 60 * 60 * 1000 },
      "1y": { ms: 365 * 24 * 60 * 60 * 1000, bucket: 24 * 60 * 60 * 1000 },
    };

    const cfg = config[range] || config["24h"];

    const data = await Alert.aggregate([
      { $match: { createdAt: { $gte: new Date(now - cfg.ms) } } },
      {
        $project: {
          bucket: {
            $toDate: {
              $subtract: [
                { $toLong: "$createdAt" },
                { $mod: [{ $toLong: "$createdAt" }, cfg.bucket] },
              ],
            },
          },
        },
      },
      { $group: { _id: "$bucket", count: { $sum: 1 } } },
      { $sort: { _id: 1 } },
    ]);

    res.json(
      data.map((d) => ({
        timestamp: d._id,
        count: d.count,
      }))
    );
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
