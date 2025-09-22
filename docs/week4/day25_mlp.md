# Day 25 — MLP (Neural Network) Results

Model saved: `detection-engine\models\mlp.pkl`

## Data used
- sample_size_used: 8483628

## Best hyperparameters

{'activation': 'relu', 'alpha': 0.0001, 'hidden_layer_sizes': (50,), 'learning_rate_init': 0.001}

## Metrics (on test set)

- Accuracy: 0.9822
- Precision: 0.9432
- Recall: 0.9681
- F1-score: 0.9555
- ROC-AUC: 0.997129421541303

Confusion matrix:

[[2014978, 29210], [15987, 484914]]

Notes:
- MLP training can be sensitive to scaling; ensure features were scaled (StandardScaler) in preprocessing.
- Early stopping is enabled.
- For production, consider using a smaller MLP or a dedicated deep learning framework for more complex networks.
