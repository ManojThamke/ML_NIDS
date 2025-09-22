# Day 23 — K-Nearest Neighbors (KNN) Results

Sample used: 500000 rows

## Tried ks

3, 5, 7

## Best (by F1)

- k = 3
{
  "k": 3,
  "accuracy": 0.994776,
  "precision": 0.9848951162225642,
  "recall": 0.9886183488476078,
  "f1": 0.9867532204077493,
  "roc_auc": 0.9964084164312033,
  "confusion_matrix": [
    [
      100026,
      373
    ],
    [
      280,
      24321
    ]
  ],
  "report": {
    "0": {
      "precision": 0.9972085418619026,
      "recall": 0.9962848235540195,
      "f1-score": 0.9967464686978401,
      "support": 100399.0
    },
    "1": {
      "precision": 0.9848951162225642,
      "recall": 0.9886183488476078,
      "f1-score": 0.9867532204077493,
      "support": 24601.0
    },
    "accuracy": 0.994776,
    "macro avg": {
      "precision": 0.9910518290422334,
      "recall": 0.9924515862008136,
      "f1-score": 0.9917498445527947,
      "support": 125000.0
    },
    "weighted avg": {
      "precision": 0.9947851611886757,
      "recall": 0.994776,
      "f1-score": 0.9947797174883639,
      "support": 125000.0
    }
  },
  "train_time_seconds": 0.9393668174743652,
  "predict_time_seconds": 2.077127695083618,
  "avg_predict_ms_per_sample": 0.016617021560668944,
  "avg_predict_proba_ms_per_sample": 0.016911474227905274,
  "n_train_samples": 375000,
  "n_test_samples": 125000
}

## All results

{
  "k_3": {
    "k": 3,
    "accuracy": 0.994776,
    "precision": 0.9848951162225642,
    "recall": 0.9886183488476078,
    "f1": 0.9867532204077493,
    "roc_auc": 0.9964084164312033,
    "confusion_matrix": [
      [
        100026,
        373
      ],
      [
        280,
        24321
      ]
    ],
    "report": {
      "0": {
        "precision": 0.9972085418619026,
        "recall": 0.9962848235540195,
        "f1-score": 0.9967464686978401,
        "support": 100399.0
      },
      "1": {
        "precision": 0.9848951162225642,
        "recall": 0.9886183488476078,
        "f1-score": 0.9867532204077493,
        "support": 24601.0
      },
      "accuracy": 0.994776,
      "macro avg": {
        "precision": 0.9910518290422334,
        "recall": 0.9924515862008136,
        "f1-score": 0.9917498445527947,
        "support": 125000.0
      },
      "weighted avg": {
        "precision": 0.9947851611886757,
        "recall": 0.994776,
        "f1-score": 0.9947797174883639,
        "support": 125000.0
      }
    },
    "train_time_seconds": 0.9393668174743652,
    "predict_time_seconds": 2.077127695083618,
    "avg_predict_ms_per_sample": 0.016617021560668944,
    "avg_predict_proba_ms_per_sample": 0.016911474227905274,
    "n_train_samples": 375000,
    "n_test_samples": 125000
  },
  "k_5": {
    "k": 5,
    "accuracy": 0.994432,
    "precision": 0.9835349326429063,
    "recall": 0.9882525100605667,
    "f1": 0.9858880778588808,
    "roc_auc": 0.9972158307976393,
    "confusion_matrix": [
      [
        99992,
        407
      ],
      [
        289,
        24312
      ]
    ],
    "report": {
      "0": {
        "precision": 0.9971180981442147,
        "recall": 0.9959461747626969,
        "f1-score": 0.9965317919075144,
        "support": 100399.0
      },
      "1": {
        "precision": 0.9835349326429063,
        "recall": 0.9882525100605667,
        "f1-score": 0.9858880778588808,
        "support": 24601.0
      },
      "accuracy": 0.994432,
      "macro avg": {
        "precision": 0.9903265153935605,
        "recall": 0.9920993424116318,
        "f1-score": 0.9912099348831975,
        "support": 125000.0
      },
      "weighted avg": {
        "precision": 0.9944448225082333,
        "recall": 0.994432,
        "f1-score": 0.9944370238330308,
        "support": 125000.0
      }
    },
    "train_time_seconds": 0.9657561779022217,
    "predict_time_seconds": 2.247755527496338,
    "avg_predict_ms_per_sample": 0.017982044219970704,
    "avg_predict_proba_ms_per_sample": 0.018162660598754883,
    "n_train_samples": 375000,
    "n_test_samples": 125000
  },
  "k_7": {
    "k": 7,
    "accuracy": 0.993712,
    "precision": 0.981286124247201,
    "recall": 0.9868704524206333,
    "f1": 0.9840703660167809,
    "roc_auc": 0.997738614003659,
    "confusion_matrix": [
      [
        99936,
        463
      ],
      [
        323,
        24278
      ]
    ],
    "report": {
      "0": {
        "precision": 0.9967783440888099,
        "recall": 0.9953884002828713,
        "f1-score": 0.9960828873007804,
        "support": 100399.0
      },
      "1": {
        "precision": 0.981286124247201,
        "recall": 0.9868704524206333,
        "f1-score": 0.9840703660167809,
        "support": 24601.0
      },
      "accuracy": 0.993712,
      "macro avg": {
        "precision": 0.9890322341680055,
        "recall": 0.9911294263517523,
        "f1-score": 0.9900766266587806,
        "support": 125000.0
      },
      "weighted avg": {
        "precision": 0.9937293512862225,
        "recall": 0.993712,
        "f1-score": 0.9937187270119191,
        "support": 125000.0
      }
    },
    "train_time_seconds": 0.8960206508636475,
    "predict_time_seconds": 2.4619288444519043,
    "avg_predict_ms_per_sample": 0.019695430755615237,
    "avg_predict_proba_ms_per_sample": 0.01907038688659668,
    "n_train_samples": 375000,
    "n_test_samples": 125000
  }
}

Notes:
- KNN stores the full training set in the model; model size ~ memory to keep training set.
- Inference cost grows with training size; consider approximate nearest neighbor libraries (FAISS, Annoy) or KDTree for speed.
- For realtime detection, KNN may be too slow on large training sets.
