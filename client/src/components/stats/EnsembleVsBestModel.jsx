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

/* 🔒 Clamp helper (absolute safety) */
const clamp = (value, min = 0, max = 100) =>
  Math.min(Math.max(value, min), max);

function EnsembleVsBestModelChart({ data }) {
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border h-[470px] flex items-center justify-center animate-fade-in">
        <p className="text-sm text-gray-400">
          No ensemble comparison data available
        </p>
      </div>
    );
  }

  /* ✅ Sanitize + clamp confidence values */
  const safeData = data.map((d) => ({
    ...d,
    bestModelConfidence: clamp(d.bestModelConfidence),
    ensembleConfidence: clamp(d.ensembleConfidence),
  }));

  /* 🔧 Dynamic Y scale (capped at 100) */
  const maxValue = Math.max(
    ...safeData.map((d) =>
      Math.max(d.bestModelConfidence, d.ensembleConfidence)
    )
  );

  const yMax =
    maxValue < 20 ? 20 :
    maxValue < 50 ? 50 :
    100;

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[600px] flex flex-col animate-fade-in">
      {/* Header */}
      <h3 className="font-semibold text-gray-700">
        Ensemble vs Best Model
      </h3>
      <p className="text-xs text-gray-500 mb-3">
        Ensemble confidence compared with the strongest individual model
      </p>

      {/* Chart */}
      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={safeData}>
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke="#e5e7eb"
            />

            <XAxis
              dataKey="index"
              tick={{ fontSize: 11, fill: "#6b7280" }}
              label={{
                value: "Detection Index",
                position: "insideBottom",
                offset: -5,
                fontSize: 11,
                fill: "#6b7280",
              }}
            />

            <YAxis
              domain={[0, yMax]}
              tickFormatter={(v) => `${v}%`}
              tick={{ fontSize: 11, fill: "#6b7280" }}
            />

            <Tooltip
              formatter={(v) => `${v}%`}
              contentStyle={{
                background: "#111827",
                borderRadius: "10px",
                border: "none",
                color: "#f9fafb",
                fontSize: "12px",
              }}
              labelStyle={{ color: "#9ca3af" }}
            />

            <Legend
              verticalAlign="top"
              height={28}
              wrapperStyle={{ fontSize: "12px" }}
            />

            {/* 🟦 Ensemble confidence band */}
            <Area
              type="monotone"
              dataKey="ensembleConfidence"
              fill="#3b82f6"
              fillOpacity={0.15}
              stroke="none"
              isAnimationActive={false}
            />

            {/* 🔴 Best individual model */}
            <Line
              type="monotone"
              dataKey="bestModelConfidence"
              stroke="#ef4444"
              strokeWidth={2}
              dot={false}
              name="Best Individual Model"
              isAnimationActive
              animationBegin={300}
              animationDuration={1600}
              animationEasing="ease-in-out"
            />

            {/* 🔵 Ensemble */}
            <Line
              type="monotone"
              dataKey="ensembleConfidence"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={false}
              name="Ensemble Prediction"
              isAnimationActive
              animationBegin={300}
              animationDuration={1600}
              animationEasing="ease-in-out"
            />

            {/* ⚠️ Decision threshold */}
            <ReferenceLine
              y={50}
              stroke="#9ca3af"
              strokeDasharray="4 4"
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
      <p className="text-xs text-gray-500 text-center mt-2 leading-snug">
        Ensemble smooths individual model spikes, improving stability and reducing false positives.
      </p>
    </div>
  );
}

export default EnsembleVsBestModelChart;
