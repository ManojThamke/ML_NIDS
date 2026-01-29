import React, { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from "recharts";
import { getAlertTopDestinations } from "../../api";

/**
 * TopAttackedDestinationsChart V3.0
 * Fully integrated with Shadow-Glow architecture and theme-adaptive depth.
 */
function TopAttackedDestinationsChart({ theme = 'light' }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  // 🎨 Semantic Risk Palette (matching forensic grid)
  const RED_GRADIENT = theme === 'dark' 
    ? ["#f43f5e", "#ef4444", "#f87171", "#fb7185", "#fda4af"] 
    : ["#dc2626", "#ef4444", "#f87171", "#fca5a5", "#fee2e2"];

  // 🔹 Dashboard Shadow Architecture
  const containerStyle = theme === 'light' 
    ? "bg-white border-slate-100 shadow-[0_20px_50px_rgba(79,70,229,0.08)] shadow-indigo-100/40 text-slate-800"
    : "bg-slate-900 border-slate-800 shadow-[0_20px_60px_rgba(0,0,0,0.6)] shadow-black text-slate-100";

  useEffect(() => {
    getAlertTopDestinations()
      .then((res) => {
        setData(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Forensic Retrieval Failure:", err);
        setLoading(false);
      });
  }, []);

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload.length) return null;
    const { destination, count } = payload[0].payload;

    return (
      <div className="bg-slate-900/95 backdrop-blur-md border border-slate-700 rounded-2xl px-4 py-3 shadow-2xl animate-in zoom-in-95 duration-200">
        <p className="text-[10px] uppercase tracking-[0.2em] font-black text-indigo-400 mb-1">Target Identity</p>
        <p className="text-sm font-black text-white mb-2 italic tabular-nums">{destination}</p>
        <div className="flex items-center gap-3 border-t border-slate-800 pt-2">
          <div className="w-2 h-2 rounded-full bg-rose-500 animate-pulse shadow-[0_0_8px_rgba(244,63,94,0.6)]" />
          <p className="text-xs text-slate-300 font-bold">
            Incidents: <span className="text-white font-black">{count.toLocaleString()}</span>
          </p>
        </div>
      </div>
    );
  };

  if (loading || !data.length) {
    return (
      <div className={`${containerStyle} rounded-[2.5rem] p-8 h-[380px] flex items-center justify-center transition-all duration-700 animate-pulse`}>
        <div className="text-center space-y-3">
           <div className="w-10 h-10 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mx-auto" />
           <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
             {loading ? "Decrypting Target Vectors..." : "No Active Threats Detected"}
           </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${containerStyle} rounded-[2.5rem] p-6 h-[380px] flex flex-col transition-all duration-700 hover:scale-[1.01] group relative overflow-hidden`}>
      
      {/* 🚀 Header: Risk Profiling */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="font-black text-slate-800 dark:text-white text-lg tracking-tighter uppercase">
            Target Vulnerability Matrix
          </h3>
          <p className="text-[10px] text-indigo-500 font-black uppercase tracking-[0.3em]">Asset Risk Profiling</p>
        </div>
        <div className="bg-rose-500/10 px-3 py-1.5 rounded-xl border border-rose-500/20 shadow-sm flex items-center gap-2">
           <div className="w-1.5 h-1.5 rounded-full bg-rose-600 animate-pulse" />
           <span className="text-[9px] font-black text-rose-600 uppercase tracking-widest">Live Threat Intel</span>
        </div>
      </div>

      {/* 📊 Matrix Rendering Area */}
      <div className="flex-grow w-full overflow-hidden">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 40, left: 10, bottom: 5 }}
            barCategoryGap="25%"
          >
            <CartesianGrid horizontal={false} strokeDasharray="4 4" stroke={theme === 'dark' ? "#1e293b" : "#f1f5f9"} />
            <XAxis type="number" hide />
            <YAxis
              type="category"
              dataKey="destination"
              width={100}
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10, fill: theme === 'dark' ? "#64748b" : "#94a3b8", fontWeight: 800, fontStyle: 'italic' }}
            />
            <Tooltip 
              content={<CustomTooltip />} 
              cursor={{ fill: theme === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(79,70,229,0.03)', radius: 12 }}
            />
            <Bar
              dataKey="count"
              radius={[0, 12, 12, 0]}
              animationDuration={2500}
              animationEasing="ease-in-out"
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={RED_GRADIENT[index % RED_GRADIENT.length]}
                  className="transition-all duration-500 hover:opacity-80 cursor-crosshair"
                  style={{ filter: `drop-shadow(0 4px 10px ${RED_GRADIENT[index % RED_GRADIENT.length]}44)` }}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 📑 Footer: Technical Baseline */}
      <div className={`mt-4 pt-4 border-t ${theme === 'dark' ? 'border-slate-800' : 'border-slate-50'} w-full`}>
        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest text-center opacity-60 italic">
          Categorizing network infrastructure based on cumulative incident frequency
        </p>
      </div>
    </div>
  );
}

export default TopAttackedDestinationsChart;