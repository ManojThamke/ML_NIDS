<div align="center">

# 🚨 ML-Based Network Intrusion Detection System

### Real-Time Threat Detection using Machine Learning & MERN Stack

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![Node.js](https://img.shields.io/badge/Node.js-Express-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)](https://nodejs.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-Mongoose-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-Ensemble-FF6600?style=for-the-badge)](https://xgboost.readthedocs.io)

[![License](https://img.shields.io/badge/License-Academic-blue?style=flat-square)](https://github.com/ManojThamke/ML_NIDS)
[![GitHub Stars](https://img.shields.io/github/stars/ManojThamke/ML_NIDS?style=flat-square&color=yellow)](https://github.com/ManojThamke/ML_NIDS/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/ManojThamke/ML_NIDS?style=flat-square&color=green)](https://github.com/ManojThamke/ML_NIDS/forks)
[![Accuracy](https://img.shields.io/badge/Detection%20Accuracy-90%25+-brightgreen?style=flat-square)](https://github.com/ManojThamke/ML_NIDS)
[![Dataset](https://img.shields.io/badge/Dataset-CICIDS2017-purple?style=flat-square)](https://www.unb.ca/cic/datasets/ids-2017.html)

</div>

---

## 📋 Table of Contents

- [Project Description](#-project-description)
- [Key Highlights](#-key-highlights)
- [Problem Statement](#-problem-statement)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Dataset Details](#-dataset-details)
- [ML Models](#-machine-learning-models)
- [Real-Time Pipeline](#-real-time-detection-pipeline)
- [Dashboard Features](#-dashboard-features)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [Testing Strategy](#-testing-strategy)
- [Results](#-results--achievements)
- [Future Scope](#-future-scope)
- [Author](#-author)

---

## 🌟 Project Description

The **ML-Based Network Intrusion Detection System (NIDS)** is an advanced cybersecurity solution designed to **monitor, analyze, and detect malicious network activities in real-time** using Machine Learning.

Unlike traditional rule-based systems, this project leverages **10+ supervised learning algorithms** and a **hybrid stacked ensemble model** to improve detection accuracy and reduce false positives.

The system integrates a **Python-based detection engine** with a **MERN stack dashboard**, providing a complete end-to-end solution:

```
Packet Capture  →  Feature Extraction  →  ML Prediction  →  Live Dashboard
```

---

## 🎯 Key Highlights

| Feature | Description |
|--------|-------------|
| 🕵️ Real-Time Sniffing | Live packet capture using **Scapy** |
| 🤖 10+ ML Models | Classical, advanced, and ensemble algorithms |
| 🧬 Hybrid Ensemble | Stacked model: RF + XGBoost + LightGBM + LR meta |
| 💾 Dual Logging | Simultaneous logging to **MongoDB** and **CSV** |
| 📊 Live Dashboard | React-based UI with charts, filters, and export |
| 🎭 Attack Simulation | UDP Flood, Port Scan, SYN Flood testing |
| 🎚️ Configurable Threshold | Adjustable prediction probability cutoff |
| ✅ High Accuracy | Achieves **~90%+ detection accuracy** |

---

## 🧠 Problem Statement

Traditional Intrusion Detection Systems suffer from critical limitations:

- ❌ Depend on **static, rule-based signatures**
- ❌ Fail to detect **unknown (zero-day) attacks**
- ❌ Generate excessive **false positive alerts**

### ✅ How This Project Solves It

- Uses **ML-based classification** — learns attack patterns, not just rules
- Trained on **real-world traffic data** (CICIDS2017 dataset)
- Applies **ensemble learning** to boost precision and reduce noise

---

## 🏗️ System Architecture

```
          ┌────────────────────────────┐
          │       Network Traffic      │
          └────────────┬───────────────┘
                       ↓
          ┌────────────────────────────┐
          │   Packet Sniffer (Scapy)   │
          └────────────┬───────────────┘
                       ↓
          ┌────────────────────────────┐
          │  Feature Extraction Engine │
          │  (Flow-based calculations) │
          └────────────┬───────────────┘
                       ↓
          ┌────────────────────────────┐
          │   ML Models / Ensemble     │
          │  (RF, XGB, LGBM, SVM...)   │
          └────────────┬───────────────┘
                       ↓
          ┌────────────────────────────┐
          │      Prediction Engine     │
          │   ATTACK 🚨 / BENIGN ✅    │
          └────────────┬───────────────┘
                       ↓
     ┌─────────────────────────────────────┐
     │    Logging System (CSV + MongoDB)   │
     └────────────┬────────────────────────┘
                  ↓
     ┌─────────────────────────────────────┐
     │   Node.js API  (Express Backend)    │
     └────────────┬────────────────────────┘
                  ↓
     ┌─────────────────────────────────────┐
     │  React Dashboard (Visualization UI) │
     └─────────────────────────────────────┘
```

---

## ⚙️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| 🧠 ML Engine | Python, scikit-learn, XGBoost, LightGBM, Pandas, NumPy | Model training, prediction, feature processing |
| 🌐 Network | Scapy | Real-time packet sniffing & flow analysis |
| 🖥️ Backend | Node.js, Express.js, MongoDB (Mongoose) | REST API, database logging |
| 🎨 Frontend | React.js, Tailwind CSS, Recharts | Live dashboard, charts, alerts |

---

## 📊 Dataset Details

| Property | Value |
|----------|-------|
| **Dataset** | [CICIDS2017](https://www.unb.ca/cic/datasets/ids-2017.html) |
| **Source** | Canadian Institute for Cybersecurity |
| **Traffic Types** | BENIGN, DoS, DDoS, PortScan, Brute Force |
| **Label Encoding** | `BENIGN → 0` / `ATTACK → 1` |

### 📌 Data Preprocessing Steps

1. Removed irrelevant columns (Flow ID, Timestamp, IPs)
2. Encoded binary labels (BENIGN=0, ATTACK=1)
3. Handled missing/infinite values
4. Normalized feature values
5. Selected 6 real-time compatible features

### 🔍 Features Used (Optimized for Real-Time)

```
✦ Destination Port        ✦ Flow Duration
✦ Fwd Packet Length Min   ✦ Packet Length Std
✦ Flow IAT Mean           ✦ Fwd IAT Mean
```

> These features enable fast computation while maintaining strong classification performance.

---

## 🤖 Machine Learning Models

### Classical Models
| Model | Type |
|-------|------|
| Logistic Regression | Linear Classifier |
| Decision Tree | Tree-based |
| Naïve Bayes | Probabilistic |

### Advanced Models
| Model | Type |
|-------|------|
| Random Forest | Bagging Ensemble |
| Gradient Boosting | Boosting |
| SVM | Margin-based |
| KNN | Instance-based |
| XGBoost | Extreme Boosting |
| LightGBM | Gradient Boosting |

### 🏆 Final Model — Stacked Ensemble (Hybrid)

```
  Base Layer:  [ Random Forest ]  [ XGBoost ]  [ LightGBM ]
                        ↓               ↓             ↓
  Meta Layer:      [ Logistic Regression (Meta-Classifier) ]
                                  ↓
                         Final Prediction 🎯
```

> Stacking combines the strengths of multiple models and allows the meta-learner to correct individual model errors — resulting in higher accuracy and fewer false positives.

---

## ⚡ Real-Time Detection Pipeline

```
Step 1 → Capture packets using Scapy
Step 2 → Maintain flow-based statistics
Step 3 → Extract 6 key features dynamically
Step 4 → Pass feature vector to ML model
Step 5 → Get attack probability score
Step 6 → Apply threshold (default: 0.6)
Step 7 → Log result → CSV + MongoDB
Step 8 → Push alert to React Dashboard
```

---

## 📈 Evaluation Metrics

| Metric | Focus |
|--------|-------|
| Accuracy | Overall correct predictions |
| Precision | Minimizing False Positives |
| Recall | Capturing True Positives |
| F1-Score | Precision-Recall balance |
| ROC-AUC | Threshold-independent performance |

---

## 📊 Dashboard Features

### 🔴 Real-Time Monitoring
- Live **attack alerts** with timestamp and probability
- Benign traffic log with source/destination IPs

### 📉 Visualizations
- **Pie Chart** — Attack vs Benign traffic ratio
- **Line Chart** — Attack trends over time

### 🗂️ Data Table

| Column | Description |
|--------|-------------|
| Source IP | Origin address |
| Destination IP | Target address |
| Timestamp | Detection time |
| Prediction | ATTACK / BENIGN |
| Probability | Confidence score |

### 🔎 Filters & Export
- Search by IP address
- Filter by attack/benign status
- Time range selection
- Export logs as **CSV / PDF**

---

## 📂 Project Structure

```
ML_NIDS/
│
├── 📁 data/                    # CICIDS2017 dataset files
│
├── 📁 detection-engine/        # Python ML + real-time core
│   ├── realtime_detector.py    # Main detection loop
│   ├── feature_extractor.py    # Flow-based feature computation
│   ├── simulate_attack.py      # Attack traffic generator
│   └── 📁 models/              # Trained .pkl model files
│
├── 📁 server/                  # Node.js + Express backend
│   ├── 📁 models/              # Mongoose schemas
│   ├── 📁 routes/              # API route handlers
│   └── server.js               # Entry point
│
├── 📁 client/                  # React frontend
│   ├── 📁 components/          # Reusable UI components
│   ├── 📁 pages/               # Dashboard pages
│   └── App.js                  # Root component
│
├── 📁 logs/                    # CSV detection logs
├── 📁 docs/                    # Reports & analysis notebooks
└── README.md
```

---

## 🚀 Installation & Setup

**Prerequisites:** Python 3.10+ · Node.js 16+ · MongoDB running locally

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/ManojThamke/ML_NIDS.git
cd ML_NIDS
```

### Step 2 — Python Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install pandas numpy scikit-learn joblib scapy matplotlib seaborn xgboost lightgbm
```

### Step 3 — Run Detection Engine

```bash
cd detection-engine
python realtime_detector.py
```

> ⚠️ Run as **Administrator** (Windows) or with `sudo` (Linux/macOS) for packet capture permissions.

### Step 4 — Start Backend Server

```bash
cd server
npm install
npm start
```

> API runs at `http://localhost:5000`

### Step 5 — Launch React Dashboard

```bash
cd client
npm install
npm start
```

> Dashboard opens at `http://localhost:3000`

---

## 🧪 Testing Strategy

### ✅ Benign Traffic
- Normal web browsing simulation
- Video streaming traffic

### 🚨 Attack Simulation

```bash
# Run from detection-engine/
python simulate_attack.py --type udp_flood
python simulate_attack.py --type port_scan
python simulate_attack.py --type syn_flood
```

| Attack Type | Method |
|-------------|--------|
| UDP Flood | Scapy UDP packet burst |
| Port Scan | Sequential port probing |
| SYN Flood | Half-open TCP connections |

---

## 📌 Results & Achievements

| Metric | Result |
|--------|--------|
| 🎯 Detection Accuracy | **~90%+** |
| ⚡ Real-Time Monitoring | ✅ Working |
| 🧬 Ensemble Improvement | ✅ Confirmed |
| 📊 Live Dashboard Alerts | ✅ Functional |

---

## ⚠️ Limitations

- Ensemble models have higher computational overhead
- Detection quality depends on quality of feature engineering
- Performance varies based on available system hardware
- Tested on CICIDS2017; real-world accuracy may differ

---

## 🔮 Future Scope

| Enhancement | Description |
|------------|-------------|
| 🧠 Deep Learning | LSTM / CNN for sequential traffic analysis |
| ☁️ Cloud Deployment | AWS / Azure containerized deployment |
| 🔥 Auto-Blocking | Firewall rule injection on attack detection |
| ⚡ WebSocket Streaming | True real-time push to frontend |
| 📱 Mobile Dashboard | React Native monitoring app |

---

## 👨‍💻 Author

<div align="center">

**Manoj Thamke**  
Final Year B.E. — Information Technology

[![GitHub](https://img.shields.io/badge/GitHub-ManojThamke-181717?style=for-the-badge&logo=github)](https://github.com/ManojThamke)
[![Repo](https://img.shields.io/badge/Project-ML__NIDS-blue?style=for-the-badge&logo=github)](https://github.com/ManojThamke/ML_NIDS)

</div>

---

## 📜 License

This project is developed for **academic and educational purposes**.

---

## 🤝 Contributing

Contributions are welcome!

1. 🍴 Fork the repository
2. 🌿 Create a feature branch: `git checkout -b feature/improvement`
3. 💬 Commit your changes: `git commit -m 'Add feature'`
4. 📤 Push to branch: `git push origin feature/improvement`
5. 🔁 Open a Pull Request

---

<div align="center">

⭐ **Star this repo if you found it useful!** ⭐

[![View on GitHub](https://img.shields.io/badge/View%20on-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/ManojThamke/ML_NIDS)

</div>
