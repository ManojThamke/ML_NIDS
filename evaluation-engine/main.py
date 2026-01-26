from db.mongo_client import MongoDBClient
from loaders.load_detection_logs import load_detection_logs
from metrics.confusion_matrix import compute_confusion_matrix
from metrics.classification_metrics import (
    compute_classification_metrics,
    compute_confidence_stability
)
from analysis.per_model_analysis import per_model_analysis
from analysis.ensemble_comparison import ensemble_comparison
from export.export_metrics_for_backend import export_metrics_for_backend


def main():
    print("🚀 Starting Evaluation Engine")

    # 1️⃣ Connect to MongoDB
    mongo = MongoDBClient()
    mongo.connect()

    # 2️⃣ Get DetectionLog collection
    collection = mongo.get_collection()

    # 3️⃣ Load detection logs (can later add time_window="1h"/"6h")
    df = load_detection_logs(collection)

    # 4️⃣ Sanity check output
    print("\n📊 Sample Evaluation Data:")
    print(df.head())

    if df.empty:
        print("\n⚠️ No logs found. Skipping evaluation.")
        mongo.close()
        return

    # 5️⃣ Confusion Matrix (Proxy)
    cm = compute_confusion_matrix(df)
    print("\n📊 Confusion Matrix (Proxy Evaluation):")
    for k, v in cm.items():
        print(f"{k}: {v}")

    # 6️⃣ Classification Metrics
    cls_metrics = compute_classification_metrics(cm)
    print("\n📈 Classification Metrics:")
    for k, v in cls_metrics.items():
        print(f"{k}: {v}")

    # 7️⃣ Confidence Stability (NEW)
    confidence_stability = compute_confidence_stability(
        df["confidence"].dropna().tolist()
    )
    print("\n📉 Confidence Stability:")
    for k, v in confidence_stability.items():
        print(f"{k}: {v}")

    # 8️⃣ Per-Model Analysis
    model_analysis = per_model_analysis(df)
    print("\n🤖 Per-Model Analysis:")
    for k, v in model_analysis.items():
        print(f"\n{k}:")
        print(v)

    # 9️⃣ Ensemble Comparison
    ensemble_stats = ensemble_comparison(df)
    print("\n🧠 Ensemble Comparison:")
    for k, v in ensemble_stats.items():
        print(f"{k}: {v}")

    # 🔟 Export metrics for backend (UPDATED)
    export_metrics_for_backend(
        confusion_matrix=cm,
        classification_metrics=cls_metrics,
        confidence_stability=confidence_stability,
        per_model_analysis=model_analysis,
        ensemble_comparison=ensemble_stats,
        time_window="all"
    )

    # 🔒 Close DB
    mongo.close()

    print("✅ Evaluation Engine finished successfully")


if __name__ == "__main__":
    main()
