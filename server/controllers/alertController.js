const Alert = require("../models/DetectionLog");
const { Parser } = require("json2csv");

/* =====================================================
   CREATE ALERT (Python → Backend)
   POST /api/alerts
===================================================== */
exports.createAlert = async (req, res) => {
  try {
    const body = { ...req.body };

    // per_model safety
    if (body.per_model) {
      body.modelProbabilities =
        typeof body.per_model === "string"
          ? JSON.parse(body.per_model)
          : body.per_model;
      delete body.per_model;
    }

    // features safety
    if (body.features && typeof body.features === "string") {
      body.features = JSON.parse(body.features);
    }

    const alert = new Alert(body);
    const saved = await alert.save();

    res.status(201).json(saved);
  } catch (err) {
    console.error("Create alert error:", err);
    res.status(400).json({ error: err.message });
  }
};

/* =====================================================
   DASHBOARD TABLE (LATEST ALERTS)
   GET /api/alerts
===================================================== */
exports.getAlerts = async (req, res) => {
  try {
    const alerts = await Alert.find()
      .sort({ createdAt: -1 })
      .limit(10)
      .lean();

    res.json(alerts);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/* =====================================================
   ALERT STATS (CARDS)
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
   LOGS TABLE (FILTER + SEARCH + PAGINATION)
   GET /api/alerts/logs
===================================================== */
exports.getLogs = async (req, res) => {
  try {
    let { page = 1, limit = 50, label, minConf, maxConf, search } = req.query;

    page = Math.max(parseInt(page), 1);
    limit = Math.min(parseInt(limit), 200);

    const query = {};

    if (label) query.finalLabel = label.toUpperCase();

    if (minConf || maxConf) {
      query.confidence = {};
      if (minConf) query.confidence.$gte = Number(minConf);
      if (maxConf) query.confidence.$lte = Number(maxConf);
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
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/* =====================================================
   EXPORT ALERT LOGS
   GET /api/alerts/export
===================================================== */
exports.exportLogs = async (req, res) => {
  try {
    const {
      format = "csv",
      range = "24h",
      onlyAttack,
      includeMeta,
      includeModelProb,
    } = req.query;

    const now = Date.now();
    const rangeMap = {
      "1h": 60 * 60 * 1000,
      "24h": 24 * 60 * 60 * 1000,
      "7d": 7 * 24 * 60 * 60 * 1000,
      "30d": 30 * 24 * 60 * 60 * 1000,
    };

    const query = {};
    if (rangeMap[range]) {
      query.createdAt = { $gte: new Date(now - rangeMap[range]) };
    }

    if (onlyAttack === "true") {
      query.finalLabel = "ATTACK";
    }

    const logs = await Alert.find(query).lean();

    const rows = logs.map((log) => {
      const row = {
        timestamp: new Date(log.timestamp || log.createdAt).toISOString(),
        sourceIP: log.sourceIP,
        destinationIP: log.destinationIP,
        srcPort: log.srcPort,
        dstPort: log.dstPort,
        protocol: log.protocol,
        finalLabel: log.finalLabel,
        confidence: +(log.confidence * 100).toFixed(2),
        severity: log.severity,
        attackVotes: log.attackVotes,
        totalModels: log.totalModels,
      };

      if (includeMeta === "true") {
        row.flowDuration = log.flowDuration;
        row.threshold = log.threshold;
        row.voteK = log.voteK;
        row.aggregationMethod = log.aggregationMethod;
        row.hybridLabel = log.hybridLabel;
        row.hybridReason = log.hybridReason;
      }

      if (includeModelProb === "true" && log.modelProbabilities) {
        Object.entries(log.modelProbabilities).forEach(
          ([model, prob]) => {
            row[`prob_${model}`] = +(prob * 100).toFixed(2);
          }
        );
      }

      return row;
    });

    if (format === "json") {
      res.setHeader(
        "Content-Disposition",
        `attachment; filename=alerts_${range}.json`
      );
      return res.json(rows);
    }

    const csv = new Parser().parse(rows);

    res.setHeader("Content-Type", "text/csv");
    res.setHeader(
      "Content-Disposition",
      `attachment; filename=alerts_${range}.csv`
    );
    res.send(csv);
  } catch (err) {
    console.error("Export error:", err);
    res.status(500).json({ error: err.message });
  }
};
/* =====================================================
   ALERT LOG INSIGHTS (CARDS)
   GET /api/alerts/logs/insights
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
      Alert.countDocuments({ confidence: { $gte: 0.7 } }),
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
   ALERT TRAFFIC TIMELINE
   GET /api/alerts/logs/timeline
===================================================== */
exports.getAlertTimeline = async (req, res) => {
  try {
    const { range = "24h" } = req.query;

    const rangeMap = {
      "1h": 1 * 60 * 60 * 1000,
      "2h": 2 * 60 * 60 * 1000,
      "24h": 24 * 60 * 60 * 1000,
      "7d": 7 * 24 * 60 * 60 * 1000,
      "30d": 30 * 24 * 60 * 60 * 1000,
      "1y": 365 * 24 * 60 * 60 * 1000,
    };

    const windowMs = rangeMap[range] || rangeMap["24h"];
    const now = Date.now();

    const data = await Alert.aggregate([
      { $match: { createdAt: { $gte: new Date(now - windowMs) } } },
      {
        $group: {
          _id: {
            $dateToString: {
              format: "%Y-%m-%d %H:%M",
              date: "$createdAt",
            },
          },
          count: { $sum: 1 },
        },
      },
      { $sort: { _id: 1 } },
    ]);

    res.json(
      data.map(d => ({
        timestamp: d._id,
        count: d.count,
      }))
    );
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
exports.getAlertTopDestinations = async (req, res) => {
  try {
    const limit = parseInt(req.query.limit || 5);

    const data = await Alert.aggregate([
      { $match: { finalLabel: "ATTACK" } },
      { $group: { _id: "$destinationIP", count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $limit: limit },
    ]);

    res.json(
      data.map(d => ({
        destination: d._id,
        count: d.count,
      }))
    );
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
