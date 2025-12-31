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

/* 🎨 Consistent Model Colors */
const MODEL_COLORS = {
  rf: "#fde68a",
  lgb: "#fbcfe8",
  xgb: "#ddd6fe",
  svm: "#fca5a5",       // dominant
  knn: "#fdba74",
  mlp: "#7dd3fc",
  naive_bayes: "#94a3b8",
};

function PerModelProbabilityChart({ perModel }) {
  if (!perModel || Object.keys(perModel).length === 0) {
    return (
      <p className="text-sm text-gray-500">
        No per-model data available
      </p>
    );
  }

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload || !payload.length) return null;

  const { model, value } = payload[0].payload;

  return (
    <div className="bg-gray-900 px-3 py-2 rounded-lg shadow text-xs text-pink-50">
      <div className="flex items-center gap-2 mb-1">
        <span
          className="w-2.5 h-2.5 rounded-full"
          style={{ backgroundColor: MODEL_COLORS[model] || "#9ca3af" }}
        />
        <span className="font-semibold uppercase">{model}</span>
      </div>
      <div className="text-pink-200">
        Probability: <span className="font-bold text-pink-500">{value}%</span>
      </div>
    </div>
  );
};

  /* Convert object → chart data */
  const data = Object.entries(perModel).map(([model, prob]) => ({
    model,
    value: +(prob * 100).toFixed(2),
  }));

  /* Dominant model detection */
  const dominant = data.reduce((a, b) =>
    b.value > a.value ? b : a
  );

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
            tick={{ fontSize: 12 }}
            axisLine={false}
          />

          <YAxis
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
            axisLine={false}
            tick={{ fontSize: 12 }}
          />

          <Tooltip content={<CustomTooltip />}/>

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

export default PerModelProbabilityChart;
