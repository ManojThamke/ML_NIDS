# Week 1 Report - ML_NIDS Project

## ✅ Day 1: Environment & Setup
- Installed Python, Node.js, MongoDB, React.
- Created project structure:


- Created virtual environment `venv/` and installed dependencies (pandas, numpy, scikit-learn, scapy, matplotlib, seaborn, fpdf, requests).

---

## ✅ Day 2: Dataset Collection
- Downloaded full CICIDS2017 dataset (8 CSV files).
- Stored in `data/cicids2017/`.
- Merged into single file `cicids2017_full.csv`.

---

## ✅ Day 3: Dataset Cleaning
- Dropped irrelevant columns (Flow ID, Source IP, Destination IP, Timestamp).
- Normalized labels: BENIGN → 0, Attacks → 1.
- Removed NaN/Inf values.
- Saved cleaned dataset as `cicids2017_cleaned.csv`.

---

## ✅ Day 4: Exploratory Data Analysis
- Plotted **class distribution** (Benign vs Attack).
- Plotted histograms for 4 features.
- Generated correlation heatmap.
- Created EDA report: `docs/week1/eda/eda_report.pdf`.

---

## ✅ Day 5: Baseline Features
- Selected 4 baseline features:
1. Destination Port  
2. Flow Duration  
3. Fwd Packet Length Min  
4. Packet Length Std  
- Extracted with label → `baseline_train.csv` + `baseline_test.csv`.

---

## ✅ Day 6: Baseline Model Training
- Trained Random Forest (100 trees).
- Metrics:
- "accuracy": 0.9927071312633861,
  "precision": 0.9802327387423984,
  "recall": 0.9827630609641426,
  "f1-score": 0.9814962690472986,
  "confusion_matrix": [
    [
      678087,
      3309
    ],
    [
      2878,
      164089
    ]
  ]
- Saved model: `detection-engine/models/realtime_rf.pkl`
- Saved metrics: `detection-engine/models/realtime_rf_metrics.json`

---

## 📌 Week 1 Summary
- Environment ready ✅  
- Dataset cleaned & analyzed ✅  
- Baseline Random Forest trained ✅  
- Documentation report created ✅  

Next: **Week 2 → Real-Time Sniffer + Baseline Detector**
