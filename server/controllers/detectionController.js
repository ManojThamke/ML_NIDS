const DetectionLog = require("../models/DetectionLog");

/* =====================================================
   CREATE RAW DETECTION (OPTIONAL / LEGACY)
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
    res.status(400).json({ error: err.message });
  }
};

/* =====================================================
   RECENT RAW DETECTIONS (OPTIONAL)
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
   DETECTION TIMELINE (RAW / LEGACY)
   Used by charts calling /detections/timeline
===================================================== */
exports.getDetectionTimeline = async (req, res) => {
  try {
    const { range = "24h" } = req.query;

    const now = Date.now();
    const rangeMap = {
  "1h": 1 * 60 * 60 * 1000,        // 1 hour
  "2h": 2 * 60 * 60 * 1000,        // 2 hours
  "24h": 24 * 60 * 60 * 1000,      // 24 hours
  "7d": 7 * 24 * 60 * 60 * 1000,   // 7 days
  "30d": 30 * 24 * 60 * 60 * 1000, // 30 days
  "1y": 365 * 24 * 60 * 60 * 1000, // 1 year
};


    const windowMs = rangeMap[range] || rangeMap["24h"];

    const data = await DetectionLog.aggregate([
      {
        $match: {
          timestamp: { $gte: new Date(now - windowMs) },
        },
      },
      {
        $group: {
          _id: {
            $dateToString: {
              format: "%Y-%m-%d %H:%M",
              date: "$timestamp",
            },
          },
          count: { $sum: 1 },
        },
      },
      { $sort: { _id: 1 } },
    ]);

    res.json(
      data.map((d) => ({
        timestamp: d._id,
        count: d.count,
      }))
    );
  } catch (err) {
    console.error("Detection timeline error:", err);
    res.status(500).json({ error: err.message });
  }
};
