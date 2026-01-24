import { useEffect, useState, useMemo } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { getLogs } from "../../api";

function AttackConfidenceArea() {
  const [data, setData] = useState([]);

  /* ================= FETCH RECENT CONFIDENCE ================= */
  useEffect(() => {
    let mounted = true;

    const fetchData = async () => {
      try {
        const res = await getLogs({ page: 1, limit: 20 });
        if (!mounted) return;

        const formatted = res.data.logs
          .slice()
          .reverse() // oldest → newest
          .map((log, index) => ({
            index: index + 1,
            confidence: Number(log.confidence ?? 0),
          }));

        setData(formatted);
      } catch (err) {
        console.error("AttackConfidenceArea error:", err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  /* ================= DYNAMIC Y-AXIS ================= */
  const maxConfidence = useMemo(() => {
    return Math.max(...data.map((d) => d.confidence), 0);
  }, [data]);

  // Zoom when benign, expand when attack appears
  const yMax =
    maxConfidence < 0.1 ? 0.1 :
    maxConfidence < 0.3 ? 0.4 :
    1;

  /* ================= FORCE REMOUNT FOR ANIMATION ================= */
  const chartKey = data.length; // guarantees animation on refresh

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border h-[340px]">
      <h3 className="font-semibold mb-4 text-gray-700">
        Ensemble Confidence Trend
      </h3>

      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={data} key={chartKey}>
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
            domain={[0, yMax]}
            tickFormatter={(v) => `${Math.round(v * 100)}%`}
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 11, fill: "#6b7280" }}
          />

          <Tooltip
            formatter={(value) => `${(value * 100).toFixed(2)}%`}
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
            <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#ef4444" stopOpacity={0.45} />
              <stop offset="70%" stopColor="#ef4444" stopOpacity={0.2} />
              <stop offset="100%" stopColor="#ef4444" stopOpacity={0.05} />
            </linearGradient>
          </defs>

          <Area
            type="monotone"
            dataKey="confidence"
            stroke="#ef4444"
            strokeWidth={3}
            fill="url(#confidenceGradient)"
            isAnimationActive={true}
            animationDuration={1200}
            animationEasing="ease-out"
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Context hint */}
      <p className="mt-2 text-xs text-gray-500">
        {yMax < 1
          ? "Zoomed view for benign traffic (low confidence)"
          : "Expanded view due to high confidence activity"}
      </p>
    </div>
  );
}

export default AttackConfidenceArea;
