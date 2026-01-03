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

/* 🎨 Consistent ML-NIDS Model Colors */
const MODEL_COLORS = {
  rf: "#86efac",
  lgb: "#fde68a",
  xgb: "#a7f3d0",
  svm: "#fca5a5",
  knn: "#fbcfe8",
  mlp: "#ddd6fe",
  naive_bayes: "#fecaca",
};

/* Wrapped X-axis labels */
const CustomTick = ({ x, y, payload }) => {
  const words = payload.value.split(" ");
  return (
    <g transform={`translate(${x},${y + 6})`}>
      <text
        textAnchor="middle"
        fill="#374151"
        fontSize={11}
        fontWeight={500}
      >
        {words.map((word, i) => (
          <tspan key={i} x={0} dy={i === 0 ? 0 : 12}>
            {word}
          </tspan>
        ))}
      </text>
    </g>
  );
};

/* Clean dashboard tooltip */
const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload || !payload.length) return null;

  const { model, value } = payload[0].payload;

  return (
    <div className="bg-white border rounded-lg px-4 py-2 shadow-lg">
      <p className="text-sm font-semibold text-gray-700 mb-1">
        {model.toUpperCase()}
      </p>
      <p className="text-sm text-gray-600">
        Avg Probability: <span className="font-semibold">{value}%</span>
      </p>
    </div>
  );
};

function PerModelAverageProbabilityChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <p className="text-sm text-gray-500">
          No model probability data available
        </p>
      </div>
    );
  }

  /* Convert to percentage */
  const chartData = data.map((d) => ({
    model: d.model,
    value: +(d.avgProbability * 100).toFixed(2),
  }));

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px] flex flex-col">
      <h3 className="font-semibold mb-2 text-gray-700">
        Per-Model Average Probability
      </h3>

      {/* 🔥 Fixed-height chart area */}
      <div className="h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 12, right: 20, left: 0, bottom: 6 }}
            barCategoryGap="22%"
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
              height={45}
              tickMargin={6}
            />

            <YAxis
              domain={[0, 100]}
              tickFormatter={(v) => `${v}%`}
              padding={{ top: 18 }}
            />

            <Tooltip content={<CustomTooltip />} />

            <Bar dataKey="value" radius={[6, 6, 0, 0]}>
              {chartData.map((entry) => (
                <Cell
                  key={entry.model}
                  fill={MODEL_COLORS[entry.model] || "#9ca3af"}
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

      {/* Explanation line */}
      <p className="-mt-2 text-sm text-gray-600 text-center leading-snug">
        Shows the average confidence level produced by each detection model.
      </p>
    </div>
  );
}

export default PerModelAverageProbabilityChart;
