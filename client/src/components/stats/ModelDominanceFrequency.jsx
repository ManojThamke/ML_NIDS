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

/* 🎨 ML-NIDS unified model palette */
const MODEL_COLORS = {
  rf: "#93c5fd",
  lgb: "#fde68a",
  xgb: "#a7f3d0",
  svm: "#fca5a5",
  knn: "#fbcfe8",
  mlp: "#c4b5fd",
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

/* Clean tooltip (dashboard style) */
const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload || !payload.length) return null;

  const { model, percent } = payload[0].payload;

  return (
    <div className="bg-white border rounded-lg px-4 py-2 shadow-lg">
      <p className="text-sm font-semibold text-gray-700 mb-1">
        {model.toUpperCase()}
      </p>
      <p className="text-sm text-gray-600">
        Dominance: <span className="font-semibold">{percent}%</span>
      </p>
    </div>
  );
};

function ModelDominanceFrequency({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <p className="text-sm text-gray-500">
          No dominance data available
        </p>
      </div>
    );
  }

  /* 🔥 Find most dominant model */
  const dominant = data.reduce((a, b) =>
    b.percent > a.percent ? b : a
  );

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px] flex flex-col">
      <h3 className="font-semibold mb-2 text-gray-700">
        Model Dominance Frequency
      </h3>

      {/* 🔥 Fixed-height chart area */}
      <div className="h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 12, right: 20, left: 0, bottom: 6 }}
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
              height={45}
              tickMargin={6}
            />

            <YAxis
              domain={[0, 100]}
              tickFormatter={(v) => `${v}%`}
              padding={{ top: 18 }}
            />

            <Tooltip content={<CustomTooltip />} />

            <Bar dataKey="percent" radius={[8, 8, 0, 0]}>
              {data.map((entry) => (
                <Cell
                  key={entry.model}
                  fill={MODEL_COLORS[entry.model] || "#9ca3af"}
                  opacity={entry.model === dominant.model ? 1 : 0.6}
                />
              ))}

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

      {/* Explanation line */}
      <p className="-mt-2 text-sm text-gray-600 text-center leading-snug">
        Shows how often each model was the most confident during detection.
      </p>
    </div>
  );
}

export default ModelDominanceFrequency;
