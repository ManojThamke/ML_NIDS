import React from "react";

/* ✅ Professional model labels (shared standard) */
const MODEL_LABELS = {
  RandomForest: "Random Forest",
  GradientBoosting: "Gradient Boosting",
  DecisionTree: "Decision Tree",
  LightGBM: "LightGBM",
  XGBoost: "XGBoost",
  KNN: "KNN",
  MLP: "MLP",
  NaiveBayes: "Naive Bayes",
  LogisticRegression: "Logistic Regression",
};

/* 🎨 Softer SOC-style color scale */
function getColor(value) {
  if (value >= 99) return "bg-green-500 text-white";
  if (value >= 95) return "bg-green-200 text-gray-900";
  if (value >= 85) return "bg-yellow-200 text-gray-900";
  if (value >= 70) return "bg-orange-200 text-gray-900";
  return "bg-red-200 text-gray-900";
}

/* 🔒 Clamp safety */
const clamp = (v) => Math.min(Math.max(v, 0), 100);

/* Two-line header renderer */
const HeaderCell = ({ label }) => {
  const parts = label.split(" ");
  return (
    <div className="text-xs text-center font-semibold text-gray-600 leading-tight">
      {parts.map((p, i) => (
        <div key={i}>{p}</div>
      ))}
    </div>
  );
};

function ModelAgreementHeatmap({ data }) {
  /* 🔐 Hard guard */
  if (
    !data ||
    !Array.isArray(data.models) ||
    data.models.length === 0 ||
    !data.matrix
  ) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border h-[300px] flex items-center justify-center">
        <p className="text-sm text-gray-400">
          Loading model agreement data…
        </p>
      </div>
    );
  }

  const { models, matrix } = data;

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border">
      <h3 className="font-semibold mb-2 text-gray-700">
        Model Agreement Heatmap
      </h3>
      <p className="text-xs text-gray-500 mb-4">
        Pairwise agreement percentage between detection models
      </p>

      <div
        className="grid gap-px"
        style={{
          gridTemplateColumns: `130px repeat(${models.length}, 1fr)`,
        }}
      >
        {/* Column Headers */}
        <div />
        {models.map((model) => (
          <HeaderCell
            key={model}
            label={MODEL_LABELS[model] || model}
          />
        ))}

        {/* Rows */}
        {models.map((row) => (
          <React.Fragment key={row}>
            {/* Row Header */}
            <div className="text-xs font-semibold text-gray-600 flex items-center pr-2">
              {MODEL_LABELS[row] || row}
            </div>

            {models.map((col) => {
              const rawValue = matrix[row]?.[col] ?? 0;
              const value = clamp(rawValue);
              const isDiagonal = row === col;

              return (
                <div
                  key={`${row}-${col}`}
                  className={`h-10 flex items-center justify-center text-xs font-medium
                    ${
                      isDiagonal
                        ? "bg-gray-200 text-gray-700 font-semibold"
                        : getColor(value)
                    }`}
                >
                  {value.toFixed(2)}%
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-4 mt-4 text-xs text-gray-600">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-green-500 rounded"></span> ≥99%
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-green-200 rounded"></span> 95–99%
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-yellow-200 rounded"></span> 85–95%
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-orange-200 rounded"></span> 70–85%
        </span>
      </div>

      {/* Insight */}
      <p className="text-xs text-gray-500 text-center mt-3">
        High agreement indicates stable ensemble behavior and consistent
        classification decisions.
      </p>
    </div>
  );
}

export default ModelAgreementHeatmap;
