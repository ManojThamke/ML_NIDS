# Week 3 Report — ML_NIDS Project

## ✅ Dataset + Pipeline Review
- Final dataset created and preprocessed.
- Feature engineering with 6–8 common features.
- Models trained: Logistic Regression, Decision Tree, RF, GBM, XGB, LGBM.

## 📊 Model Metrics
| model              | container   |   accuracy |   precision |   recall |       f1 |   train_time |
|:-------------------|:------------|-----------:|------------:|---------:|---------:|-------------:|
| RandomForest       | ensemble    |   0.998097 |    0.994097 | 0.996245 | 0.99517  |      490.653 |
| DecisionTree       | baseline    |   0.998076 |    0.994345 | 0.995885 | 0.995115 |      nan     |
| LightGBM           | advanced    |   0.996553 |    0.992826 | 0.989637 | 0.991229 |      270.914 |
| XGBoost            | advanced    |   0.996177 |    0.990974 | 0.989589 | 0.990281 |      411.82  |
| GBM                | ensemble    |   0.992975 |    0.98594  | 0.978255 | 0.982082 |     2018.22  |
| LogisticRegression | baseline    |   0.881367 |    0.890437 | 0.452958 | 0.600464 |      nan     |

## 🏆 Top Candidates
- **RandomForest** — F1=0.9952, Recall=0.9962, Acc=0.9981
- **DecisionTree** — F1=0.9951, Recall=0.9959, Acc=0.9981
- **LightGBM** — F1=0.9912, Recall=0.9896, Acc=0.9966

## 📌 Next Steps (Week 4 Plan)
- Train remaining 5 models (SVM, KNN, Naive Bayes, MLP, Hybrid Ensemble).
- Compare against Week 3 models.
- Finalize top 3 for deployment.
