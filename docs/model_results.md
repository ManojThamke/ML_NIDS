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


# Ensemble Models — Day 18

Trained models: RandomForest, GradientBoosting (sklearn)

## RandomForest

- Accuracy: 0.9981
- Precision: 0.9941
- Recall: 0.9962
- F1-score: 0.9952
- ROC-AUC: 0.9997794613905018
- Train time (s): 490.65
- Inference time (s): 7.7072

Confusion matrix:

[[2041225, 2963], [1881, 499020]]

Short notes (speed vs accuracy):

- RandomForest: typically slower to train, fast-ish inference with many trees; good accuracy and robustness.
- GBM: often higher accuracy per-tree, slower training; inference comparable to RF depending on tree count.

## GBM

- Accuracy: 0.9930
- Precision: 0.9859
- Recall: 0.9783
- F1-score: 0.9821
- ROC-AUC: 0.9993104562407443
- Train time (s): 2018.22
- Inference time (s): 7.4464

Confusion matrix:

[[2037200, 6988], [10892, 490009]]

Short notes (speed vs accuracy):

- RandomForest: typically slower to train, fast-ish inference with many trees; good accuracy and robustness.
- GBM: often higher accuracy per-tree, slower training; inference comparable to RF depending on tree count.

---
