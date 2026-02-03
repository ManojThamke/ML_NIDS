import pandas as pd
import numpy as np

def compute_confusion_matrix_vectorized(df: pd.DataFrame) -> dict:
    """
    Computes confusion matrix using vectorized boolean masks.
    Significantly faster than iterrows().
    """
    # 1. Define Proxy Ground Truth (Vectorized)
    # True if attackVotes >= 50% of totalModels
    proxy_truth = (df["attackVotes"] >= (df["totalModels"] / 2))
    
    # 2. Define Predictions
    predictions = (df["finalLabel"] == "ATTACK")

    # 3. Calculate TP, FP, TN, FN using bitwise logic
    tp = (proxy_truth & predictions).sum()
    fp = (~proxy_truth & predictions).sum()
    tn = (~proxy_truth & ~predictions).sum()
    fn = (proxy_truth & ~predictions).sum()

    return {
        "TP": int(tp), "FP": int(fp), 
        "TN": int(tn), "FN": int(fn),
        "False Positive Rate": round(fp / (fp + tn), 4) if (fp + tn) > 0 else 0,
        "False Negative Rate": round(fn / (fn + tp), 4) if (fn + tp) > 0 else 0,
    }