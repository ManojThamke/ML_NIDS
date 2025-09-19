# Baseline Model Results — Day 17

Trained models: Logistic Regression, Decision Tree

## LogisticRegression

- Accuracy: 0.8814
- Precision: 0.8904
- Recall: 0.4530
- F1-score: 0.6005
- ROC-AUC: 0.9417964513856524

Confusion matrix:

[[2016271, 27917], [274014, 226887]]

Short pros / cons:

- Pros: fast, interpretable, stable baseline.
- Cons: weak on non-linear patterns.

## DecisionTree

- Accuracy: 0.9981
- Precision: 0.9943
- Recall: 0.9959
- F1-score: 0.9951
- ROC-AUC: 0.9995545899810937

Confusion matrix:

[[2041351, 2837], [2061, 498840]]

Short pros / cons:

- Pros: interpretable, captures non-linear interactions.
- Cons: prone to overfitting.

---

Notes: These are baselines. Next step: ensemble models (RF, GBM, etc.)
