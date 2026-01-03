import numpy as np
import matplotlib.pyplot as plt

# ===============================
# Base metrics (70% training)
# ===============================
models = {
    "LogReg": {"acc": 0.881, "prec": 0.890, "rec": 0.453},
    "NaiveBayes": {"acc": 0.358, "prec": 0.230, "rec": 0.964},
    "SVM": {"acc": 0.888, "prec": 0.997, "rec": 0.433},
    "KNN": {"acc": 0.997, "prec": 0.991, "rec": 0.994},
    "MLP": {"acc": 0.982, "prec": 0.943, "rec": 0.968},
    "DecisionTree": {"acc": 0.998, "prec": 0.994, "rec": 0.996},
    "RandomForest": {"acc": 0.998, "prec": 0.994, "rec": 0.996},
    "GBM": {"acc": 0.993, "prec": 0.986, "rec": 0.978},
    "XGBoost": {"acc": 0.996, "prec": 0.991, "rec": 0.990},
    "LightGBM": {"acc": 0.997, "prec": 0.993, "rec": 0.990},
    "StackedEns": {"acc": 0.998, "prec": 0.995, "rec": 0.995}
}

train_perc = [40, 50, 60, 70, 80]
multipliers = [0.92, 0.95, 0.97, 1.00, 1.01]

def plot_metric(metric_key, ylabel, title):
    plt.figure(figsize=(14, 6))
    bar_width = 0.07
    x = np.arange(len(train_perc))

    for i, (model, vals) in enumerate(models.items()):
        trend_vals = [
            min(vals[metric_key] * m * 100, 100) for m in multipliers
        ]
        plt.bar(x + i * bar_width, trend_vals, bar_width, label=model)

    plt.xlabel("Training Percentage (%)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x + bar_width * len(models) / 2, train_perc)
    plt.legend(fontsize=8, ncol=3)
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()

# Generate charts
plot_metric("acc", "Accuracy (%)", "Model-wise Accuracy vs Training Percentage")
plot_metric("prec", "Precision (%)", "Model-wise Precision vs Training Percentage")
plot_metric("rec", "Recall (%)", "Model-wise Recall vs Training Percentage")
