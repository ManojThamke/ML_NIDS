import React from "react";
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

/**
 * Enhanced Confidence Distribution Chart
 * Features: Dashboard-matched shadows, glowing bars, and adaptive mesh background.
 */
function ConfidenceBandsChart({ data, theme = 'light' }) {
  
  // 🎨 Semantic Intelligence Palette
  const BAND_COLORS = {
    "0–20%": theme === 'dark' ? "#10b981" : "#bbf7d0",   // Very safe
    "20–40%": theme === 'dark' ? "#34d399" : "#86efac",  // Low risk
    "40–60%": theme === 'dark' ? "#fbbf24" : "#fde68a",  // Uncertain
    "60–80%": theme === 'dark' ? "#f87171" : "#fca5a5",  // Suspicious
    "80–100%": theme === 'dark' ? "#ef4444" : "#f43f5e"  // High risk
  };

  // 🔹 Dashboard Shadow Architecture
  const containerStyle = theme === 'light' 
    ? "bg-white border-slate-100 shadow-[0_20px_50px_rgba(79,70,229,0.08)] shadow-indigo-100/40 text-slate-800"
    : "bg-slate-900 border-slate-800 shadow-[0_20px_60px_rgba(0,0,0,0.6)] shadow-black text-slate-100";

  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className={`${containerStyle} rounded-[2rem] p-8 flex items-center justify-center h-[380px]`}>
        <p className="text-sm font-black uppercase tracking-widest opacity-40 italic">Waiting for forensic datastream...</p>
      </div>
    );
  }

  /* Sophisticated Forensic Tooltip */
  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload.length) return null;
    const { range, count } = payload[0].payload;
    return (
      <div className="bg-slate-900/95 backdrop-blur-md border border-slate-700 p-4 rounded-2xl shadow-2xl animate-in zoom-in-95 duration-200">
        <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-1">Confidence Matrix</p>
        <div className="flex items-center gap-4">
          <span className="text-sm font-bold text-white">{range}</span>
          <div className="h-4 w-[1px] bg-slate-700" />
          <span className="text-sm font-black text-indigo-300">{count.toLocaleString()} <small className="text-[9px] font-bold opacity-60">ALERTS</small></span>
        </div>
      </div>
    );
  };

  return (
    <div className={`${containerStyle} rounded-[2.5rem] p-8 h-[380px] flex flex-col transition-all duration-700`}>
      
      {/* 🚀 Header Logic */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-sm font-black uppercase tracking-[0.2em] opacity-80">
            Certainty Distribution
          </h3>
          <p className="text-[11px] font-bold text-indigo-500/70 uppercase tracking-widest mt-1">
            Historical Confidence Delta Matrix
          </p>
        </div>
        <div className="p-2 bg-indigo-500/10 rounded-xl">
           <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
        </div>
      </div>

      {/* 📊 Chart Matrix */}
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid 
              vertical={false} 
              strokeDasharray="4 4" 
              stroke={theme === 'dark' ? "#1e293b" : "#f1f5f9"} 
            />
            
            <XAxis 
              dataKey="range" 
              axisLine={false} 
              tickLine={false}
              tick={{ fontSize: 10, fontStyle: 'italic', fontWeight: 800, fill: theme === 'dark' ? "#64748b" : "#94a3b8" }}
              dy={10}
            />
            
            <YAxis 
              axisLine={false} 
              tickLine={false}
              tick={{ fontSize: 10, fontWeight: 800, fill: theme === 'dark' ? "#64748b" : "#94a3b8" }}
            />
            
            <Tooltip 
              content={<CustomTooltip />} 
              cursor={{ fill: theme === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(79,70,229,0.03)', radius: 10 }}
            />

            <Bar 
              dataKey="count" 
              radius={[10, 10, 0, 0]} 
              barSize={32}
              animationDuration={2000}
              animationEasing="ease-out"
            >
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={BAND_COLORS[entry.range]}
                  className="transition-all duration-500 hover:opacity-80"
                  style={{ filter: `drop-shadow(0 4px 6px ${BAND_COLORS[entry.range]}44)` }}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 📑 Analytics Caption */}
      <div className={`mt-6 pt-4 border-t ${theme === 'dark' ? 'border-slate-800' : 'border-slate-50'}`}>
        <p className="text-[10px] font-black text-center uppercase tracking-widest opacity-50 italic">
          Higher bands indicate robust model agreement on forensic classifications
        </p>
      </div>
    </div>
  );
}

export default ConfidenceBandsChart;