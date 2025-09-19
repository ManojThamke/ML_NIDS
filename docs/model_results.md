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

- Pros: fast, interpretable coefficients, good baseline for linear separability.
- Cons: limited if features are not linearly separable; sensitive to collinearity.

## DecisionTree

- Accuracy: 0.9981
- Precision: 0.9943
- Recall: 0.9959
- F1-score: 0.9951
- ROC-AUC: 0.9995545899810937

Confusion matrix:

[[2041351, 2837], [2061, 498840]]

Short pros / cons:

- Pros: interpretable rules, captures non-linear interactions, no scaling required.
- Cons: prone to overfitting; unstable to small data changes.

---

Notes:
- These are baseline models. Next step: train stronger ensemble models (RF, XGB, LGBM) and compare.
