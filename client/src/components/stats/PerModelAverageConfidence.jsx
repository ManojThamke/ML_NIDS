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

/* 🎨 Soft pastel colors (your original nice ones) */
const MODEL_COLORS = {
  RandomForest: "#fde68a",
  GradientBoosting: "#86efac",
  DecisionTree: "#bfdbfe",
  LightGBM: "#bbf7d0",
  MLP: "#ddd6fe",
  XGBoost: "#fecaca",
  KNN: "#fbcfe8",
  NaiveBayes: "#e5e7eb",
  LogisticRegression: "#f3f4f6",
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

/* ✅ Two-line X-axis labels (same logic everywhere) */
const CustomTick = ({ x, y, payload }) => {
  const label = MODEL_LABELS[payload.value] || payload.value;
  const parts = label.split(" ");

  return (
    <g transform={`translate(${x},${y + 8})`}>
      <text
        textAnchor="middle"
        fill="#6b7280"
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

  const { model, value } = payload[0].payload;

  return (
    <div className="bg-gray-900 text-white rounded-lg px-4 py-2 shadow-lg">
      <p className="text-sm font-semibold mb-1">
        {MODEL_LABELS[model] || model}
      </p>
      <p className="text-sm text-gray-300">
        Avg Confidence:{" "}
        <span className="font-semibold text-white">
          {value}%
        </span>
      </p>
    </div>
  );
};

function PerModelAverageConfidence({ data }) {
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <p className="text-sm text-gray-500">
          No per-model confidence data available
        </p>
      </div>
    );
  }

  /* Convert confidence (0–1) → percentage */
  const chartData = data.map((d) => ({
    model: d.model,
    value: +(d.avgConfidence * 100).toFixed(2),
  }));

  /* Subtle dynamic Y scaling */
  const maxValue = Math.max(...chartData.map(d => d.value));
  const yMax = Math.ceil(maxValue + 2);

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px] flex flex-col animate-fade-in">
      <h3 className="font-semibold mb-1 text-gray-700">
        Per-Model Average Confidence
      </h3>
      <p className="text-xs text-gray-500 mb-3">
        Relative confidence strength of each detection model
      </p>

      <div className="h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 10, right: 20, left: 0, bottom: 10 }}
            barCategoryGap="30%"
          >
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke="#e5e7eb"
            />

            <XAxis
              dataKey="model"
              tick={<CustomTick />}
              interval={0}
              height={56}
            />

            <YAxis
              domain={[0, yMax]}
              tickFormatter={(v) => `${v}%`}
              tick={{ fontSize: 11, fill: "#6b7280" }}
            />

            <Tooltip content={<CustomTooltip />} />

            <Bar
              dataKey="value"
              radius={[6, 6, 0, 0]}
              isAnimationActive
              animationDuration={1400}
              animationEasing="ease-in-out"
            >
              {chartData.map((entry) => (
                <Cell
                  key={entry.model}
                  fill={MODEL_COLORS[entry.model] || "#e5e7eb"}
                />
              ))}

              <LabelList
                dataKey="value"
                position="top"
                formatter={(v) => `${v}%`}
                fontSize={11}
                fill="#6b7280"
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="text-xs text-gray-600 text-center mt-1">
        Higher bars indicate stronger average model confidence (not accuracy).
      </p>
    </div>
  );
}

export default PerModelAverageConfidence;
