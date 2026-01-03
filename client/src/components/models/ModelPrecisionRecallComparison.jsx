import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

/* 🎨 ML-NIDS pastel colors */
const COLORS = {
  precision: "#93c5fd", // light blue
  recall: "#86efac",    // light green
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
          <tspan key={i} x="0" dy={i === 0 ? 0 : 12}>
            {word}
          </tspan>
        ))}
      </text>
    </g>
  );
};

/* Clean tooltip */
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="bg-white border rounded-lg px-4 py-2 shadow-lg">
      <p className="text-sm font-semibold text-gray-700 mb-1">
        {label}
      </p>
      {payload.map((item, idx) => (
        <p
          key={idx}
          className="text-sm"
          style={{ color: item.color }}
        >
          {item.name}: {item.value}%
        </p>
      ))}
    </div>
  );
};

function ModelPrecisionRecallComparison({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <p className="text-sm text-gray-400">
          No precision/recall data available
        </p>
      </div>
    );
  }

  const formatted = data.map((m) => ({
    modelName: m.modelName,
    precision: +(m.precision * 100).toFixed(2),
    recall: +(m.recall * 100).toFixed(2),
  }));

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px] flex flex-col">
      <h3 className="font-semibold mb-1 text-gray-700">
        Precision vs Recall Comparison
      </h3>

      {/* Legend */}
      <div className="flex justify-center gap-6 text-sm text-gray-600 mb-1">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded bg-[#93c5fd]" />
          Precision
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded bg-[#86efac]" />
          Recall
        </div>
      </div>

      {/* 🔥 Fixed-height chart area */}
      <div className="h-[235px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={formatted}
            margin={{ top: 12, right: 20, left: 0, bottom: 6 }}
            barCategoryGap="24%"
          >
            <CartesianGrid strokeDasharray="3 3" />

            <XAxis
              dataKey="modelName"
              tick={<CustomTick />}
              interval={0}
              height={45}
            />

            <YAxis
              domain={[0, 100]}
              tickFormatter={(v) => `${v}%`}
              padding={{ top: 18 }}
            />

            <Tooltip
              content={<CustomTooltip />}
              wrapperStyle={{ zIndex: 1000 }}
            />

            <Bar
              dataKey="precision"
              fill={COLORS.precision}
              radius={[6, 6, 0, 0]}
              barSize={28}
            />

            <Bar
              dataKey="recall"
              fill={COLORS.recall}
              radius={[6, 6, 0, 0]}
              barSize={28}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Explanation line */}
      <p className="-mt-2 text-sm text-gray-600 text-center leading-snug">
        Precision reflects false alarms, while recall shows missed intrusions.
      </p>
    </div>
  );
}

export default ModelPrecisionRecallComparison;
