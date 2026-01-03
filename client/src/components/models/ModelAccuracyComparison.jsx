import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
} from "recharts";

/* 🎨 ML-NIDS pastel palette */
const COLORS = [
  "#93c5fd",
  "#7dd3fc",
  "#fdba74",
  "#c4b5fd",
  "#86efac",
  "#fde68a",
  "#a7f3d0",
  "#fca5a5",
  "#fbcfe8",
];

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

function ModelAccuracyComparison({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <p className="text-sm text-gray-400">
          No model accuracy data available
        </p>
      </div>
    );
  }

  const formatted = data.map((m) => ({
    modelName: m.modelName,
    accuracyPercent: +(m.accuracy * 100).toFixed(2),
  }));

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px] flex flex-col">
      <h3 className="font-semibold mb-2 text-gray-700">
        Model Accuracy Comparison
      </h3>

      {/* 🔥 Fixed-height chart area */}
      <div className="h-[235px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={formatted}
            margin={{ top: 12, right: 10, left: 0, bottom: 6 }}
            barCategoryGap="18%"
          >
            <CartesianGrid strokeDasharray="3 3" />

            <XAxis
              dataKey="modelName"
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

            <Tooltip formatter={(v) => `${v}%`} />

            <Bar
              dataKey="accuracyPercent"
              radius={[6, 6, 0, 0]}
              barSize={32}
            >
              {/* Percentage labels */}
              <LabelList
                dataKey="accuracyPercent"
                position="top"
                formatter={(v) => `${v}%`}
                fontSize={11}
                fill="#6b7280"
              />
              {formatted.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Explanation line (tight & readable) */}
      <p className="-mt-2 text-sm text-gray-600 text-center leading-snug">
        Accuracy shows overall correctness but does not reflect false alarms.
      </p>
    </div>
  );
}

export default ModelAccuracyComparison;
