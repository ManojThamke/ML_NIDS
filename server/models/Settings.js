const mongoose = require("mongoose");

const SettingsSchema = new mongoose.Schema(
  {
    models: [String],
    aggregation: String,
    smoothing: Number,
    threshold: Number,
    interface: String,
    filter: String,
  },
  { timestamps: true }
);

module.exports = mongoose.model("Settings", SettingsSchema);
