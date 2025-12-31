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
// "#93c5fd", 
//   "#7dd3fc", 
//   "#fdba74", 
//   "#c4b5fd", 
//   "#86efac", 
//   "#fde68a", 
//   "#a7f3d0", 
//   "#fca5a5", 
//   "#fbcfe8", 
//   "#ddd6fe", 
//   "#fecaca",
const BAND_COLORS = {
  "0-20": "#86efac",   // Very safe
  "20-40": "#34d399", // Low risk
  "40-60": "#fbbf24", // Uncertain
  "60-80": "#ec4899", // Suspicious
  "80-100": "#a78bfa" // High risk
};

function ProbabilityConfidenceBands({ data }) {
  return (
    <div className="bg-white rounded-xl p-6 shadow border h-[340px] flex flex-col">
      <h3 className="font-semibold mb-2 text-gray-700">
        Probability Confidence Bands
      </h3>

      <div className="flex-1">
        <ResponsiveContainer>
          <BarChart
            data={data}
            margin={{ top: 20, right: 30, left: 10, bottom: 10 }}
            barCategoryGap={30}
          >
            <CartesianGrid
              vertical={false}
              strokeDasharray="3 3"
              stroke="#e5e7eb"
            />

            <XAxis
              dataKey="range"
              tick={{ fontSize: 12 }}
            />

            <YAxis
              allowDecimals={false}
              tick={{ fontSize: 12 }}
            />

            <Tooltip
              contentStyle={{
                backgroundColor: "#111827",
                borderRadius: "8px",
                border: "none",
                color: "#fff",
                fontSize: "12px",
              }}
              formatter={(v) => [`${v} logs`, "Count"]}
            />

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

      {/* Insight Text */}
      <p className="mt-1 text-xs text-gray-500 text-center">
        Distribution of alerts based on model confidence levels.
      </p>
    </div>
  );
}

export default ProbabilityConfidenceBands;
