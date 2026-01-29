import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
  LabelList,
} from "recharts";

/**
 * Enhanced Model Dominance Chart
 * Features: Adaptive highlights, semantic drop-shadows, and staggered NOC typography.
 */
function ModelDominanceFrequencyChart({ data, theme = 'light' }) {
  
  // 🎨 Semantic Model Palette
  const MODEL_COLORS = {
    RandomForest: "#60a5fa",
    GradientBoosting: "#fbbf24",
    DecisionTree: "#94a3b8",
    KNN: "#f472b6",
    LightGBM: "#818cf8",
    MLP: "#a78bfa",
    XGBoost: "#10b981",
    NaiveBayes: "#f87171",
    LogisticRegression: "#cbd5e1",
  };

  const MODEL_LABELS = {
    RandomForest: "Random Forest",
    GradientBoosting: "Grad Boost",
    DecisionTree: "Decision Tree",
    LightGBM: "LightGBM",
    XGBoost: "XGBoost",
    KNN: "KNN",
    MLP: "MLP",
    NaiveBayes: "Naive Bayes",
    LogisticRegression: "Log Reg",
  };

  // 🔹 Dashboard Shadow Architecture
  const containerStyle = theme === 'light' 
    ? "bg-white border-slate-100 shadow-[0_20px_50px_rgba(79,70,229,0.08)] shadow-indigo-100/40 text-slate-800"
    : "bg-slate-900 border-slate-800 shadow-[0_20px_60px_rgba(0,0,0,0.6)] shadow-black text-slate-100";

  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className={`${containerStyle} rounded-[2.5rem] p-8 flex items-center justify-center h-[380px]`}>
        <p className="text-sm font-black uppercase tracking-widest opacity-40 italic">Waiting for dominance telemetry...</p>
      </div>
    );
  }

  const dominant = data.reduce((a, b) => b.percent > a.percent ? b : a);

  /* Sophisticated Forensic Tooltip */
  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;
    const { model, percent } = payload[0].payload;
    return (
      <div className="bg-slate-900/95 backdrop-blur-md border border-slate-700 p-4 rounded-2xl shadow-2xl animate-in zoom-in-95 duration-200">
        <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-1">Ensemble Influence</p>
        <div className="flex flex-col gap-1">
          <span className="text-sm font-bold text-white">{MODEL_LABELS[model] || model}</span>
          <div className="h-[1px] w-full bg-slate-700 my-1" />
          <span className="text-sm font-black text-indigo-300">{percent}% <small className="text-[9px] font-bold opacity-60 uppercase">Dominance</small></span>
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
            Model Dominance Matrix
          </h3>
          <p className="text-[11px] font-bold text-indigo-500/70 uppercase tracking-widest mt-1">
            Ensemble Decision Frequency Delta
          </p>
        </div>
        <div className="p-2 bg-emerald-500/10 rounded-xl">
           <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        </div>
      </div>

      {/* 📊 Chart Matrix */}
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid 
              vertical={false} 
              strokeDasharray="4 4" 
              stroke={theme === 'dark' ? "#1e293b" : "#f1f5f9"} 
            />
            
            <XAxis 
              dataKey="model" 
              axisLine={false} 
              tickLine={false}
              interval={0}
              tick={({ x, y, payload }) => (
                <g transform={`translate(${x},${y + 12})`}>
                  <text 
                    textAnchor="middle" 
                    fill={theme === 'dark' ? "#64748b" : "#94a3b8"} 
                    fontSize={9} 
                    fontWeight={800}
                    className="uppercase tracking-tighter italic"
                  >
                    {MODEL_LABELS[payload.value] || payload.value}
                  </text>
                </g>
              )}
            />

            <YAxis 
              domain={[0, 100]}
              axisLine={false} 
              tickLine={false}
              tick={{ fontSize: 10, fontWeight: 800, fill: theme === 'dark' ? "#64748b" : "#94a3b8" }}
              tickFormatter={(v) => `${v}%`}
            />
            
            <Tooltip 
              content={<CustomTooltip />} 
              cursor={{ fill: theme === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(79,70,229,0.03)', radius: 12 }}
            />

            <Bar 
              dataKey="percent" 
              radius={[12, 12, 0, 0]} 
              barSize={28}
              animationDuration={2000}
              animationEasing="ease-out"
            >
              {data.map((entry, index) => {
                const isTop = entry.model === dominant.model;
                return (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={MODEL_COLORS[entry.model]}
                    fillOpacity={isTop ? 1 : 0.6}
                    className="transition-all duration-500 hover:fill-opacity-90"
                    style={{ filter: isTop ? `drop-shadow(0 6px 12px ${MODEL_COLORS[entry.model]}66)` : 'none' }}
                  />
                );
              })}
              
              <LabelList 
                dataKey="percent" 
                position="top" 
                formatter={(v) => `${v}%`} 
                fontSize={10} 
                fontWeight={900}
                fill={theme === 'dark' ? "#94a3b8" : "#64748b"}
                dy={-10}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 📑 Footer Caption */}
      <div className={`mt-6 pt-4 border-t ${theme === 'dark' ? 'border-slate-800' : 'border-slate-50'}`}>
        <p className="text-[10px] font-black text-center uppercase tracking-widest opacity-50 italic">
          Highlighting primary model dominance within the ensemble classification engine
        </p>
      </div>
    </div>
  );
}

export default ModelDominanceFrequencyChart;