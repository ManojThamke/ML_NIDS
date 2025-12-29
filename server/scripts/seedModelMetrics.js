const mongoose = require("mongoose");
const ModelMetric = require("../models/ModelMetric");
require("dotenv").config();

const data = [
  {
    modelName: "Random Forest",
    accuracy: 0.9981,
    precision: 0.9940,
    recall: 0.9962,
    f1: 0.9951,
    roc_auc: 0.9997
  },
  {
    modelName: "XGBoost",
    accuracy: 0.9961,
    precision: 0.9910,
    recall: 0.9896,
    f1: 0.9902,
    roc_auc: 0.9998
  },
  {
    modelName: "LightGBM",
    accuracy: 0.9965,
    precision: 0.9928,
    recall: 0.9896,
    f1: 0.9912,
    roc_auc: 0.9997
  },
  {
    modelName: "MLP",
    accuracy: 0.9822,
    precision: 0.9431,
    recall: 0.9680,
    f1: 0.9554,
    roc_auc: 0.9971
  },
  {
    modelName: "Naive Bayes",
    accuracy: 0.3583,
    precision: 0.2301,
    recall: 0.9636,
    f1: 0.3715,
    roc_auc: 0.8212
  },
  {
    modelName: "Stacked Ensemble",
    accuracy: 0.9979,
    precision: 0.9945,
    recall: 0.9950,
    f1: 0.9947,
    roc_auc: 0.9999
  }
];

async function seed() {
  await mongoose.connect(process.env.MONGO_URI);
  await ModelMetric.deleteMany();
  await ModelMetric.insertMany(data);
  console.log("✅ Model metrics seeded");
  process.exit();
}

seed();
