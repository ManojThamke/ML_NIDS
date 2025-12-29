import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

function AttackProbabilityArea({ alerts }) {
  const data = alerts.slice(-10).map((a, i) => ({
    index: i + 1,
    probability: a.probability || 0,
  }));

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px]">
      <h3 className="font-semibold mb-4 text-gray-700">
        Recent Attack Probability
      </h3>

      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={data}>
          <CartesianGrid
            strokeDasharray="4 4"
            stroke="#e5e7eb"
            vertical={false}
          />

          <XAxis
            dataKey="index"
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 11, fill: "#6b7280" }}
          />

          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 11, fill: "#6b7280" }}
            domain={[0.02, 0.05]}
          />

          <Tooltip
            cursor={{ stroke: "transparent" }}
            contentStyle={{
              backgroundColor: "#111827",
              borderRadius: "10px",
              border: "none",
              color: "#f9fafb",
              fontSize: "12px",
            }}
            labelStyle={{ color: "#9ca3af" }}
          />

          <defs>
            <linearGradient id="attackGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#ef4444" stopOpacity={0.35} />
              <stop offset="70%" stopColor="#ef4444" stopOpacity={0.2} />
              <stop offset="100%" stopColor="#ef4444" stopOpacity={0.05} />
            </linearGradient>
          </defs>

          <Area
            type="monotone"
            dataKey="probability"
            stroke="#ef4444"
            strokeWidth={3}
            fill="url(#attackGradient)"
            isAnimationActive
            animationDuration={900}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export default AttackProbabilityArea;
