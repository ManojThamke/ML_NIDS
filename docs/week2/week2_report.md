# Week 2 Report — Real-Time Baseline Detector

## Achievements
- Implemented real-time packet sniffer using Scapy (Day 8).
- Developed feature extractor for 4 baseline features:
  - Destination Port
  - Flow Duration
  - Fwd Packet Length Min
  - Packet Length Std
- Built real-time detector (Day 10) using Random Forest (baseline model).
- Created attack simulator for UDP/TCP floods (Day 11).
- Added realtime logger to save predictions into CSV (Day 12).
- Performed threshold tuning experiments (Day 13) — observed probabilities mostly low, highlighting need for richer features.

## Architecture
![Architecture Diagram](docs\Diagrams\System Achitecture.jpg)

**Pipeline:**
Sniffer → Feature Extractor → ML Model (Random Forest) → Prediction → Logger (CSV).

## Observations
- Baseline detector correctly processed real packets and produced predictions.
- Most predictions = BENIGN with low probabilities (0.00–0.04).
- Attack traffic not always flagged due to limited features and class imbalance.

## Next Steps (Week 3)
- Merge CICIDS dataset with benign traffic captures.
- Expand feature set (30+).
- Train multiple ML models (LogReg, DT, RF, XGB, LGBM, etc.).
- Compare results and select top candidates.
