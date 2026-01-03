import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LabelList,
} from "recharts";

const COLOR_F1 = "#c4b5fd";

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

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="bg-white border rounded-lg px-4 py-2 shadow-lg">
      <p className="text-sm font-semibold text-gray-700 mb-1">
        {label}
      </p>
      <p className="text-sm text-violet-600">
        F1 Score: {payload[0].value}%
      </p>
    </div>
  );
};

function F1ScoreComparison({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <p className="text-sm text-gray-400">
          No F1 score data available
        </p>
      </div>
    );
  }

  const formatted = data.map((m) => ({
    modelName: m.modelName,
    f1: +(m.f1 * 100).toFixed(2),
  }));

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px] flex flex-col">
      <h3 className="font-semibold mb-2 text-gray-700">
        F1 Score Comparison
      </h3>

      {/* Fixed-height chart */}
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
              dataKey="f1"
              fill={COLOR_F1}
              radius={[6, 6, 0, 0]}
              barSize={30}
            >
              <LabelList
                dataKey="f1"
                position="top"
                formatter={(v) => `${v}%`}
                fontSize={11}
                fill="#6b7280"
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Tight explanation */}
      <p className="-mt-2 text-sm text-gray-600 text-center leading-snug">
        F1 score balances precision and recall for intrusion detection.
      </p>
    </div>
  );
}

export default F1ScoreComparison;
