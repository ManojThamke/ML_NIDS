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
  "0-20": "#86efac",   // Very safe
  "20-40": "#34d399", // Low risk
  "40-60": "#fbbf24", // Uncertain
  "60-80": "#fca5a5", // Suspicious
  "80-100": "#c4b5fd" // High risk
};

/* Clean tooltip */
const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload || !payload.length) return null;

  const { range, count } = payload[0].payload;

  return (
    <div className="bg-white border rounded-lg px-4 py-2 shadow-lg">
      <p className="text-sm font-semibold text-gray-700 mb-1">
        Confidence Band: {range}%
      </p>
      <p className="text-sm text-gray-600">
        Alerts: <span className="font-semibold">{count}</span>
      </p>
    </div>
  );
};

function ProbabilityConfidenceBands({ data }) {
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <p className="text-sm text-gray-500">
          No confidence band data available
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px] flex flex-col">
      <h3 className="font-semibold mb-2 text-gray-700">
        Probability Confidence Bands
      </h3>

      {/* 🔥 Fixed-height chart area */}
      <div className="h-[250px]">
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
            >
              {data.map((entry) => (
                <Cell
                  key={entry.range}
                  fill={BAND_COLORS[entry.range]}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Explanation line */}
      <p className="-mt-2 text-sm text-gray-600 text-center leading-snug">
        Shows how alerts are distributed across different model confidence ranges.
      </p>
    </div>
  );
}

export default ProbabilityConfidenceBands;
