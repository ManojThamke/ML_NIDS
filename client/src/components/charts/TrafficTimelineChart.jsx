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
        <div className="bg-white rounded-xl p-6 shadow-sm border min-h-[380px]">
            <div className="flex-1">
                <ResponsiveContainer width="100%" height="100%">

                    {/* Header */}
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="font-semibold text-gray-700">
                            Traffic Timeline
                        </h3>

                        {/* Range Selector */}
                        <div className="flex gap-2">
                            {ranges.map(r => (
                                <button
                                    key={r.value}
                                    onClick={() => setRange(r.value)}
                                    className={`px-3 py-1 rounded-full text-xs font-medium transition
                ${range === r.value
                                            ? "bg-pink-500 text-white"
                                            : "border text-gray-600 hover:bg-pink-50"
                                        }`}
                                >
                                    {r.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </ResponsiveContainer>
            </div>
            {/* Refresh Indicator */}
            {/* Refresh Indicator (NO LAYOUT SHIFT) */}
            <p
                className={`
                    text-xs text-gray-400 mb-2 transition-opacity duration-200
                    ${refreshing ? "opacity-100 animate-pulse" : "opacity-0"}
                `}
            >
                Updating timeline…
            </p>


            {/* Chart */}
            <ResponsiveContainer width="100%" height={260}>
                <AreaChart data={data}>
                    <CartesianGrid strokeDasharray="4 4" vertical={false} />

                    <XAxis
                        dataKey="timestamp"
                        tickFormatter={(v) =>
                            new Date(v).toLocaleTimeString([], {
                                hour: "2-digit",
                                minute: "2-digit",
                            })
                        }
                    />

                    <YAxis allowDecimals={false} />

                    <Tooltip
                        labelFormatter={(v) =>
                            new Date(v).toLocaleString()
                        }
                        contentStyle={{
                            backgroundColor: "#111827",
                            borderRadius: "10px",
                            border: "none",
                            color: "#f9fafb",
                            fontSize: "12px",
                        }}
                    />

                    {/* Gradient */}
                    <defs>
                        <linearGradient id="timelineGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#ec4899" stopOpacity={0.35} />
                            <stop offset="70%" stopColor="#ec4899" stopOpacity={0.2} />
                            <stop offset="100%" stopColor="#ec4899" stopOpacity={0.05} />
                        </linearGradient>
                    </defs>

                    <Area
                        type="monotone"
                        dataKey="count"
                        stroke="#ec4899"
                        strokeWidth={3}
                        fill="url(#timelineGradient)"
                        isAnimationActive
                        animationDuration={700}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}

export default TrafficTimelineChart;
