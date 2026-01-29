import React from "react";
import GlobalSecurityOverview from "../components/stats/GlobalSecurityOverview";
import { BarChart3, ShieldCheck, Activity } from "lucide-react";

/**
 * Enhanced Security Statistics Page
 * Features: Centered max-width layout, staggered entrance, and professional NOC typography.
 */
function Stats({ theme = 'light' }) {
  
  // 🔹 Dashboard-Matched Typography Styling
  const titleColor = theme === 'dark' ? "text-white" : "text-slate-900";
  const subtextColor = "text-indigo-500";

  return (
    <div className="p-4 space-y-8 max-w-[1700px] mx-auto animate-in fade-in duration-700">
      
      {/* 🚀 SOPHISTICATED HEADER SECTION */}
      <div className="flex justify-between items-end px-2">
        <div className="flex flex-col">
          <div className="flex items-center gap-3 mb-1">
             <div className="p-2 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-200/50">
                <BarChart3 size={24} className="text-white" />
             </div>
             <h1 className={`text-4xl font-black tracking-tighter ${titleColor}`}>
               Security Statistics
             </h1>
          </div>
          <p className={`text-[11px] font-bold ${subtextColor} uppercase tracking-[0.4em] ml-1 opacity-80`}>
            Real-time Forensic Intelligence Matrix
          </p>
        </div>

        {/* 📊 LIVE INDICATOR BUG */}
        <div className="hidden md:flex items-center gap-4 pb-1">
          <div className="flex flex-col items-end">
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Engine Status</span>
            <div className="flex items-center gap-2">
              <span className="text-[12px] font-black text-emerald-500 uppercase tracking-tight">Active Analysis</span>
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
            </div>
          </div>
        </div>
      </div>

      {/* 🛡️ MAIN ANALYTICS GRID */}
      <div className="relative group">
        {/* Subtle background glow for the entire section */}
        <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500/5 to-purple-500/5 rounded-[3rem] blur-2xl opacity-50 pointer-events-none" />
        
        <GlobalSecurityOverview theme={theme} />
      </div>

      {/* 📑 FOOTER BASELINE */}
      <div className="flex justify-center pt-4 border-t border-slate-100 dark:border-slate-800">
        <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] opacity-50 italic">
          Aggregated Telemetry Data represents ensemble model consensus over 24H observation window
        </p>
      </div>
    </div>
  );
}

export default Stats;