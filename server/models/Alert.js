const mongoose = require("mongoose");

const AlertSchema = new mongoose.Schema(
  {
    timestamp: {
      type: String,
      required: true
    },
    sourceIP: {
      type: String,
      required: true
    },
    destinationIP: {
      type: String,
      required: true
    },
    modelUsed: {
      type: String,
      required: true
    },
    probability: {
      type: Number,
      required: true
    },
    finalLabel: {
      type: String,
      enum: ["ATTACK", "BENIGN"],
      required: true
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model("Alert", AlertSchema);
