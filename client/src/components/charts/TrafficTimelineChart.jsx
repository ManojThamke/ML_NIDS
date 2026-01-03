import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { useEffect, useState, useCallback } from "react";
import { getTrafficTimeline } from "../../api";

const ranges = [
  { label: "1H", value: "1h" },
  { label: "2H", value: "2h" },
  { label: "24H", value: "24h" },
  { label: "7D", value: "7d" },
  { label: "30D", value: "30d" },
  { label: "1Y", value: "1y" },
];

/* Clean tooltip */
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="bg-white border rounded-lg px-4 py-2 shadow-lg">
      <p className="text-sm font-semibold text-gray-700 mb-1">
        {new Date(label).toLocaleString()}
      </p>
      <p className="text-sm text-gray-600">
        Traffic Count:{" "}
        <span className="font-semibold">{payload[0].value}</span>
      </p>
    </div>
  );
};

function TrafficTimelineChart() {
  const [range, setRange] = useState("24h");
  const [data, setData] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  /* ================= FETCH TIMELINE ================= */
  const fetchTimeline = useCallback(async () => {
    try {
      setRefreshing(true);
      const res = await getTrafficTimeline(range);
      setData(res.data);
    } catch (err) {
      console.error("Timeline fetch failed:", err);
    } finally {
      setRefreshing(false);
    }
  }, [range]);

  /* ================= INITIAL LOAD ================= */
  useEffect(() => {
    fetchTimeline();
  }, [fetchTimeline]);

  /* ================= AUTO REFRESH ================= */
  useEffect(() => {
    const interval = setInterval(fetchTimeline, 2000);
    return () => clearInterval(interval);
  }, [fetchTimeline]);

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px] flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-semibold text-gray-700">
          Traffic Timeline
        </h3>

        {/* Range Selector */}
        <div className="flex gap-2">
          {ranges.map((r) => (
            <button
              key={r.value}
              onClick={() => setRange(r.value)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition
                ${
                  range === r.value
                    ? "bg-pink-500 text-white"
                    : "border text-gray-600 hover:bg-pink-50"
                }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {/* Refresh Indicator (no layout shift) */}
      <p
        className={`text-xs text-gray-400 mb-1 transition-opacity duration-200
          ${refreshing ? "opacity-100 animate-pulse" : "opacity-0"}
        `}
      >
        Updating timeline…
      </p>

      {/* 🔥 Fixed-height chart area */}
      <div className="h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="timelineGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#fca5a5" stopOpacity={0.6} />
                <stop offset="70%" stopColor="#fecaca" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#fee2e2" stopOpacity={0.1} />
              </linearGradient>
            </defs>

            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke="#e5e7eb"
            />

            <XAxis
              dataKey="timestamp"
              tick={{ fontSize: 11, fill: "#6b7280" }}
              tickFormatter={(v) =>
                new Date(v).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })
              }
            />

            <YAxis
              allowDecimals={false}
              tick={{ fontSize: 11, fill: "#6b7280" }}
              padding={{ top: 18 }}
            />

            <Tooltip content={<CustomTooltip />} />

            <Area
              type="monotone"
              dataKey="count"
              stroke="#ef4444"
              strokeWidth={3}
              fill="url(#timelineGradient)"
              isAnimationActive
              animationDuration={700}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Explanation line */}
      <p className="-mt-2 text-sm text-gray-600 text-center leading-snug">
        Displays network traffic volume over time with live updates.
      </p>
    </div>
  );
}

export default TrafficTimelineChart;
