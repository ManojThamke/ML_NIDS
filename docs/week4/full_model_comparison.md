# Full Model Comparison

Generated from model metrics in `detection-engine/models/`.

## Table (sorted by F1 desc)

| model_pretty     |   accuracy |   precision |     recall |         f1 |    roc_auc |   train_time_s |   inference_time_s | avg_predict_ms_per_sample   |
|:-----------------|-----------:|------------:|-----------:|-----------:|-----------:|---------------:|-------------------:|:----------------------------|
| Stacked Ensemble |   0.997949 |    0.994576 |   0.995007 |   0.994792 |   0.999957 |     5582.71    |           15.7416  |                             |
| Mlp              |   0.982241 |    0.943185 |   0.968084 |   0.955472 |   0.997129 |     1722.35    |            0.87905 |                             |
| Svm              |   0.888233 |    0.996884 |   0.433435 |   0.604179 |   0.953943 |     1195.62    |           28.8944  |                             |
| Naive Bayes      |   0.358314 |    0.230112 |   0.96364  |   0.37151  |   0.821226 |        1.31955 |          nan       |                             |
| Realtime Rf      |   0.992707 |    0.980233 |   0.982763 | nan        | nan        |      nan       |          nan       |                             |
| Advanced         | nan        |  nan        | nan        | nan        | nan        |      nan       |          nan       |                             |
| Baseline         | nan        |  nan        | nan        | nan        | nan        |      nan       |          nan       |                             |
| Ensemble         | nan        |  nan        | nan        | nan        | nan        |      nan       |          nan       |                             |
| Knn              | nan        |  nan        | nan        | nan        | nan        |      nan       |          nan       |                             |

## Notes

- `avg_predict_ms_per_sample` is preferred for inference speed comparison; when missing it's computed from inference_time_s / n_test_samples if n_test_samples is available in the JSON.
- Missing values are shown as blank. If important metrics are missing, regenerate those model metric files with training scripts.


## Raw files used:
- `detection-engine\models\advanced_metrics.json`
- `detection-engine\models\baseline_metrics.json`
- `detection-engine\models\ensemble_metrics.json`
- `detection-engine\models\knn_metrics.json`
- `detection-engine\models\mlp_metrics.json`
- `detection-engine\models\naive_bayes_metrics.json`
- `detection-engine\models\realtime_rf_metrics.json`
- `detection-engine\models\stacked_ensemble_metrics.json`
- `detection-engine\models\svm_metrics.json`
