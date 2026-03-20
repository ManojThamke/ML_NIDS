<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:ef4444,100:dc2626&height=120&section=header&text=ML-Based%20NIDS&fontSize=40&fontColor=ffffff&fontAlignY=65&animation=fadeIn" width="100%"/>

# 🚨 ML-Based Network Intrusion Detection System

### Real-Time Threat Detection · Machine Learning · MERN Stack

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/></a>
  <a href="https://reactjs.org"><img src="https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black"/></a>
  <a href="https://nodejs.org"><img src="https://img.shields.io/badge/Node.js-Express-339933?style=for-the-badge&logo=nodedotjs&logoColor=white"/></a>
  <a href="https://mongodb.com"><img src="https://img.shields.io/badge/MongoDB-Mongoose-47A248?style=for-the-badge&logo=mongodb&logoColor=white"/></a>
</p>

<p align="center">
  <a href="https://scikit-learn.org"><img src="https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white"/></a>
  <a href="https://xgboost.readthedocs.io"><img src="https://img.shields.io/badge/XGBoost-Ensemble-FF6600?style=for-the-badge"/></a>
  <img src="https://img.shields.io/badge/Detection%20Accuracy-90%25+-brightgreen?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Dataset-CICIDS2017-8B5CF6?style=for-the-badge"/>
</p>

<p align="center">
  <a href="https://github.com/ManojThamke/ML_NIDS/stargazers"><img src="https://img.shields.io/github/stars/ManojThamke/ML_NIDS?style=flat-square&color=yellow&label=⭐ Stars"/></a>
  <a href="https://github.com/ManojThamke/ML_NIDS/forks"><img src="https://img.shields.io/github/forks/ManojThamke/ML_NIDS?style=flat-square&color=green&label=🍴 Forks"/></a>
  <img src="https://img.shields.io/badge/License-Academic-blue?style=flat-square"/>
  <img src="https://img.shields.io/badge/Status-Active-success?style=flat-square"/>
</p>

<br/>

> **An end-to-end cybersecurity solution that uses 10+ supervised ML algorithms and a hybrid stacked ensemble to detect network intrusions in real-time — with live dashboards, attack simulation, and dual logging.**

