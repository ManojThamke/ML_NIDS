# Week 4 Wrap-Up Report

📅 **Day 28 Deliverable** — docs/week4/week4_report.md

## ✅ Top 3 Models Selected

- **Stacked_Ensemble**
  - Accuracy: 0.9979
  - F1-score: 0.9948
  - Inference speed: 15.7416410446167

- **Mlp**
  - Accuracy: 0.9822
  - F1-score: 0.9555
  - Inference speed: 0.8790497779846191

- **Svm**
  - Accuracy: 0.8882
  - F1-score: 0.6042
  - Inference speed: 28.89443826675415

## 📌 Why These Models?
- Highest accuracy and F1-scores among all 10 models.
- Balanced trade-off between detection performance and inference speed.
- Reliable for real-time deployment compared to slower models like full SVM.

## 🚀 Feature Set Frozen for Deployment
We will use the **final engineered feature set (8 features)** from Week 3 preprocessing:
- Destination Port
- Flow Duration
- Fwd Packet Length Min
- Packet Length Std
- Flow IAT Mean
- Fwd IAT Mean
- (plus 2 extended features selected in Week 3)

This frozen set ensures **consistency** between offline training and real-time deployment.

## 📂 Metrics Files Used
- advanced_metrics.json
- baseline_metrics.json
- ensemble_metrics.json
- knn_metrics.json
- mlp_metrics.json
- naive_bayes_metrics.json
- realtime_rf_metrics.json
- stacked_ensemble_metrics.json
- svm_metrics.json
