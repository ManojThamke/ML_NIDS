import os
import pandas as pd
from sklearn.model_selection import train_test_split

# ================================
# PATH CONFIG
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "..",
    "data",
    "final",
    "cicids2017_final_scaled.csv"
)

LABEL_COL = "Label"
RANDOM_STATE = 42

# ================================
# LOAD DATASET (ONCE)
# ================================
print("📥 Loading frozen scaled dataset...")
df = pd.read_csv(DATASET_PATH)

X = df.drop(columns=[LABEL_COL])
y = df[LABEL_COL]

print(f"✅ Dataset loaded | Shape: {df.shape}")
print(f"🧮 Features: {X.shape[1]} | Samples: {X.shape[0]}")

# ================================
# SPLIT FUNCTION
# ================================
def get_train_test_split(train_size: float):
    """
    Returns stratified train-test split.
    
    train_size: float (0.4, 0.5, 0.6, 0.7)
    """

    if train_size not in [0.4, 0.5, 0.6, 0.7]:
        raise ValueError("❌ train_size must be one of: 0.4, 0.5, 0.6, 0.7")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        train_size=train_size,
        stratify=y,
        random_state=RANDOM_STATE
    )

    print(
        f"🔀 Split done → Train: {len(X_train)} | Test: {len(X_test)} "
        f"(Train % = {int(train_size*100)})"
    )

    return X_train, X_test, y_train, y_test
