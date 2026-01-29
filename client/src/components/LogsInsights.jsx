import React, { useEffect, useState } from "react";
import { getAlertInsights } from "../api";
import { 
  ShieldAlert, Activity, 
  ArrowUpRight, ArrowDownLeft 
} from "lucide-react";

/**
 * Forensic Insights V5.1 - Professional Matrix
 * Features: Uniform card sizing, staggered animations, and theme-adaptive glow.
 */
function LogsInsights({ theme = 'light' }) {
  const [data, setData] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const themeStyles = {
    light: {
      card: "bg-white border-slate-100 shadow-[0_20px_50px_rgba(79,70,229,0.06)] shadow-indigo-100/30 text-slate-800",
      text: "text-slate-800",
      subtext: "text-slate-400",
      rowHover: "hover:bg-indigo-50/30",
      barBg: "bg-slate-100"
    },
    dark: {
      card: "bg-slate-900 border-slate-800 shadow-[0_20px_60px_rgba(0,0,0,0.5)] shadow-black text-slate-100",
      text: "text-slate-100",
      subtext: "text-slate-500",
      rowHover: "hover:bg-slate-800/50",
      barBg: "bg-slate-800"
    }
  };

  const style = themeStyles[theme] || themeStyles.light;

  const fetchInsights = async (isBackground = false) => {
    try {
      if (isBackground) setRefreshing(true);
      const res = await getAlertInsights();
      setData(res.data);
    } catch (err) {
      console.error("Insights protocol failure:", err);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => { fetchInsights(false); }, []);
  useEffect(() => {
    const interval = setInterval(() => { fetchInsights(true); }, 5000);
    return () => clearInterval(interval);
  }, []);

  if (!data) return null;

  return (
    <div className="space-y-4">
      {/* 🔄 Intelligence Sync Status */}
      <div className="flex items-center gap-2 px-2 h-4">
        {refreshing && (
          <div className="flex items-center gap-2 animate-in fade-in slide-in-from-left-2 duration-300">
            <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
            <span className="text-[9px] font-black uppercase tracking-[0.2em] text-indigo-500/70">Intelligence Re-syncing...</span>
          </div>
        )}
      </div>

      {/* 🔹 Uniform Staggered Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        
        {/* Card 1: Origin Vectors */}
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 fill-mode-both" style={{ animationDelay: '100ms' }}>
          <InsightCard title="Origin Vectors" icon={<ArrowUpRight size={16}/>} themeStyle={style}>
            {data.topSourceIPs.slice(0, 5).map((ip) => (
              <Row key={ip._id} label={ip._id} value={ip.count} themeStyle={style} />
            ))}
          </InsightCard>
        </div>

        {/* Card 2: Target Verticals */}
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 fill-mode-both" style={{ animationDelay: '200ms' }}>
          <InsightCard title="Target Verticals" icon={<ArrowDownLeft size={16}/>} themeStyle={style}>
            {data.topDestinationIPs.slice(0, 5).map((ip) => (
              <Row key={ip._id} label={ip._id} value={ip.count} themeStyle={style} />
            ))}
          </InsightCard>
        </div>

        {/* Card 3: Traffic Matrix */}
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 fill-mode-both" style={{ animationDelay: '300ms' }}>
          <InsightCard title="Traffic Matrix" icon={<Activity size={16}/>} themeStyle={style}>
            <div className="flex flex-col gap-4 mt-1 justify-center h-full">
              <StatBar label="Benign" value={data.benignCount} total={data.benignCount + data.attackCount} color="emerald" themeStyle={style} />
              <StatBar label="Threats" value={data.attackCount} total={data.benignCount + data.attackCount} color="rose" themeStyle={style} />
            </div>
          </InsightCard>
        </div>

        {/* Card 4: Critical Anomalies */}
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 fill-mode-both" style={{ animationDelay: '400ms' }}>
          <InsightCard title="Critical Anomalies" icon={<ShieldAlert size={16}/>} themeStyle={style}>
            <div className="flex flex-col justify-center h-full pb-2">
              <div className="flex items-baseline gap-2">
                <span className="text-6xl font-black tracking-tighter text-rose-600 drop-shadow-sm animate-pulse">
                  {data.highRiskCount}
                </span>
                <span className="text-[10px] font-black text-rose-500/60 uppercase tracking-widest leading-none">Events</span>
              </div>
              <p className={`text-[10px] font-bold mt-3 uppercase tracking-tight ${style.subtext}`}>
                Certainty Threshold <span className="text-indigo-500">≥ 70%</span>
              </p>
            </div>
          </InsightCard>
        </div>

      </div>
    </div>
  );
}

/* ===================== Helper Components ===================== */

/**
 * InsightCard helper with fixed height for uniform layout
 */
function InsightCard({ title, icon, children, themeStyle }) {
  return (
    <div className={`${themeStyle.card} rounded-[2rem] p-6 border transition-all duration-500 h-[190px] flex flex-col hover:scale-[1.02] active:scale-98`}>
      <h3 className="text-[10px] font-black uppercase tracking-[0.25em] mb-4 flex items-center gap-2 opacity-60">
        <span className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-500">{icon}</span>
        {title}
      </h3>
      <div className="flex-1 space-y-1.5 overflow-hidden flex flex-col justify-center">
        {children}
      </div>
    </div>
  );
}

function Row({ label, value, themeStyle }) {
  return (
    <div className={`flex justify-between items-center text-[12px] px-2 py-1 transition-colors group rounded-lg ${themeStyle.rowHover}`}>
      <span className="font-mono font-bold tracking-tighter text-indigo-600/80 group-hover:text-indigo-600 truncate max-w-[70%]">{label}</span>
      <span className={`font-black tabular-nums ${themeStyle.text}`}>{value.toLocaleString()}</span>
    </div>
  );
}

function StatBar({ label, value, total, color, themeStyle }) {
  const percentage = total > 0 ? (value / total) * 100 : 0;
  const colorClass = color === "emerald" ? "bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.3)]" : "bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.3)]";
  
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between items-end">
        <span className="text-[9px] font-black uppercase tracking-widest opacity-50">{label}</span>
        <span className={`text-[11px] font-black tabular-nums ${themeStyle.text}`}>{value.toLocaleString()}</span>
      </div>
      <div className={`w-full h-1.5 rounded-full overflow-hidden ${themeStyle.barBg}`}>
        <div 
          className={`h-full ${colorClass} transition-all duration-1000 ease-out`} 
          style={{ width: `${percentage}%` }} 
        />
      </div>
    </div>
  );
}

export default LogsInsights;