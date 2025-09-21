# Day 22 — SVM (RBF) Results

Model saved: `detection-engine\models\svm.pkl`

## Data used
- sample_size_used: 100000
- grid_used: small
- approx_used: False

## Best hyperparameters

{'C': 1.0, 'gamma': 'scale', 'kernel': 'rbf'}

## Metrics (on test set)

- Accuracy: 0.8882
- Precision: 0.9969
- Recall: 0.4334
- F1-score: 0.6042
- ROC-AUC: 0.95394335527695

Confusion matrix:

[[24088, 8], [3345, 2559]]

Notes:
- Kernel: RBF (or approximated if --approx). Tuned C and gamma on selected grid.
- SVMs can be slow on large datasets; for reproducibility we used stratified subsampling when requested.
python detection-engine\train_svm.py --sample 100000 --n_jobs 2 --grid small