const mongoose = require("mongoose");

/**
 * Settings Schema – Phase-2 Realtime ML-NIDS
 * Controls Python detection-engine runtime behavior
 */

const SettingsSchema = new mongoose.Schema(
  {
    /* ===============================
       ML CONFIGURATION
    =============================== */

    models: {
      type: [String],
      required: true,
      default: [
        "LogisticRegression",
        "DecisionTree",
        "RandomForest",
        "KNN",
        "NaiveBayes",
        "GradientBoosting",
        "XGBoost",
        "LightGBM",
        "MLP",
      ],
    },

    threshold: {
      type: Number,
      required: true,
      min: 0,
      max: 1,
      default: 0.5,
    },

    voteK: {
      type: Number,
      required: true,
      min: 1,
      default: 3,
    },

    /* ===============================
       FLOW CONFIGURATION
    =============================== */

    flowTimeout: {
      type: Number, // seconds
      required: true,
      min: 1,
      default: 10,
    },

    /* ===============================
       NETWORK CONFIGURATION
    =============================== */

    interface: {
      type: String,
      required: true, // mandatory for Windows / hotspot
    },
    
    protocol: {
      type: String,
      enum: ["tcp", "udp", "both"],
      default: "both",
    },
  },
  {
    timestamps: true, // createdAt, updatedAt
  }
);

module.exports = mongoose.model("Settings", SettingsSchema);
