const Settings = require("../models/Settings");

/* ================= GET SETTINGS ================= */
exports.getSettings = async (req, res) => {
  try {
    const settings = await Settings.findOne().sort({ createdAt: -1 });
    res.json(settings);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

/* ================= SAVE / UPDATE SETTINGS ================= */
exports.saveSettings = async (req, res) => {
  try {
    const settings = new Settings(req.body);
    await settings.save();

    res.json({
      message: "Settings saved successfully",
      settings,
    });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};
