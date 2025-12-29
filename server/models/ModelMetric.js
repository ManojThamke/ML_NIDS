const mongoose = require("mongoose");

const ModelMetricSchema = new mongoose.Schema(
  {
    modelName: {
      type: String,
      required: true,
      unique: true
    },

    accuracy: {
      type: Number,
      required: true
    },

    precision: Number,
    recall: Number,
    f1: Number,
    roc_auc: Number,

    trainTimeSeconds: Number,
    inferenceTimeSeconds: Number,

    datasetSize: Number,

    evaluatedOn: {
      type: String,
      default: "Offline Dataset"
    }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model("ModelMetric", ModelMetricSchema);
