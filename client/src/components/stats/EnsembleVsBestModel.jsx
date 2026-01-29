import React from "react";
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
  AreaChart,
  ComposedChart
} from "recharts";

/**
 * Enhanced Ensemble Comparison Chart
 * Features: Dashboard-matched shadows, gradient area fills, and high-density NOC typography.
 */
function EnsembleVsBestModelChart({ data, theme = 'light' }) {
  
  // 🔹 Dashboard Shadow Architecture
  const containerStyle = theme === 'light' 
    ? "bg-white border-slate-100 shadow-[0_20px_50px_rgba(79,70,229,0.08)] shadow-indigo-100/40 text-slate-800"
    : "bg-slate-900 border-slate-800 shadow-[0_20px_60px_rgba(0,0,0,0.6)] shadow-black text-slate-100";

  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className={`${containerStyle} rounded-[2.5rem] p-8 flex items-center justify-center h-[500px]`}>
        <p className="text-sm font-black uppercase tracking-widest opacity-40 italic">Waiting for ensemble telemetry...</p>
      </div>
    );
  }

  const clamp = (v) => Math.min(Math.max(v, 0), 100);

  const safeData = data.map((d) => ({
    ...d,
    bestModelConfidence: clamp(d.bestModelConfidence),
    ensembleConfidence: clamp(d.ensembleConfidence),
  }));

  /* Sophisticated Forensic Tooltip */
  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="bg-slate-900/95 backdrop-blur-md border border-slate-700 p-4 rounded-2xl shadow-2xl animate-in zoom-in-95 duration-200">
        <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2 border-b border-slate-800 pb-1">Telemetry Node #{payload[0].payload.index}</p>
        <div className="space-y-2">
          <div className="flex items-center justify-between gap-4">
            <span className="text-[11px] font-bold text-slate-400 uppercase">Ensemble</span>
            <span className="text-sm font-black text-indigo-400">{payload[1].value}%</span>
          </div>
          <div className="flex items-center justify-between gap-4">
            <span className="text-[11px] font-bold text-slate-400 uppercase">Best Individual</span>
            <span className="text-sm font-black text-rose-400">{payload[0].value}%</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={`${containerStyle} rounded-[2.5rem] p-8 h-[550px] flex flex-col transition-all duration-700 animate-in fade-in slide-in-from-bottom-4`}>
      
      {/* 🚀 Header Logic */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-sm font-black uppercase tracking-[0.2em] opacity-80">
            Ensemble Decision Stability
          </h3>
          <p className="text-[11px] font-bold text-indigo-500/70 uppercase tracking-widest mt-1">
            Hybrid Consensus vs Singular Model Performance
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="p-2 bg-indigo-500/10 rounded-xl">
             <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
          </div>
        </div>
      </div>

      {/* 📊 Chart Matrix */}
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={safeData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
            <defs>
              <linearGradient id="ensembleGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.15}/>
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
              </linearGradient>
            </defs>
            
            <CartesianGrid 
              vertical={false} 
              strokeDasharray="4 4" 
              stroke={theme === 'dark' ? "#1e293b" : "#f1f5f9"} 
            />
            
            <XAxis 
              dataKey="index" 
              axisLine={false} 
              tickLine={false}
              tick={{ fontSize: 10, fontWeight: 800, fill: theme === 'dark' ? "#64748b" : "#94a3b8" }}
              label={{ value: "DETECTION INDEX SEQUENCE", position: "bottom", offset: 0, fontSize: 9, fontWeight: 900, fill: "#6366f1", opacity: 0.6 }}
            />
            
            <YAxis 
              domain={[0, 100]}
              axisLine={false} 
              tickLine={false}
              tick={{ fontSize: 10, fontWeight: 800, fill: theme === 'dark' ? "#64748b" : "#94a3b8" }}
              tickFormatter={(v) => `${v}%`}
            />
            
            <Tooltip content={<CustomTooltip />} />
            
            <Legend 
              verticalAlign="top" 
              align="right"
              iconType="circle"
              content={({ payload }) => (
                <div className="flex justify-end gap-6 mb-8">
                  {payload.map((entry, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                      <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">{entry.value}</span>
                    </div>
                  ))}
                </div>
              )}
            />

            {/* 🟦 Gradient Area for Ensemble */}
            <Area
              type="monotone"
              dataKey="ensembleConfidence"
              fill="url(#ensembleGradient)"
              stroke="none"
              isAnimationActive={true}
            />

            {/* 🔴 Best Individual Model - Glowing Line */}
            <Line
              type="monotone"
              dataKey="bestModelConfidence"
              stroke="#f43f5e"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name="Best Singular Model"
              animationDuration={2000}
            />

            {/* 🔵 Ensemble Prediction - Bold Primary Line */}
            <Line
              type="monotone"
              dataKey="ensembleConfidence"
              stroke="#6366f1"
              strokeWidth={4}
              dot={false}
              name="Ensemble Aggregator"
              animationDuration={2500}
              style={{ filter: "drop-shadow(0 4px 10px rgba(99,102,241,0.3))" }}
            />

            <ReferenceLine
              y={50}
              stroke={theme === 'dark' ? "#334155" : "#cbd5e1"}
              strokeDasharray="8 8"
              label={{ value: "LOGIC THRESHOLD", position: "right", fill: "#94a3b8", fontSize: 9, fontWeight: 900 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* 📑 Footer Analysis */}
      <div className={`mt-6 pt-4 border-t ${theme === 'dark' ? 'border-slate-800' : 'border-slate-50'}`}>
        <p className="text-[10px] font-black text-center uppercase tracking-widest opacity-50 italic leading-loose">
          Ensemble Aggregator stabilizes predictive variance by weighting model consensus, significantly reducing false positive triggers
        </p>
      </div>
    </div>
  );
}

export default EnsembleVsBestModelChart;