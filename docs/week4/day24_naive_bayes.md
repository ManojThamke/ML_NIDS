# Day 24 — Naïve Bayes Results

Model saved: `detection-engine\models\naive_bayes.pkl`

## Metrics (on test set)

- Accuracy: 0.3583
- Precision: 0.2301
- Recall: 0.9636
- F1-score: 0.3715
- ROC-AUC: 0.8212263262920604

Confusion matrix:

[[429254, 1614934], [18213, 482688]]

Notes:
- GaussianNB is extremely fast (training in <1s).
- Works best with normally-distributed features.
- Usually a weaker baseline vs. tree/boosting models.
