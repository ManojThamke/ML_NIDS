import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

/**
 * Enhanced Attack Timeline Chart
 * Features: Dashboard-matched shadows, glowing area fills, and high-density NOC typography.
 */
function AttackTimelineChart({ data, theme = 'light' }) {
  
  // 🔹 Dashboard Shadow Architecture
  const containerStyle = theme === 'light' 
    ? "bg-white border-slate-100 shadow-[0_20px_50px_rgba(79,70,229,0.08)] shadow-indigo-100/40 text-slate-800"
    : "bg-slate-900 border-slate-800 shadow-[0_20px_60px_rgba(0,0,0,0.6)] shadow-black text-slate-100";

  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className={`${containerStyle} rounded-[2.5rem] p-8 flex items-center justify-center h-[380px]`}>
        <p className="text-sm font-black uppercase tracking-widest opacity-40 italic">Waiting for detection telemetry...</p>
      </div>
    );
  }

  const normalizedData = data.length === 1 ? [{ ...data[0], attacks: 0 }, data[0]] : data;
  const maxAttacks = Math.max(...normalizedData.map((d) => d.attacks || 0));
  const yMax = Math.max(5, maxAttacks + 1);

  /* Sophisticated Forensic Tooltip */
  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload || !payload.length) return null;
    return (
      <div className="bg-slate-900/95 backdrop-blur-md border border-slate-700 p-4 rounded-2xl shadow-2xl animate-in zoom-in-95 duration-200">
        <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-1">Temporal Node</p>
        <div className="flex items-center gap-4">
          <span className="text-sm font-bold text-white italic">{label}</span>
          <div className="h-4 w-[1px] bg-slate-700" />
          <span className="text-sm font-black text-rose-400">
            {payload[0].value.toLocaleString()} <small className="text-[9px] font-bold opacity-60 uppercase">Attacks</small>
          </span>
        </div>
      </div>
    );
  };

  return (
    <div className={`${containerStyle} rounded-[2.5rem] p-8 h-[380px] flex flex-col transition-all duration-700 animate-in fade-in slide-in-from-bottom-4`}>
      
      {/* 🚀 Header Logic */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-sm font-black uppercase tracking-[0.2em] opacity-80">
            Anomaly Temporal Matrix
          </h3>
          <p className="text-[11px] font-bold text-indigo-500/70 uppercase tracking-widest mt-1">
            Real-time Threat Frequency Timeline
          </p>
        </div>
        <div className="p-2 bg-rose-500/10 rounded-xl">
           <div className={`w-2 h-2 rounded-full ${maxAttacks > 0 ? 'bg-rose-500 animate-pulse' : 'bg-emerald-500'}`} />
        </div>
      </div>

      {/* 📊 Chart Matrix */}
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={normalizedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="attackGlow" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#f43f5e" stopOpacity={0}/>
              </linearGradient>
            </defs>

            <CartesianGrid 
              vertical={false} 
              strokeDasharray="4 4" 
              stroke={theme === 'dark' ? "#1e293b" : "#f1f5f9"} 
            />
            
            <XAxis 
              dataKey="time" 
              axisLine={false} 
              tickLine={false}
              tick={{ fontSize: 10, fontStyle: 'italic', fontWeight: 800, fill: theme === 'dark' ? "#64748b" : "#94a3b8" }}
              dy={10}
            />
            
            <YAxis 
              domain={[0, yMax]}
              axisLine={false} 
              tickLine={false}
              tick={{ fontSize: 10, fontWeight: 800, fill: theme === 'dark' ? "#64748b" : "#94a3b8" }}
            />
            
            <Tooltip content={<CustomTooltip />} />

            <Area
              type="monotone"
              dataKey="attacks"
              stroke="#f43f5e"
              strokeWidth={3}
              fill="url(#attackGlow)"
              dot={{ r: 4, fill: "#f43f5e", strokeWidth: 2, stroke: theme === 'dark' ? "#0f172a" : "#fff" }}
              activeDot={{ r: 6, strokeWidth: 0, fill: "#f43f5e", shadow: "0 0 10px rgba(244,63,94,0.5)" }}
              isAnimationActive={true}
              animationDuration={2000}
              style={{ filter: "drop-shadow(0 4px 6px rgba(244,63,94,0.2))" }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* 📑 Analytics Caption */}
      <div className={`mt-6 pt-4 border-t ${theme === 'dark' ? 'border-slate-800' : 'border-slate-50'}`}>
        <p className="text-[10px] font-black text-center uppercase tracking-widest opacity-50 italic leading-snug">
          Amplitude spikes correlate with detected malicious signature clusters over the current observation window
        </p>
      </div>
    </div>
  );
}

export default AttackTimelineChart;