<br/>

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Highlights](#-key-highlights)
- [Problem Statement](#-problem-statement)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Dataset Details](#-dataset-details)
- [Machine Learning Models](#-machine-learning-models)
- [Real-Time Detection Pipeline](#-real-time-detection-pipeline)
- [Dashboard Features](#-dashboard-features)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [Testing Strategy](#-testing-strategy)
- [Results & Achievements](#-results--achievements)
- [Limitations](#-limitations)
- [Future Scope](#-future-scope)
- [Author](#-author)
- [License](#-license)
- [Contributing](#-contributing)

---

## 🌟 Overview

The **ML-Based Network Intrusion Detection System (NIDS)** is an advanced cybersecurity solution built to **monitor, analyze, and detect malicious network activity in real-time** using Machine Learning.

Unlike traditional signature-based systems, this project trains on **real-world traffic data** and applies a **hybrid stacked ensemble model** to maximize detection accuracy while minimizing false positives. The detection engine feeds into a full **MERN stack dashboard**, forming a complete, production-ready pipeline:

```
Packet Capture  ──►  Feature Extraction  ──►  ML Prediction  ──►  Live Dashboard
```

---

## 🎯 Key Highlights

| Feature | Description |
|---------|-------------|
| 🕵️ **Real-Time Sniffing** | Live packet capture using **Scapy** |
| 🤖 **10+ ML Models** | Classical, advanced, and ensemble algorithms |
| 🧬 **Hybrid Ensemble** | Stacked model: RF + XGBoost + LightGBM → LR meta-classifier |
| 💾 **Dual Logging** | Simultaneous logging to **MongoDB** and **CSV** |
| 📊 **Live Dashboard** | React-based UI with charts, filters, and export |
| 🎭 **Attack Simulation** | UDP Flood, Port Scan, SYN Flood built-in |
| 🎚️ **Tunable Threshold** | Adjustable prediction probability cutoff (default: 0.6) |
| ✅ **High Accuracy** | Achieves **~90%+ detection accuracy** on CICIDS2018 |

---

## 🧠 Problem Statement

Traditional Intrusion Detection Systems carry critical weaknesses that leave networks exposed:

| ❌ Problem | Impact |
|-----------|--------|
| Static rule-based signatures | Cannot adapt to new or evolving attack patterns |
| Zero-day attack blindness | Unknown threats go undetected |
| High false positive rate | Security teams suffer from alert fatigue |

### ✅ How This Project Addresses It

- **ML-based classification** — learns attack *patterns*, not rigid rules
- Trained on **CICIDS2017**, a benchmark dataset with real traffic flows
- **Ensemble stacking** boosts precision and suppresses false alarms
- **Configurable threshold** provides fine-grained sensitivity control

---

## 🏗️ System Architecture

```
          ┌──────────────────────────────────────┐
          │          Network Traffic              │
          │   (Live packets or simulated flows)   │
          └──────────────────┬───────────────────┘
                             ↓
          ┌──────────────────────────────────────┐
          │       Packet Sniffer (Scapy)          │
          │   Captures raw TCP/UDP/ICMP packets   │
          └──────────────────┬───────────────────┘
                             ↓
          ┌──────────────────────────────────────┐
          │      Feature Extraction Engine        │
          │   Computes 6 flow-based features      │
          └──────────────────┬───────────────────┘
                             ↓
          ┌──────────────────────────────────────┐
          │     ML Prediction Engine              │
          │   Stacked Ensemble (RF+XGB+LGBM+LR)   │
          └──────────────────┬───────────────────┘
                             ↓
          ┌──────────────────────────────────────┐
          │       Classification Output           │
          │     🚨 ATTACK  ──or──  ✅ BENIGN     │
          └──────────────────┬───────────────────┘
                             ↓
     ┌───────────────────────────────────────────────┐
     │      Dual Logging System (CSV + MongoDB)       │
     └───────────────────────┬───────────────────────┘
                             ↓
     ┌───────────────────────────────────────────────┐
     │         Node.js + Express REST API             │
     └───────────────────────┬───────────────────────┘
                             ↓
     ┌───────────────────────────────────────────────┐
     │     React Dashboard (Live Visualization UI)    │
     └───────────────────────────────────────────────┘
```

---

## ⚙️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| 🧠 **ML Engine** | Python, scikit-learn, XGBoost, LightGBM, Pandas, NumPy | Model training, prediction, feature processing |
| 🌐 **Networking** | Scapy | Real-time packet sniffing and flow analysis |
| 🖥️ **Backend** | Node.js, Express.js, MongoDB (Mongoose) | REST API, database logging, data persistence |
| 🎨 **Frontend** | React.js, Tailwind CSS, Recharts | Live dashboard, charts, alerts, export |

---

## 📊 Dataset Details

| Property | Value |
|----------|-------|
| **Name** | [CICIDS2018](https://drive.google.com/file/d/1MDGCSzMd-RApt2Q-_xc_M1IjA2HJbDBM/view?usp=drive_link) |
| **Source** | Canadian Institute for Cybersecurity (UNB) |
| **Traffic Types** | BENIGN, DoS, DDoS, PortScan, Brute Force |
| **Label Encoding** | `BENIGN → 0` / All Attacks → `1` |

### 📌 Preprocessing Pipeline

```
1. Drop irrelevant columns  ──►  Flow ID, Timestamp, IP addresses removed
2. Binary label encoding    ──►  BENIGN=0, ATTACK=1
3. Handle nulls & infinities ──►  Missing/inf values replaced or dropped
4. Feature normalization    ──►  MinMaxScaler / StandardScaler applied
5. Feature selection        ──►  6 real-time-compatible features retained
```

### 🔍 Selected Features (Optimized for Real-Time)

These 6 features balance computational speed with classification quality:

| Feature | Description |
|---------|-------------|
| `Destination Port` | Target port number |
| `Flow Duration` | Total flow duration (µs) |
| `Fwd Packet Length Min` | Minimum forward packet size |
| `Packet Length Std` | Standard deviation of packet lengths |
| `Flow IAT Mean` | Mean inter-arrival time of packets |
| `Fwd IAT Mean` | Mean inter-arrival time (forward direction) |

---

## 🤖 Machine Learning Models

### Classical Baselines

| Model | Type | Notes |
|-------|------|-------|
| Logistic Regression | Linear Classifier | Fast, interpretable baseline |
| Decision Tree | Tree-based | Captures non-linear boundaries |
| Naïve Bayes | Probabilistic | Lightweight, works well with limited data |

### Advanced Models

| Model | Type | Notes |
|-------|------|-------|
| Random Forest | Bagging Ensemble | Robust to noise, strong base learner |
| Gradient Boosting | Sequential Boosting | Handles class imbalance well |
| SVM | Margin-based | Effective in high-dimensional space |
| KNN | Instance-based | Simple, good for local patterns |
| XGBoost | Extreme Boosting | Regularized, high-performance |
| LightGBM | Leaf-wise Boosting | Fastest of the ensemble trio |

---

### 🏆 Final Model — Stacked Ensemble (Hybrid)

The production model uses **stacking** — a meta-learning strategy where base model outputs serve as inputs to a final classifier:

```
 ┌─────────────────────────────────────────────────────────────────┐
 │                        BASE LAYER                               │
 │                                                                 │
 │   ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐  │
 │   │ Random Forest │  │   XGBoost     │  │    LightGBM       │  │
 │   └───────┬───────┘  └───────┬───────┘  └────────┬──────────┘  │
 └───────────┼──────────────────┼───────────────────┼─────────────┘
             └──────────────────┼───────────────────┘
                                ↓
 ┌─────────────────────────────────────────────────────────────────┐
 │                       META LAYER                                │
 │           ┌───────────────────────────────────┐                 │
 │           │  Logistic Regression (Combiner)   │                 │
 │           └──────────────────┬────────────────┘                 │
 └──────────────────────────────┼─────────────────────────────────┘
                                ↓
                    🎯 Final Prediction (ATTACK / BENIGN)
```

> **Why stacking?** The meta-learner learns *which* base model to trust for which type of input — correcting individual model errors and achieving higher accuracy than any single model alone.

---

## ⚡ Real-Time Detection Pipeline

```
 Step 1  ─►  Capture raw packets via Scapy
 Step 2  ─►  Maintain per-flow statistics in memory
 Step 3  ─►  Extract 6 feature values per flow
 Step 4  ─►  Pass feature vector to stacked ML model
 Step 5  ─►  Receive attack probability score (0.0 – 1.0)
 Step 6  ─►  Apply threshold (default: 0.6)
              │
              ├──► score ≥ 0.6 → 🚨 ATTACK
              └──► score < 0.6 → ✅ BENIGN
 Step 7  ─►  Log result to CSV + MongoDB
 Step 8  ─►  Push alert to React Dashboard via REST API
```

---

## 📈 Evaluation Metrics

| Metric | What It Measures |
|--------|-----------------|
| **Accuracy** | Overall correct predictions across all classes |
| **Precision** | How many flagged alerts are true attacks (minimizes false positives) |
| **Recall** | How many real attacks are caught (minimizes missed detections) |
| **F1-Score** | Harmonic mean of Precision and Recall |
| **ROC-AUC** | Threshold-independent discrimination ability |

---

## 📊 Dashboard Features

### 🔴 Real-Time Monitoring
- Live **attack alerts** with timestamp, source/destination IPs, and probability score
- Continuously updated benign traffic log

### 📉 Visualizations

| Chart | Purpose |
|-------|---------|
| **Pie Chart** | Attack vs Benign traffic distribution |
| **Line Chart** | Attack frequency trend over time |

### 🗂️ Traffic Log Table

| Column | Description |
|--------|-------------|
| Source IP | Origin address |
| Destination IP | Target address |
| Timestamp | Detection time |
| Prediction | 🚨 ATTACK / ✅ BENIGN |
| Probability | Model confidence score |

### 🔎 Filters & Export
- Search logs by IP address
- Filter by prediction label (ATTACK / BENIGN)
- Time range selection
- Export to **CSV** or **PDF**

---

## 📂 Project Structure

```
ML_NIDS/
│
├── 📁 data/                        # CICIDS2018 dataset files
│   └── *.csv                       # Raw and preprocessed data
│
├── 📁 detection-engine/            # Python ML core
│   ├── realtime_detector.py        # Main detection loop
│   ├── feature_extractor.py        # Flow-based feature computation
│   ├── simulate_attack.py          # Attack traffic generator
│   └── 📁 models/                  # Trained .pkl model files
│       ├── random_forest.pkl
│       ├── xgboost_model.pkl
│       ├── lightgbm_model.pkl
│       └── stacked_ensemble.pkl
│
├── 📁 server/                      # Node.js + Express backend
│   ├── 📁 models/                  # Mongoose schemas
│   ├── 📁 routes/                  # API route handlers
│   └── server.js                   # Entry point (port 5000)
│
├── 📁 client/                      # React frontend
│   ├── 📁 components/              # Reusable UI components
│   ├── 📁 pages/                   # Dashboard pages
│   └── App.js                      # Root component (port 3000)
│
├── 📁 logs/                        # CSV detection logs
├── 📁 docs/                        # Reports & analysis notebooks
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites

Make sure the following are installed and running before setup:

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| Node.js | 16+ |
| MongoDB | Running locally (default port 27017) |

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/ManojThamke/ML_NIDS.git
cd ML_NIDS
```

### Step 2 — Python Environment Setup

```bash
# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install Python dependencies
pip install pandas numpy scikit-learn joblib scapy matplotlib seaborn xgboost lightgbm
```

### Step 3 — Start the Detection Engine

```bash
cd detection-engine
python realtime_detector.py
```

> ⚠️ **Permissions required:** Run as **Administrator** on Windows or with `sudo` on Linux/macOS for raw packet capture.

### Step 4 — Start the Backend Server

```bash
cd server
npm install
npm start
```

> Backend REST API runs at `http://localhost:5000`

### Step 5 — Launch the React Dashboard

```bash
cd client
npm install
npm start
```

> Dashboard accessible at `http://localhost:3000`

---

## 🧪 Testing Strategy

### ✅ Benign Traffic Simulation
- Normal web browsing
- Video/audio streaming traffic

### 🚨 Attack Simulation

Run these commands from within the `detection-engine/` directory:

```bash
python simulate_attack.py --type udp_flood
python simulate_attack.py --type port_scan
python simulate_attack.py --type syn_flood
```

| Attack Type | Method | Description |
|-------------|--------|-------------|
| **UDP Flood** | Scapy UDP packet burst | Overwhelms target with UDP datagrams |
| **Port Scan** | Sequential port probing | Identifies open ports on target host |
| **SYN Flood** | Half-open TCP connections | Exhausts server connection table |

---

## 📌 Results & Achievements

| Metric | Result |
|--------|--------|
| 🎯 Detection Accuracy | **~90%+** on CICIDS2018 test set |
| ⚡ Real-Time Monitoring | ✅ Fully functional |
| 🧬 Ensemble Improvement over Single Models | ✅ Confirmed |
| 📊 Live Dashboard with Alerts | ✅ Operational |
| 📁 Dual Logging (CSV + MongoDB) | ✅ Working |

---

## ⚠️ Limitations

| Limitation | Details |
|-----------|---------|
| **Computational overhead** | Ensemble inference is slower than single models |
| **Feature dependency** | Detection quality is tied to feature engineering quality |
| **Hardware sensitivity** | Performance varies on low-resource machines |
| **Dataset gap** | Trained on CICIDS2017; real-world accuracy may differ |

---

## 🔮 Future Scope

| Enhancement | Description |
|------------|-------------|
| 🧠 **Deep Learning** | LSTM / CNN / Transformer models for sequential traffic analysis |
| ☁️ **Cloud Deployment** | Containerized deployment on AWS / Azure / GCP |
| 🔥 **Auto-Blocking** | Automatic firewall rule injection on confirmed attack detection |
| ⚡ **WebSocket Streaming** | True real-time push to frontend (replacing polling) |
| 📱 **Mobile Dashboard** | React Native monitoring app for on-the-go alerting |
| 🔍 **Explainability** | SHAP / LIME integration for interpretable predictions |
| 🗂️ **Multi-Dataset Support** | Extend to NSL-KDD, UNSW-NB15 for generalization testing |

---

## 👨‍💻 Author

<div align="center">

<br/>

**Manoj Thamke**
<br/>
Final Year B.E. — Information Technology

<br/>

[![GitHub](https://img.shields.io/badge/GitHub-ManojThamke-181717?style=for-the-badge&logo=github)](https://github.com/ManojThamke)
[![Project Repo](https://img.shields.io/badge/Project-ML__NIDS-blue?style=for-the-badge&logo=github)](https://github.com/ManojThamke/ML_NIDS)

<br/>

</div>

---

## 📜 License

This project is developed for **academic and educational purposes**. You are free to reference, study, and build upon it with attribution.

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome!

```
1. 🍴 Fork the repository
2. 🌿 Create a feature branch     →  git checkout -b feature/your-feature
3. 💬 Commit your changes         →  git commit -m 'Add: your feature description'
4. 📤 Push to your branch         →  git push origin feature/your-feature
5. 🔁 Open a Pull Request
```

Please ensure your code follows existing conventions and is well-documented.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:dc2626,100:ef4444&height=80&section=footer" width="100%"/>

**If this project helped you, please consider giving it a ⭐**

[![View on GitHub](https://img.shields.io/badge/View%20on-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/ManojThamke/ML_NIDS)

</div>
