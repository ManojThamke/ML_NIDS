const DetectionLog = require("../models/DetectionLog");
const { Parser } = require("json2csv");

/* =====================================================
   CREATE DETECTION (Python → Backend)
   POST /api/detections
===================================================== */
exports.createDetection = async (req, res) => {
  try {
    const log = new DetectionLog({
      ...req.body,
      timestamp: new Date(req.body.timestamp),
    });

    await log.save();
    res.status(201).json({ message: "Detection saved" });
  } catch (err) {
    console.error("❌ Detection save failed:", err.message);
    res.status(400).json({ error: err.message });
  }
};

/* =====================================================
   RECENT DETECTIONS (Dashboard Table)
===================================================== */
exports.getRecentDetections = async (req, res) => {
  try {
    const limit = Math.min(Number(req.query.limit) || 10, 100);

    const logs = await DetectionLog.find()
      .sort({ timestamp: -1 })
      .limit(limit)
      .lean();

    res.json(logs);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/* =====================================================
   GLOBAL DASHBOARD STATS (Cards)
===================================================== */
exports.getStats = async (req, res) => {
  try {
    const [total, attack, benign, high] = await Promise.all([
      DetectionLog.countDocuments(),
      DetectionLog.countDocuments({ finalLabel: "ATTACK" }),
      DetectionLog.countDocuments({ finalLabel: "BENIGN" }),
      DetectionLog.countDocuments({ severity: "HIGH" }),
    ]);

    res.json({ total, attack, benign, high });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/* =====================================================
   LOGS API (FILTER + PAGINATION)
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
      DetectionLog.find(query)
        .sort({ timestamp: -1 })
        .skip((page - 1) * limit)
        .limit(limit)
        .lean(),
      DetectionLog.countDocuments(query),
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
   EXPORT LOGS (CSV / JSON)
===================================================== */
exports.exportLogs = async (req, res) => {
  try {
    const { format = "csv" } = req.query;

    const logs = await DetectionLog.find()
      .sort({ timestamp: -1 })
      .lean();

    if (format === "json") {
      res.setHeader("Content-Type", "application/json");
      res.setHeader(
        "Content-Disposition",
        "attachment; filename=detections.json"
      );
      return res.send(logs);
    }

    const fields = [
      "timestamp",
      "sourceIP",
      "destinationIP",
      "dstPort",
      "protocol",
      "finalLabel",
      "hybridLabel",
      "severity",
      "confidence",
      "attackVotes",
      "flowDuration",
    ];

    const csv = new Parser({ fields }).parse(logs);

    res.setHeader("Content-Type", "text/csv");
    res.setHeader(
      "Content-Disposition",
      "attachment; filename=detections.csv"
    );
    res.send(csv);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/* =====================================================
   TRAFFIC TIMELINE (Charts)
===================================================== */
exports.getTrafficTimeline = async (req, res) => {
  try {
    const { range = "1h" } = req.query;

    const now = Date.now();
    const config = {
      "1h": { ms: 3600000, bucket: 60000 },
      "24h": { ms: 86400000, bucket: 300000 },
      "7d": { ms: 604800000, bucket: 3600000 },
    };

    const cfg = config[range] || config["24h"];

    const data = await DetectionLog.aggregate([
      { $match: { timestamp: { $gte: new Date(now - cfg.ms) } } },
      {
        $project: {
          bucket: {
            $toDate: {
              $subtract: [
                { $toLong: "$timestamp" },
                { $mod: [{ $toLong: "$timestamp" }, cfg.bucket] },
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
