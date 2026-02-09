const Settings = require("../models/Settings");

/* ======================================================
   GET LATEST SETTINGS
====================================================== */
exports.getSettings = async (req, res) => {
  try {
    const settings = await Settings.findOne().sort({ updatedAt: -1 });

    if (!settings) {
      return res.json(null);
    }

    res.json(settings);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/* ======================================================
   SAVE / UPDATE SETTINGS
====================================================== */
exports.saveSettings = async (req, res) => {
  try {
    const {
      models,
      threshold,
      voteK,
      flowTimeout,
      interface: iface,
      protocol,
    } = req.body;

    /* ================= VALIDATION ================= */

    if (!iface || iface.trim() === "") {
      return res.status(400).json({
        error: "Network interface is required",
      });
    }

    if (!models || models.length === 0) {
      return res.status(400).json({
        error: "At least one model must be selected",
      });
    }

    /* ================= SAVE SETTINGS ================= */

    const settings = new Settings({
      models,
      threshold: threshold ?? 0.5,
      voteK: voteK ?? 3,
      flowTimeout: flowTimeout ?? 10,
      interface: iface.trim(),
      protocol: protocol ?? "both",
    });

    await settings.save();

    res.json({
      message: "Settings saved successfully",
      settings,
    });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};
