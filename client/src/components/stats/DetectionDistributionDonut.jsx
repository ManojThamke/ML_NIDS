import React from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

/**
 * Enhanced Detection Distribution Donut
 * Features: Dashboard-matched glowing shadows, centered intelligence, and theme-adaptive labels.
 */
function DetectionDistributionDonut({ data, theme = 'light' }) {
  const attack = data?.attack ?? 0;
  const benign = data?.benign ?? 0;

  // 🎨 Semantic Palette
  const COLORS = {
    Benign: theme === 'dark' ? "#10b981" : "#10b981", // Emerald
    Attack: theme === 'dark' ? "#ef4444" : "#f43f5e", // Rose/Red
  };

  const total = attack + benign;
  const attackPercent = total > 0 ? ((attack / total) * 100).toFixed(1) : "0.0";

  const chartData = [
    { name: "Benign", value: benign === 0 ? 0.0001 : benign },
    { name: "Attack", value: attack === 0 ? 0.0001 : attack },
  ];

  // 🔹 Dashboard Shadow Logic
  const containerStyle = theme === 'light' 
    ? "bg-white border-slate-100 shadow-[0_20px_50px_rgba(79,70,229,0.08)] shadow-indigo-100/40 text-slate-800"
    : "bg-slate-900 border-slate-800 shadow-[0_20px_60px_rgba(0,0,0,0.6)] shadow-black text-slate-100";

  /* High-Contrast Tooltip */
  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;
    const { name, value } = payload[0];
    return (
      <div className="bg-slate-900/95 backdrop-blur-md border border-slate-700 p-3 rounded-xl shadow-2xl animate-in zoom-in-95 duration-200">
        <p className={`text-[10px] font-black uppercase tracking-widest mb-1 ${name === 'Attack' ? 'text-rose-400' : 'text-emerald-400'}`}>
          {name} Payload
        </p>
        <p className="text-sm font-black text-white">{Math.round(value).toLocaleString()} <small className="opacity-50">ALERTS</small></p>
      </div>
    );
  };

  return (
    <div className={`${containerStyle} rounded-[2.5rem] p-8 h-[380px] flex flex-col transition-all duration-700 animate-in fade-in zoom-in-95`}>
      
      {/* 🚀 Header */}
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="text-sm font-black uppercase tracking-[0.2em] opacity-80">
            Threat Landscape
          </h3>
          <p className="text-[11px] font-bold text-indigo-500/70 uppercase tracking-widest mt-1">
            Hybrid Detection Distribution
          </p>
        </div>
        <div className="p-2 bg-rose-500/10 rounded-xl">
           <div className={`w-2 h-2 rounded-full ${attack > 0 ? 'bg-rose-500 animate-pulse' : 'bg-emerald-500'}`} />
        </div>
      </div>

      {/* 🍩 Donut Matrix */}
      <div className="flex-1 flex items-center justify-center relative min-h-0">
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              cx="50%"
              cy="50%"
              innerRadius={75}
              outerRadius={95}
              paddingAngle={4}
              cornerRadius={8}
              startAngle={90}
              endAngle={-270}
              stroke="transparent"
              isAnimationActive
              animationDuration={1800}
            >
              {chartData.map((entry) => (
                <Cell 
                  key={entry.name} 
                  fill={COLORS[entry.name]} 
                  className="transition-all duration-500 cursor-pointer outline-none"
                  style={{ filter: `drop-shadow(0 4px 12px ${COLORS[entry.name]}33)` }}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>

        {/* 🎯 Centered Intelligence Ratio */}
        <div className="absolute flex flex-col items-center justify-center pointer-events-none">
          <p className={`text-4xl font-black tracking-tighter ${attack > 0 ? 'text-rose-600' : 'text-emerald-500'}`}>
            {attackPercent}<small className="text-lg opacity-60">%</small>
          </p>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
            Attack Ratio
          </p>
        </div>
      </div>

      {/* 📊 Legend & Insight */}
      <div className="mt-4 space-y-4">
        <div className="flex justify-center items-center gap-6">
          <LegendItem color={COLORS.Attack} label="Threats" value={attack} theme={theme} />
          <div className="h-4 w-[1px] bg-slate-200 dark:bg-slate-800" />
          <LegendItem color={COLORS.Benign} label="Safe" value={benign} theme={theme} />
        </div>
        
        <p className="text-[10px] font-black text-center uppercase tracking-widest opacity-40 italic border-t dark:border-slate-800 pt-3">
          Proportional volume of benign versus anomalous traffic signatures
        </p>
      </div>
    </div>
  );
}

/* Helper Components */
function LegendItem({ color, label, value, theme }) {
  return (
    <div className="flex items-center gap-2">
      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color, boxShadow: `0 0 8px ${color}` }} />
      <span className={`text-[11px] font-black uppercase tracking-tight ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>
        {label}: <span className={theme === 'dark' ? 'text-white' : 'text-slate-900'}>{value.toLocaleString()}</span>
      </span>
    </div>
  );
}

export default DetectionDistributionDonut;