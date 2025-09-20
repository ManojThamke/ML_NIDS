# Model Comparison — Part 1 (Day 20)

This table aggregates available metrics (Accuracy, Precision, Recall, F1, Train time). Missing entries mean the training script did not produce metrics or file is not present.

| model              |   accuracy |   precision |   recall |       f1 |   train_time | note   |
|:-------------------|-----------:|------------:|---------:|---------:|-------------:|:-------|
| LogisticRegression |   0.881367 |    0.890437 | 0.452958 | 0.600464 |      nan     |        |
| DecisionTree       |   0.998076 |    0.994345 | 0.995885 | 0.995115 |      nan     |        |
| RandomForest       |   0.998097 |    0.994097 | 0.996245 | 0.99517  |      490.653 |        |
| GBM                |   0.992975 |    0.98594  | 0.978255 | 0.982082 |     2018.22  |        |
| XGBoost            |   0.996177 |    0.990974 | 0.989589 | 0.990281 |      411.82  |        |
| LightGBM           |   0.996553 |    0.992826 | 0.989637 | 0.991229 |      270.914 |        |

**Notes**:
- Accuracy can be misleading on imbalanced datasets; focus on Recall / Precision / F1 for attack detection.
- Train time measured as wall-clock seconds during training run (may vary by machine).
