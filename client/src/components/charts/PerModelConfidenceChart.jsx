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

/* 🎨 MODEL COLORS (MATCH REAL MODELS) */
const MODEL_COLORS = {
  LogisticRegression: "#bae6fd",
  DecisionTree: "#fecaca",
  RandomForest: "#fde68a",
  KNN: "#fdba74",
  NaiveBayes: "#e5e7eb",
  GradientBoosting: "#fbcfe8",
  XGBoost: "#ddd6fe",
  LightGBM: "#bbf7d0",
  MLP: "#7dd3fc",
};

/* ================= COMPONENT ================= */

function PerModelConfidenceChart({ modelProbabilities }) {
  if (!modelProbabilities || Object.keys(modelProbabilities).length === 0) {
    return (
      <p className="text-sm text-gray-500">
        No per-model confidence data available
      </p>
    );
  }

  /* Convert DB object → chart data */
  const data = Object.entries(modelProbabilities).map(
    ([model, confidence]) => ({
      model,
      value: +(confidence * 100).toFixed(2),
    })
  );

  /* Find dominant model */
  const dominant = data.reduce((a, b) =>
    b.value > a.value ? b : a
  );

  /* Tooltip */
  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;

    const { model, value } = payload[0].payload;

    return (
      <div className="bg-gray-900 px-3 py-2 rounded-lg shadow text-xs text-white">
        <div className="flex items-center gap-2 mb-1">
          <span
            className="w-2.5 h-2.5 rounded-full"
            style={{ backgroundColor: MODEL_COLORS[model] || "#9ca3af" }}
          />
          <span className="font-semibold">{model}</span>
        </div>
        <div className="text-gray-300">
          Confidence:{" "}
          <span className="font-bold text-pink-400">
            {value}%
          </span>
        </div>
      </div>
    );
  };

  return (
    <div className="h-[260px] w-full">
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid
            strokeDasharray="3 3"
            vertical={false}
            stroke="#e5e7eb"
          />

          <XAxis
            dataKey="model"
            tick={{ fontSize: 11 }}
            axisLine
          />

          <YAxis
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
            tick={{ fontSize: 11 }}
            axisLine
          />

          <Tooltip content={<CustomTooltip />} />

          <Bar dataKey="value" radius={[6, 6, 0, 0]}>
            {data.map((entry) => (
              <Cell
                key={entry.model}
                fill={MODEL_COLORS[entry.model] || "#9ca3af"}
                opacity={entry.model === dominant.model ? 1 : 0.55}
              />
            ))}

            <LabelList
              dataKey="value"
              position="top"
              formatter={(v) => (v > 0 ? `${v}%` : "")}
              fontSize={11}
              fill="#374151"
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PerModelConfidenceChart;
