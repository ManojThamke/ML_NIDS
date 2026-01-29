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
import { getDetectionTimeline } from "../../api";

const ranges = [
  { label: "1H", value: "1h" },
  { label: "2H", value: "2h" },
  { label: "24H", value: "24h" },
  { label: "7D", value: "7d" },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="bg-gray-900/95 backdrop-blur-md border border-gray-700 rounded-xl px-4 py-3 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
      <p className="text-[10px] uppercase tracking-widest font-bold text-gray-400 mb-1">
        {new Date(label).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
      </p>
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
        <p className="text-sm text-white font-medium">
          Traffic: <span className="font-bold text-indigo-300">{payload[0].value.toLocaleString()}</span>
        </p>
      </div>
    </div>
  );
};

function TrafficTimelineChart() {
  const [range, setRange] = useState("24h");
  const [data, setData] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const fetchTimeline = useCallback(async () => {
    try {
      setRefreshing(true);
      const res = await getDetectionTimeline(range);
      setData(res.data);
    } catch (err) {
      console.error("Timeline fetch failed:", err);
    } finally {
      setTimeout(() => setRefreshing(false), 800);
    }
  }, [range]);

  useEffect(() => { fetchTimeline(); }, [fetchTimeline]);

  useEffect(() => {
    const interval = setInterval(fetchTimeline, 10000);
    return () => clearInterval(interval);
  }, [fetchTimeline]);

  return (
    /* Unified h-[380px] to match TopAttackedDestinationsChart */
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 h-[380px] flex flex-col transition-all hover:shadow-xl group animate-fade-in">
      
      {/* 1. Header Area - Standardized h-[60px] internally via flex */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-bold text-gray-800 text-lg tracking-tight flex items-center gap-2">
            Traffic Timeline
            {refreshing && <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-ping" />}
          </h3>
          <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Temporal Analysis Engine</p>
        </div>

        <div className="flex bg-gray-50 p-1 rounded-xl border border-gray-100 shadow-sm">
          {ranges.map((r) => (
            <button
              key={r.value}
              onClick={() => setRange(r.value)}
              className={`px-3 py-1.5 rounded-lg text-[10px] font-black tracking-tighter transition-all
                ${range === r.value 
                  ? "bg-white text-indigo-600 shadow-sm border border-gray-200" 
                  : "text-gray-400 hover:text-gray-600"}`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {/* 2. Main Chart Area - flex-grow ensures matching height with sibling chart */}
      <div className="flex-grow w-full overflow-hidden">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="timelineGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="#f1f5f9" />

            <XAxis
              dataKey="timestamp"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10, fill: "#94a3b8", fontWeight: 600 }}
              tickFormatter={(v) => new Date(v).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            />

            <YAxis
              allowDecimals={false}
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10, fill: "#94a3b8", fontWeight: 600 }}
              padding={{ top: 20 }}
            />

            <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#e2e8f0', strokeWidth: 2 }} />

            <Area
              type="monotone"
              dataKey="count"
              stroke="#6366f1"
              strokeWidth={3}
              fill="url(#timelineGradient)"
              isAnimationActive={true}
              animationDuration={2000}
              animationEasing="ease-in-out"
              activeDot={{ r: 6, strokeWidth: 0, fill: "#4338ca" }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* 3. Refined Footer - Matches TopAttackedDestinationsChart */}
      <div className="mt-2 pt-3 border-t border-gray-100 flex justify-between items-center">
        <p className="text-[10.5px] text-gray-400 font-medium italic">
          Live stream from active network interface
        </p>
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]" />
          <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">System Sync: OK</span>
        </div>
      </div>
    </div>
  );
}

export default TrafficTimelineChart;