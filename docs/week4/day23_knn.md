# Day 23 — K-Nearest Neighbors (KNN) Results

Sample used: 8483628 rows

## Tried ks

3, 5, 7

## Best (by F1)

- k = 3
{
  "k": 3,
  "accuracy": 0.9970474895881809,
  "precision": 0.9913596328740275,
  "recall": 0.9936586195579001,
  "f1": 0.9925077949083635,
  "roc_auc": 0.9987935113447334,
  "confusion_matrix": [
    [
      1699875,
      3615
    ],
    [
      2647,
      414770
    ]
  ],
  "report": {
    "0": {
      "precision": 0.9984452476972397,
      "recall": 0.9978778859870031,
      "f1-score": 0.9981614862190739,
      "support": 1703490.0
    },
    "1": {
      "precision": 0.9913596328740275,
      "recall": 0.9936586195579001,
      "f1-score": 0.9925077949083635,
      "support": 417417.0
    },
    "accuracy": 0.9970474895881809,
    "macro avg": {
      "precision": 0.9949024402856337,
      "recall": 0.9957682527724516,
      "f1-score": 0.9953346405637187,
      "support": 2120907.0
    },
    "weighted avg": {
      "precision": 0.9970507235230724,
      "recall": 0.9970474895881809,
      "f1-score": 0.9970487797845895,
      "support": 2120907.0
    }
  },
  "train_time_seconds": 31.523873567581177,
  "predict_time_seconds": 113.13760113716125,
  "avg_predict_ms_per_sample": 0.053343970828122714,
  "avg_predict_proba_ms_per_sample": 0.054723429599281365,
  "n_train_samples": 6362721,
  "n_test_samples": 2120907
}

## All results

{
  "k_3": {
    "k": 3,
    "accuracy": 0.9970474895881809,
    "precision": 0.9913596328740275,
    "recall": 0.9936586195579001,
    "f1": 0.9925077949083635,
    "roc_auc": 0.9987935113447334,
    "confusion_matrix": [
      [
        1699875,
        3615
      ],
      [
        2647,
        414770
      ]
    ],
    "report": {
      "0": {
        "precision": 0.9984452476972397,
        "recall": 0.9978778859870031,
        "f1-score": 0.9981614862190739,
        "support": 1703490.0
      },
      "1": {
        "precision": 0.9913596328740275,
        "recall": 0.9936586195579001,
        "f1-score": 0.9925077949083635,
        "support": 417417.0
      },
      "accuracy": 0.9970474895881809,
      "macro avg": {
        "precision": 0.9949024402856337,
        "recall": 0.9957682527724516,
        "f1-score": 0.9953346405637187,
        "support": 2120907.0
      },
      "weighted avg": {
        "precision": 0.9970507235230724,
        "recall": 0.9970474895881809,
        "f1-score": 0.9970487797845895,
        "support": 2120907.0
      }
    },
    "train_time_seconds": 31.523873567581177,
    "predict_time_seconds": 113.13760113716125,
    "avg_predict_ms_per_sample": 0.053343970828122714,
    "avg_predict_proba_ms_per_sample": 0.054723429599281365,
    "n_train_samples": 6362721,
    "n_test_samples": 2120907
  },
  "k_5": {
    "k": 5,
    "accuracy": 0.9961346725716875,
    "precision": 0.9894413786009707,
    "recall": 0.9909347247476744,
    "f1": 0.9901874886290731,
    "roc_auc": 0.9991485889848291,
    "confusion_matrix": [
      [
        1699076,
        4414
      ],
      [
        3784,
        413633
      ]
    ],
    "report": {
      "0": {
        "precision": 0.9977778560774226,
        "recall": 0.9974088488925676,
        "f1-score": 0.9975933183612958,
        "support": 1703490.0
      },
      "1": {
        "precision": 0.9894413786009707,
        "recall": 0.9909347247476744,
        "f1-score": 0.9901874886290731,
        "support": 417417.0
      },
      "accuracy": 0.9961346725716875,
      "macro avg": {
        "precision": 0.9936096173391966,
        "recall": 0.994171786820121,
        "f1-score": 0.9938904034951845,
        "support": 2120907.0
      },
      "weighted avg": {
        "precision": 0.9961371488616946,
        "recall": 0.9961346725716875,
        "f1-score": 0.996135772495619,
        "support": 2120907.0
      }
    },
    "train_time_seconds": 31.953330993652344,
    "predict_time_seconds": 128.57012343406677,
    "avg_predict_ms_per_sample": 0.06062034942317922,
    "avg_predict_proba_ms_per_sample": 0.059144700443490544,
    "n_train_samples": 6362721,
    "n_test_samples": 2120907
  },
  "k_7": {
    "k": 7,
    "accuracy": 0.9967636487597051,
    "precision": 0.9914907065778227,
    "recall": 0.992070279840064,
    "f1": 0.9917804085366876,
    "roc_auc": 0.9993467701007335,
    "confusion_matrix": [
      [
        1699936,
        3554
      ],
      [
        3310,
        414107
      ]
    ],
    "report": {
      "0": {
        "precision": 0.9980566518283325,
        "recall": 0.9979136948265033,
        "f1-score": 0.9979851682079269,
        "support": 1703490.0
      },
      "1": {
        "precision": 0.9914907065778227,
        "recall": 0.992070279840064,
        "f1-score": 0.9917804085366876,
        "support": 417417.0
      },
      "accuracy": 0.9967636487597051,
      "macro avg": {
        "precision": 0.9947736792030776,
        "recall": 0.9949919873332836,
        "f1-score": 0.9948827883723073,
        "support": 2120907.0
      },
      "weighted avg": {
        "precision": 0.9967644041396633,
        "recall": 0.9967636487597051,
        "f1-score": 0.9967640056733652,
        "support": 2120907.0
      }
    },
    "train_time_seconds": 31.39974617958069,
    "predict_time_seconds": 130.33882236480713,
    "avg_predict_ms_per_sample": 0.06145428458900232,
    "avg_predict_proba_ms_per_sample": 0.05975445903377098,
    "n_train_samples": 6362721,
    "n_test_samples": 2120907
  }
}

Notes:
- KNN stores the full training set in the model; model size ~ memory to keep training set.
- Inference cost grows with training size; consider approximate nearest neighbor libraries (FAISS, Annoy) or KDTree for speed.
- For realtime detection, KNN may be too slow on large training sets.
