# Day 26 — Stacked Ensemble Results

Model saved: `detection-engine\models\stacked_ensemble.pkl`

Sample used: 8483628 rows

Base estimators:

- rf
- xgb
- lgb

## Metrics (test set)

- Accuracy: 0.9979
- Precision: 0.9946
- Recall: 0.9950
- F1-score: 0.9948
- ROC-AUC: 0.9999573641442339

Confusion matrix:

[[1701225, 2265], [2084, 415333]]

Notes:
- Stacking combines strengths of base learners. Training time = sum of base learners (with CV) + meta training.
- If XGBoost/LGBM missing, script falls back to available learners.
- For production, consider saving individual best-performing base models and using a lighter meta model.
