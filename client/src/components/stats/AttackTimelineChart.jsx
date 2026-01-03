import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

function AttackTimelineChart({ data }) {
  // 🛡️ Hard guard
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border h-[380px] flex items-center justify-center">
        <p className="text-sm text-gray-400">
          No attack activity detected in this period
        </p>
      </div>
    );
  }

  // 🔧 Ensure baseline exists
  const normalizedData =
    data.length === 1
      ? [{ ...data[0], attacks: 0 }, data[0]]
      : data;

  // 🔧 Compute safe Y max
  const maxAttacks = Math.max(...normalizedData.map((d) => d.attacks || 0));
  const yMax = Math.max(5, maxAttacks + 1);

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px] flex flex-col">
      <h3 className="font-semibold text-gray-700 mb-2">
        Attack Timeline
      </h3>

      {/* 🔥 Fixed-height chart area */}
      <div className="h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={normalizedData}>
            <defs>
              {/* Smooth gradient fill */}
              <linearGradient id="attackGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#fca5a5" stopOpacity={0.6} />
                <stop offset="100%" stopColor="#fee2e2" stopOpacity={0.08} />
              </linearGradient>
            </defs>

            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke="#e5e7eb"
            />

            <XAxis
              dataKey="time"
              tick={{ fontSize: 11, fill: "#6b7280" }}
              tickMargin={6}
            />

            <YAxis
              domain={[0, yMax]}
              allowDecimals={false}
              tick={{ fontSize: 11, fill: "#6b7280" }}
              padding={{ top: 18 }}
            />

            <Tooltip
              content={({ active, payload, label }) => {
                if (!active || !payload || !payload.length) return null;
                return (
                  <div className="bg-white border rounded-lg px-4 py-2 shadow-lg">
                    <p className="text-sm font-semibold text-gray-700 mb-1">
                      {label}
                    </p>
                    <p className="text-sm text-gray-600">
                      Attacks:{" "}
                      <span className="font-semibold">
                        {payload[0].value}
                      </span>
                    </p>
                  </div>
                );
              }}
            />

            <Area
              type="monotone"
              dataKey="attacks"
              stroke="#ef4444"
              strokeWidth={2}
              fill="url(#attackGradient)"
              dot={{ r: 3, fill: "#ef4444" }}
              activeDot={{ r: 5 }}
              connectNulls
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Explanation line */}
      <p className="-mt-2 text-sm text-gray-600 text-center leading-snug">
        Spikes indicate abnormal or suspicious traffic over time.
      </p>
    </div>
  );
}

export default AttackTimelineChart;
