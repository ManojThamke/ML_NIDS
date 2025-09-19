# Advanced Models — Day 19

Trained: XGBoost, LightGBM (basic randomized hyperparameter tuning)

## XGBoost

- Best params: {'subsample': 0.8, 'n_estimators': 100, 'max_depth': 9, 'learning_rate': 0.1, 'colsample_bytree': 1.0}
- Accuracy: 0.9962
- Precision: 0.9910
- Recall: 0.9896
- F1-score: 0.9903
- ROC-AUC: 0.9998062952697752
- Train time (s): 411.82
- Inference time (s): 1.3853

Confusion matrix:
[[2039673, 4515], [5215, 495686]]

## LightGBM

- Best params: {'subsample': 1.0, 'num_leaves': 127, 'n_estimators': 100, 'learning_rate': 0.1, 'colsample_bytree': 0.8}
- Accuracy: 0.9966
- Precision: 0.9928
- Recall: 0.9896
- F1-score: 0.9912
- ROC-AUC: 0.9997849326758371
- Train time (s): 270.91
- Inference time (s): 2.0177

Confusion matrix:
[[2040606, 3582], [5191, 495710]]

---

Notes: This was a small-budget tuning run (n_iter=6). Increase n_iter and search ranges for better tuning.
