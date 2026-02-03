from db.mongo_client import MongoDBClient
from loaders.load_detection_logs import load_detection_logs
from metrics.confusion_matrix import compute_confusion_matrix_vectorized
from metrics.classification_metrics import (
    compute_classification_metrics,
    compute_confidence_stability
)
from analysis.per_model_analysis import per_model_analysis
from analysis.ensemble_comparison import ensemble_comparison
from export.export_metrics_for_backend import export_metrics_for_backend


def main():
    """
    Main entry point for the Evaluation Engine.
    Loads real-time detection logs, computes evaluation metrics,
    performs ensemble analysis, and exports results for backend use.
    """

    print("\n🚀 Starting Evaluation Engine")

    mongo = None

    try:
        # =====================================================
        # 1️⃣ Connect to MongoDB
        # =====================================================
        mongo = MongoDBClient()
        mongo.connect()
        print("✅ Connected to MongoDB")

        # =====================================================
        # 2️⃣ Fetch Detection Logs
        # =====================================================
        collection = mongo.get_collection()
        df = load_detection_logs(collection)

        print("\n📊 Sample Detection Logs:")
        print(df.head())

        if df.empty:
            print("\n⚠️ No detection logs found. Evaluation aborted.")
            return

        print(f"\n📦 Total records loaded: {len(df)}")

        # =====================================================
        # 3️⃣ Confusion Matrix (Proxy Evaluation)
        # =====================================================
        cm = compute_confusion_matrix_vectorized(df)
        print("\n📊 Confusion Matrix:")
        for k, v in cm.items():
            print(f"  {k}: {v}")

        # =====================================================
        # 4️⃣ Classification Metrics
        # =====================================================
        cls_metrics = compute_classification_metrics(cm)
        print("\n📈 Classification Metrics:")
        for k, v in cls_metrics.items():
            print(f"  {k}: {v}")

        # =====================================================
        # 5️⃣ Confidence Stability Analysis
        # =====================================================
        confidence_values = df["confidence"].dropna().tolist()

        confidence_stability = compute_confidence_stability(confidence_values)
        print("\n📉 Confidence Stability:")
        for k, v in confidence_stability.items():
            print(f"  {k}: {v}")

        # =====================================================
        # 6️⃣ Per-Model Analysis
        # =====================================================
        model_analysis = per_model_analysis(df)
        print("\n🤖 Per-Model Analysis Summary:")
        for section, values in model_analysis.items():
            print(f"\n🔹 {section}:")
            print(values)

        # =====================================================
        # 7️⃣ Ensemble Comparison
        # =====================================================
        ensemble_stats = ensemble_comparison(df)
        print("\n🧠 Ensemble Comparison:")
        for k, v in ensemble_stats.items():
            print(f"  {k}: {v}")

        # =====================================================
        # 8️⃣ Export Metrics for Backend & Reports
        # =====================================================
        export_metrics_for_backend(
            confusion_matrix=cm,
            classification_metrics=cls_metrics,
            confidence_stability=confidence_stability,
            per_model_analysis=model_analysis,
            ensemble_comparison=ensemble_stats,
            time_window="all"
        )

        print("\n📤 Metrics exported successfully")

    except Exception as e:
        print("\n❌ Evaluation Engine failed")
        print(f"Reason: {e}")

    finally:
        # =====================================================
        # 9️⃣ Cleanup
        # =====================================================
        if mongo:
            mongo.close()
            print("🔒 MongoDB connection closed")

        print("\n✅ Evaluation Engine finished")


if __name__ == "__main__":
    main()
