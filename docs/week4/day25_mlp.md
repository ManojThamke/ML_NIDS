# Day 25 — MLP (Neural Network) Results

Model saved: `detection-engine\models\mlp.pkl`

## Data used
- sample_size_used: 100000

## Best hyperparameters

{'activation': 'tanh', 'alpha': 0.0001, 'hidden_layer_sizes': (100, 50), 'learning_rate_init': 0.01}

## Metrics (on test set)

- Accuracy: 0.9811
- Precision: 0.9514
- Recall: 0.9524
- F1-score: 0.9519
- ROC-AUC: 0.9957651925327147

Confusion matrix:

[[23809, 287], [281, 5623]]

Notes:
- MLP training can be sensitive to scaling; ensure features were scaled (StandardScaler) in preprocessing.
- Early stopping is enabled.
- For production, consider using a smaller MLP or a dedicated deep learning framework for more complex networks.

