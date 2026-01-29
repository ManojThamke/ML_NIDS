import React, { useEffect } from "react";
import PerModelConfidenceChart from "./charts/PerModelConfidenceChart";
import { X, ShieldAlert, Activity, Cpu, Database, Clock, Server } from "lucide-react";

/* ================= THEME-BASED HELPERS ================= */

const labelClass = (label) => {
  if (label === "ATTACK") return "bg-rose-500/10 text-rose-500 border-rose-500/20";
  if (label === "SUSPICIOUS") return "bg-amber-500/10 text-amber-500 border-amber-500/20";
  return "bg-emerald-500/10 text-emerald-500 border-emerald-500/20";
};

const severityClass = (severity) => {
  if (severity === "HIGH") return "bg-rose-600 text-white shadow-lg shadow-rose-900/20";
  if (severity === "MEDIUM") return "bg-amber-400 text-black";
  return "bg-emerald-500 text-white";
};

const confidenceBarClass = (confidence) => {
  if (confidence >= 0.7) return "bg-rose-500";
  if (confidence >= 0.4) return "bg-amber-400";
  return "bg-emerald-500";
};

function LogDetailsModal({ log, onClose, theme = 'light' }) {
  
  useEffect(() => {
    if (!log) return;
    const handleEsc = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [log, onClose]);

  if (!log) return null;

  const themeStyles = {
    light: {
      modal: "bg-white border-slate-200",
      card: "bg-slate-50 border-slate-100",
      innerCard: "bg-white border-slate-100",
      textMain: "text-slate-700",
      textMuted: "text-slate-400"
    },
    dark: {
      modal: "bg-slate-900 border-slate-800",
      card: "bg-slate-950 border-slate-800",
      innerCard: "bg-slate-900 border-slate-800",
      textMain: "text-slate-200",
      textMuted: "text-slate-500"
    },
    contrast: {
      modal: "bg-black border-white border-2",
      card: "bg-black border-white border",
      innerCard: "bg-black border-white border",
      textMain: "text-white",
      textMuted: "text-zinc-400"
    }
  };

  const style = themeStyles[theme];

  return (
    <div
      className="fixed inset-0 z-[2000] bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-300"
      role="dialog"
      aria-modal="true"
      onClick={onClose}
    >
      <div
        className={`rounded-3xl w-full max-w-5xl shadow-2xl relative overflow-hidden animate-in zoom-in-95 duration-300 ${style.modal}`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className={`${theme === 'contrast' ? 'bg-black border-b border-white' : 'bg-slate-950'} px-8 py-4 flex justify-between items-center`}>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-lg text-white">
              <ShieldAlert size={18} />
            </div>
            <h2 className="text-white text-sm font-black uppercase tracking-widest">
              Forensic Analysis // Flow ID: <span className="text-indigo-400 font-mono ml-2">{log._id.slice(-8).toUpperCase()}</span>
            </h2>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X size={24} />
          </button>
        </div>

        <div className="max-h-[85vh] overflow-y-auto p-8 no-scrollbar">
          
          {/* Row 1: Telemetry */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
             {[
               { icon: <Clock size={14} />, label: "Timeline", value: new Date(log.timestamp).toLocaleString() },
               { icon: <Server size={14} />, label: "Flow Origin", value: log.sourceIP },
               { icon: <Activity size={14} />, label: "Confidence", isConfidence: true },
               { icon: <Database size={14} />, label: "Severity", isSeverity: true }
             ].map((item, idx) => (
               <div key={idx} className={`p-4 rounded-2xl border ${style.card}`}>
                  <div className={`flex items-center gap-2 mb-2 ${style.textMuted}`}>
                     {item.icon} <span className="text-[10px] font-black uppercase tracking-tighter">{item.label}</span>
                  </div>
                  {item.isConfidence ? (
                    <div className="flex items-center gap-3">
                      <div className="flex-1 bg-slate-800 h-2 rounded-full overflow-hidden shadow-inner">
                        <div className={`h-full ${confidenceBarClass(log.confidence)}`} style={{ width: `${(log.confidence || 0) * 100}%` }} />
                      </div>
                      <span className={`text-sm font-black italic ${style.textMain}`}>{(log.confidence * 100).toFixed(2)}%</span>
                    </div>
                  ) : item.isSeverity ? (
                    <span className={`px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest ${severityClass(log.severity)}`}>
                       {log.severity}
                    </span>
                  ) : (
                    <p className={`font-mono text-sm font-bold truncate ${style.textMain}`}>{item.value}</p>
                  )}
               </div>
             ))}
          </div>

          <div className="grid grid-cols-12 gap-8">
            {/* Left: Chart */}
            <div className="col-span-12 lg:col-span-7">
              <div className={`rounded-3xl p-6 shadow-sm h-full border ${style.innerCard}`}>
                <div className="flex items-center justify-between mb-6">
                   <h3 className={`text-xs font-black uppercase tracking-[0.2em] ${style.textMuted}`}>Ensemble Consensus Graph</h3>
                   <div className="px-3 py-1 bg-indigo-500/10 text-indigo-400 rounded-full text-[9px] font-black uppercase border border-indigo-500/20">
                      Hybrid Validated
                   </div>
                </div>
                <div className="h-[300px]">
                  <PerModelConfidenceChart modelProbabilities={log.modelProbabilities} theme={theme} />
                </div>
              </div>
            </div>

            {/* Right: Decision + Features */}
            <div className="col-span-12 lg:col-span-5 space-y-4">
               <div className={`${theme === 'contrast' ? 'bg-black border-2 border-white' : 'bg-slate-950'} rounded-3xl p-6 text-white shadow-xl relative overflow-hidden`}>
                  <Cpu size={80} className="absolute -bottom-4 -right-4 text-white/5" />
                  <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-indigo-400 mb-4">Decision Outcome</h3>
                  <div className="space-y-4">
                     {[
                       { label: "ML Model Result", value: log.finalLabel },
                       { label: "Hybrid Overrule", value: log.hybridLabel }
                     ].map((row, idx) => (
                        <div key={idx} className="flex justify-between items-center border-b border-white/10 pb-3">
                           <span className="text-xs font-medium text-slate-400">{row.label}</span>
                           <span className={`px-3 py-1 rounded-md text-[9px] font-black border ${labelClass(row.value)}`}>
                              {row.value}
                           </span>
                        </div>
                     ))}
                     <div className="flex justify-between items-center">
                        <span className="text-xs font-medium text-slate-400">Decision Engine</span>
                        <span className="text-xs font-black text-indigo-400">{log.aggregationMethod || "Weighted Majority"}</span>
                     </div>
                  </div>
               </div>

               {/* ✅ FEATURE PREVIEW (Fixed mapping logic) */}
               <div className={`rounded-3xl p-6 border ${style.card}`}>
                  <h3 className={`text-[10px] font-black uppercase tracking-[0.2em] ${style.textMuted} mb-4`}>Feature Sample</h3>
                  <div className="grid grid-cols-2 gap-2">
                     {log.flowFeatures ? Object.entries(log.flowFeatures).slice(0, 4).map(([k, v]) => (
                        <div key={k} className={`p-2 rounded-xl border ${style.innerCard}`}>
                           <p className={`text-[8px] font-black uppercase truncate ${style.textMuted}`}>{k}</p>
                           <p className={`text-[10px] font-mono font-bold ${style.textMain}`}>{v}</p>
                        </div>
                     )) : <p className="text-[10px] italic text-slate-500">Full vector not persisted.</p>}
                  </div>
               </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LogDetailsModal;