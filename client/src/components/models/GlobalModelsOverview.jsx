import { useEffect, useState } from "react";
import { getModelMetrics } from "../../api";

/* Charts */
import ModelAccuracyComparison from "./ModelAccuracyComparison";
import ModelPrecisionRecallComparison from "./ModelPrecisionRecallComparison";
import F1ScoreComparison from "./F1ScoreComparison";
import RocAucComparison from "./RocAucComparison";

function GlobalModelsOverview() {
  const [modelMetrics, setModelMetrics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getModelMetrics()
      .then((res) => {
        setModelMetrics(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Model metrics error:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <p className="text-sm text-gray-500">
        Loading model analytics…
      </p>
    );
  }

  return (
    <div className="space-y-8">

      {/* ===============================
          MODEL PERFORMANCE OVERVIEW
      =============================== */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          Model Performance Overview
        </h2>

        {/* 🔥 FINAL 2×2 GRID */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

          {/* Row 1 */}
          <ModelAccuracyComparison data={modelMetrics} />
          <ModelPrecisionRecallComparison data={modelMetrics} />

          {/* Row 2 */}
          <F1ScoreComparison data={modelMetrics} />
          <RocAucComparison data={modelMetrics} />

        </div>
      </div>

    </div>
  );
}

export default GlobalModelsOverview;
