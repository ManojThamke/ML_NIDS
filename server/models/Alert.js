const mongoose = require("mongoose");

const AlertSchema = new mongoose.Schema(
  {
    timestamp: {
      type: String,
      required: true,
    },

    sourceIP: {
      type: String,
      required: true,
    },

    destinationIP: {
      type: String,
      required: true,
    },

    modelUsed: {
      type: String,
      required: true,
    },

    probability: {
      type: Number,
      required: true,
    },

    finalLabel: {
      type: String,
      enum: ["ATTACK", "BENIGN"],
      required: true,
    },

    // ✅ NEW (IMPORTANT)
    perModel: {
      type: mongoose.Schema.Types.Mixed, // {rf:0.7, xgb:0.8}
      default: {},
    },

    features: {
      type: mongoose.Schema.Types.Mixed, // packet features
      default: {},
    },
  },
  {
    timestamps: true,
  }
);

module.exports = mongoose.model("Alert", AlertSchema);
