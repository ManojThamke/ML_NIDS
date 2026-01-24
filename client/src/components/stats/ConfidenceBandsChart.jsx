import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  CartesianGrid,
} from "recharts";

/* 🎨 Confidence band colors (ML-NIDS semantic palette) */
const BAND_COLORS = {
  "0–20%": "#bbf7d0",   // Very safe
  "20–40%": "#86efac", // Low risk
  "40–60%": "#fde68a", // Uncertain
  "60–80%": "#fca5a5", // Suspicious
  "80–100%": "#ef4444" // High risk
};

/* Clean dashboard tooltip */
const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload || !payload.length) return null;

  const { range, count } = payload[0].payload;

  return (
    <div className="bg-gray-900 text-white rounded-lg px-4 py-2 shadow-lg">
      <p className="text-sm font-semibold mb-1">
        Confidence Range: {range}
      </p>
      <p className="text-sm text-gray-300">
        Alerts:{" "}
        <span className="font-semibold text-white">
          {count}
        </span>
      </p>
    </div>
  );
};

function ConfidenceBandsChart({ data }) {
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border animate-fade-in">
        <p className="text-sm text-gray-500">
          No confidence distribution data available
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px] flex flex-col animate-fade-in">
      <h3 className="font-semibold mb-1 text-gray-700">
        Confidence Distribution
      </h3>
      <p className="text-xs text-gray-500 mb-3">
        Distribution of alerts across confidence ranges
      </p>

      {/* Chart */}
      <div className="h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 12, right: 20, left: 0, bottom: 6 }}
            barCategoryGap={30}
          >
            <CartesianGrid
              vertical={false}
              strokeDasharray="3 3"
              stroke="#e5e7eb"
            />

            <XAxis
              dataKey="range"
              tick={{ fontSize: 11, fill: "#374151" }}
            />

            <YAxis
              allowDecimals={false}
              tick={{ fontSize: 11, fill: "#6b7280" }}
              padding={{ top: 18 }}
            />

            <Tooltip content={<CustomTooltip />} />

            <Bar
              dataKey="count"
              radius={[6, 6, 0, 0]}
              barSize={40}
              isAnimationActive
              animationBegin={200}
              animationDuration={1500}
              animationEasing="ease-in-out"
            >
              {data.map((entry) => (
                <Cell
                  key={entry.range}
                  fill={BAND_COLORS[entry.range] || "#e5e7eb"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Explanation */}
      <p className="text-xs text-gray-600 text-center mt-1">
        Higher confidence bands indicate stronger model agreement.
      </p>
    </div>
  );
}

export default ConfidenceBandsChart;
