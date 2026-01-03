import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ReferenceLine,
  Area,
} from "recharts";

function EnsembleVsBestModelChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border h-[470px] flex items-center justify-center">
        <p className="text-sm text-gray-400">
          No ensemble comparison data available
        </p>
      </div>
    );
  }

  // 🔥 Dynamic Y scale (very important)
  const maxValue = Math.max(
    ...data.map(d => Math.max(d.bestModel, d.ensemble))
  );

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[470px] flex flex-col">
      {/* Header */}
      <h3 className="font-semibold text-gray-700">
        Ensemble vs Best Model
      </h3>
      <p className="text-xs text-gray-500 mb-3">
        Ensemble confidence compared with the most confident individual model
      </p>

      {/* Chart */}
      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke="#e5e7eb"
            />

            <XAxis
              dataKey="index"
              tick={{ fontSize: 11 }}
              label={{
                value: "Alert Index",
                position: "insideBottom",
                offset: -5,
                fontSize: 11,
              }}
            />

            <YAxis
              domain={[0, Math.ceil(maxValue + 2)]}
              tickFormatter={(v) => `${v}%`}
              tick={{ fontSize: 11 }}
            />

            <Tooltip
              formatter={(v) => `${v}%`}
              contentStyle={{
                background: "#111827",
                borderRadius: "8px",
                border: "none",
                color: "#fff",
                fontSize: "12px",
              }}
            />

            <Legend
              verticalAlign="top"
              height={28}
              wrapperStyle={{ fontSize: "12px" }}
            />

            {/* 🟦 Ensemble Area (confidence band effect) */}
            <Area
              type="monotone"
              dataKey="ensemble"
              fill="#3b82f6"
              fillOpacity={0.15}
              stroke="none"
            />

            {/* 🔴 Best Model */}
            <Line
              type="monotone"
              dataKey="bestModel"
              stroke="#ef4444"
              strokeWidth={2}
              dot={false}
              name="Best Individual Model"
            />

            {/* 🔵 Ensemble */}
            <Line
              type="monotone"
              dataKey="ensemble"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={false}
              name="Ensemble Prediction"
            />

            {/* ⚠️ Optional decision threshold */}
            <ReferenceLine
              y={50}
              stroke="#9ca3af"
              strokeDasharray="4 4"
              ifOverflow="extendDomain"
              label={{
                value: "Decision Threshold",
                position: "right",
                fontSize: 10,
                fill: "#6b7280",
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Footer Insight */}
      <p className="text-xs text-gray-500 text-center mt-2">
        Ensemble smooths individual model spikes, improving stability and reducing false positives
      </p>
    </div>
  );
}

export default EnsembleVsBestModelChart;
