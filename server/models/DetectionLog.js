const mongoose = require("mongoose");

/**
 * DetectionLog Schema – Phase-2 Realtime ML-NIDS
 * Source: Python realtime_v2 engine
 * Dataset logic: CICIDS-based ensemble + hybrid engine
 */

const DetectionLogSchema = new mongoose.Schema(
  {
    /* ===============================
       FLOW IDENTIFIERS
    =============================== */

    timestamp: {
      type: Date,
      required: true,
      index: true
    },

    sourceIP: {
      type: String,
      required: true,
      index: true
    },

    destinationIP: {
      type: String,
      required: true,
      index: true
    },

    srcPort: {
      type: Number,
      required: true
    },

    dstPort: {
      type: Number,
      required: true,
      index: true
    },

    protocol: {
      type: String,
      enum: ["TCP", "UDP"],
      required: true
    },

    /* ===============================
       ML ENSEMBLE OUTPUT
    =============================== */

    finalLabel: {
      type: String,
      enum: ["BENIGN", "ATTACK"],
      required: true,
      index: true
    },

    confidence: {
      type: Number,
      required: true
    },

    attackVotes: {
      type: Number,
      required: true
    },

    totalModels: {
      type: Number,
      required: true
    },

    threshold: {
      type: Number,
      required: true
    },

    voteK: {
      type: Number,
      required: true
    },

    aggregationMethod: {
      type: String,
      default: "global-threshold-voting"
    },

    /* ===============================
       HYBRID DECISION ENGINE
    =============================== */

    hybridLabel: {
      type: String,
      enum: ["BENIGN", "SUSPICIOUS", "ATTACK"],
      required: true,
      index: true
    },

    severity: {
      type: String,
      enum: ["BENIGN", "LOW", "MEDIUM", "HIGH"],
      required: true,
      index: true
    },

    hybridReason: {
      type: String,
      required: true
    },

    /* ===============================
       FLOW METADATA
    =============================== */

    flowDuration: {
      type: Number, // seconds
      required: true
    },

    /* ===============================
       PER-MODEL PROBABILITIES
    =============================== */

    modelProbabilities: {
      type: Map,
      of: Number,
      required: true
    }
  },
  {
    timestamps: true // createdAt, updatedAt
  }
);

/* ===============================
   INDEX OPTIMIZATION (IMPORTANT)
=============================== */

DetectionLogSchema.index({ timestamp: -1 });
DetectionLogSchema.index({ hybridLabel: 1, severity: 1 });
DetectionLogSchema.index({ destinationIP: 1, dstPort: 1 });

module.exports = mongoose.model("DetectionLog", DetectionLogSchema);
