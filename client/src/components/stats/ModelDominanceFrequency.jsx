import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
  LabelList,
} from "recharts";

/* 🎨 Soft professional palette */
const MODEL_COLORS = {
  RandomForest: "#60a5fa",
  GradientBoosting: "#fde68a",
  DecisionTree: "#e5e7eb",
  KNN: "#fbcfe8",
  LightGBM: "#c7d2fe",
  MLP: "#ddd6fe",
  XGBoost: "#a7f3d0",
  NaiveBayes: "#fecaca",
  LogisticRegression: "#d1d5db",
};

/* ✅ Professional display labels */
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

/* ✅ Two-line X-axis labels (professional) */
const CustomTick = ({ x, y, payload }) => {
  const label = MODEL_LABELS[payload.value] || payload.value;
  const parts = label.split(" ");

  return (
    <g transform={`translate(${x},${y + 8})`}>
      <text
        textAnchor="middle"
        fill="#374151"
        fontSize={11}
        fontWeight={500}
      >
        {parts.map((part, index) => (
          <tspan
            key={index}
            x="0"
            dy={index === 0 ? 0 : 12}
          >
            {part}
          </tspan>
        ))}
      </text>
    </g>
  );
};

/* Tooltip */
const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;

  const { model, percent } = payload[0].payload;

  return (
    <div className="bg-white border rounded-lg px-4 py-2 shadow-lg">
      <p className="text-sm font-semibold text-gray-700 mb-1">
        {MODEL_LABELS[model] || model}
      </p>
      <p className="text-sm text-gray-600">
        Dominance: <span className="font-semibold">{percent}%</span>
      </p>
    </div>
  );
};

function ModelDominanceFrequencyChart({ data }) {
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px] flex items-center justify-center">
        <p className="text-sm text-gray-400">
          No model dominance data available
        </p>
      </div>
    );
  }

  /* 🔥 Identify most dominant model */
  const dominant = data.reduce((a, b) =>
    b.percent > a.percent ? b : a
  );

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px] flex flex-col">
      <h3 className="font-semibold mb-1 text-gray-700">
        Model Dominance Frequency
      </h3>
      <p className="text-xs text-gray-500 mb-2">
        How often each model was the most confident during detection
      </p>

      <div className="h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 14, right: 20, left: 0, bottom: 10 }}
            barCategoryGap="30%"
          >
            <CartesianGrid
              vertical={false}
              strokeDasharray="3 3"
              stroke="#e5e7eb"
            />

            <XAxis
              dataKey="model"
              tick={<CustomTick />}
              interval={0}
              height={56}
            />

            <YAxis
              domain={[0, 100]}
              tickFormatter={(v) => `${v}%`}
              tick={{ fontSize: 11, fill: "#6b7280" }}
              padding={{ top: 18 }}
            />

            <Tooltip content={<CustomTooltip />} />

            <Bar
              dataKey="percent"
              radius={[10, 10, 0, 0]}
              isAnimationActive
              animationDuration={900}
            >
              {data.map((entry) => {
                const isTop = entry.model === dominant.model;
                return (
                  <Cell
                    key={entry.model}
                    fill={MODEL_COLORS[entry.model] || "#9ca3af"}
                    opacity={isTop ? 1 : 0.75}
                    style={
                      isTop
                        ? {
                            filter:
                              "drop-shadow(0px 6px 10px rgba(0,0,0,0.12))",
                          }
                        : {}
                    }
                  />
                );
              })}

              <LabelList
                dataKey="percent"
                position="top"
                formatter={(v) => `${v}%`}
                fontSize={11}
                fill="#6b7280"
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="-mt-1 text-sm text-gray-600 text-center leading-snug">
        Higher dominance indicates stronger influence on ensemble decisions.
      </p>
    </div>
  );
}

export default ModelDominanceFrequencyChart;
