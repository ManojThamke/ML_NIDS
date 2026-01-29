import React, { useEffect, useState, useCallback } from "react";
import { getAlertLogs, exportAlertLogs } from "../api";
import { 
  Search, Download, RefreshCw, 
  ChevronLeft, ChevronRight, Clock, 
  ArrowDown, ShieldCheck, Globe, Zap, 
  Eye, EyeOff 
} from "lucide-react";

import ExportLogsModal from "../components/ExportLogsModal";
import LogsInsights from "../components/LogsInsights";
import LogDetailsModal from "../components/LogDetailsModal";

/**
 * Forensic Logs V10.5 - Professional Matrix
 * 9 Columns: Timeline, Flow, Ports, Confidence, ML, Hybrid, Severity, Duration, Insight.
 */
function Logs({ theme = 'light' }) {
  const [logs, setLogs] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedLog, setSelectedLog] = useState(null);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [search, setSearch] = useState("");
  const [label, setLabel] = useState("");

  const themeStyles = {
    light: {
      container: "bg-white border border-slate-100 shadow-[0_20px_50px_rgba(79,70,229,0.08)] shadow-indigo-100/40 text-slate-800",
      header: "bg-slate-50/60 text-slate-400 border-slate-100",
      row: "border-slate-50 hover:bg-indigo-50/20",
      text: "text-slate-800",
      subtext: "text-slate-400"
    },
    dark: {
      container: "bg-slate-900 border border-slate-800 shadow-[0_20px_60px_rgba(0,0,0,0.6)] shadow-black text-slate-100",
      header: "bg-slate-950/40 text-slate-500 border-slate-800",
      row: "border-slate-800 hover:bg-slate-800/40",
      text: "text-slate-100",
      subtext: "text-slate-500"
    }
  };

  const style = themeStyles[theme] || themeStyles.light;

  const getConfBarColor = (conf) => {
    const val = conf * 100;
    if (val >= 75) return "bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.4)]"; 
    if (val >= 45) return "bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.3)]"; 
    return "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.3)]"; 
  };

  const badgeStyle = (l) => {
    const base = "px-2.5 py-1 rounded text-[10px] font-black uppercase tracking-tight border inline-flex items-center gap-1.5 transition-all";
    if (l === "ATTACK") return `${base} bg-rose-500/10 text-rose-500 border-rose-500/20`;
    if (l === "SUSPICIOUS") return `${base} bg-amber-500/10 text-amber-500 border-amber-500/20`;
    return `${base} bg-emerald-500/10 text-emerald-500 border-emerald-500/20`;
  };

  const fetchLogs = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getAlertLogs({ page, limit: 50, label, search });
      setLogs(res.data.logs || []);
      setTotalPages(res.data.totalPages || 1);
    } catch (err) { console.error("Fetch Error:", err); } finally { setLoading(false); }
  }, [page, label, search]);

  useEffect(() => { fetchLogs(); }, [fetchLogs]);

  const handleExport = async (format, options) => {
    try {
      const res = await exportAlertLogs({ format, range: options.range, onlyAttack: options.onlyAttack });
      const blob = new Blob([res.data], { type: format === "csv" ? "text/csv;charset=utf-8;" : "application/json;charset=utf-8;" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `nids_export_${Date.now()}.${format}`;
      a.click();
    } catch (err) { console.error(err); }
  };

  return (
    <div className="p-2 space-y-6 max-w-[1700px] mx-auto animate-in fade-in duration-700">
      
      {/* 🛡️ HEADER SECTION */}
      <div className="flex justify-between items-end px-2">
        <div className="flex flex-col">
          <div className="flex items-center gap-3 mb-1">
             <ShieldCheck size={32} className="text-indigo-600 drop-shadow-sm" />
             <h1 className={`text-4xl font-black tracking-tighter ${style.text}`}>Traffic Forensics</h1>
          </div>
          <p className="text-[11px] font-bold text-indigo-500 uppercase tracking-[0.4em] ml-1 opacity-80 italic">Full Intelligence Flow Matrix</p>
        </div>
        <div className="flex gap-3 pb-1">
            <button onClick={() => setAutoRefresh(!autoRefresh)} className={`flex items-center gap-2 px-5 py-2.5 rounded-xl border text-[10px] font-black uppercase transition-all shadow-sm ${autoRefresh ? 'bg-emerald-500 text-white border-emerald-400' : 'bg-white border-slate-200 text-slate-500'}`}>
                <RefreshCw size={14} className={autoRefresh ? 'animate-spin' : ''} /> {autoRefresh ? 'Live' : 'Static View'}
            </button>
            <button onClick={() => setShowExportModal(true)} className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white rounded-xl font-black text-[10px] uppercase shadow-xl hover:scale-105 transition-all shadow-indigo-500/20">
                <Download size={14} /> Export Dataset
            </button>
        </div>
      </div>

      <LogsInsights theme={theme} />

      {/* 🔍 FILTER BAR */}
      <div className={`${style.container} sticky top-0 z-30 rounded-2xl p-3.5 flex items-center gap-4 border`}>
        <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input 
              placeholder="Search Source or Destination IP..." 
              value={search} 
              onChange={(e) => {setPage(1); setSearch(e.target.value);}} 
              className={`w-full pl-12 pr-4 py-2.5 rounded-xl border-none text-sm font-bold outline-none ${theme === 'dark' ? 'bg-slate-800 text-white' : 'bg-slate-50 text-slate-900'}`} 
            />
        </div>
        <select value={label} onChange={(e) => {setPage(1); setLabel(e.target.value);}} className={`px-4 py-2.5 rounded-xl border-none text-[10px] font-black uppercase tracking-widest outline-none cursor-pointer ${theme === 'dark' ? 'bg-slate-800 text-slate-300' : 'bg-slate-50 text-slate-500'}`}>
            <option value="">Status: All Traffic</option>
            <option value="ATTACK">Detection Only</option>
            <option value="BENIGN">Safe Flows</option>
        </select>
        <button 
          onClick={() => setShowAdvanced(!showAdvanced)} 
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all border text-[10px] font-black uppercase ${showAdvanced ? 'bg-indigo-600 text-white border-indigo-600 shadow-md shadow-indigo-100' : 'bg-slate-100 text-slate-500 border-slate-200'}`}
        >
            {showAdvanced ? <EyeOff size={16} /> : <Eye size={16} />}
            {showAdvanced ? "Basic View" : "Full Forensic"}
        </button>
      </div>

      {/* 📊 FULL FORENSIC MATRIX */}
      <div className={`${style.container} rounded-[2.5rem] overflow-hidden border transition-all duration-700`}>
        <div className="overflow-x-auto">
          <table className="min-w-full text-center border-collapse">
            <thead className={`uppercase text-[10px] font-black tracking-[0.25em] border-b ${style.header}`}>
              <tr>
                <th className="px-4 py-6">Timeline</th>
                <th className="px-4 py-6">Flow Identity</th>
                <th className="px-4 py-6">Ports (S/D)</th>
                <th className="px-5 py-6 text-center">Confidence</th>
                <th className="px-4 py-6">ML Model</th>
                <th className="px-4 py-6">Hybrid Sys</th>
                <th className="px-4 py-6 text-center">Severity</th>
                {showAdvanced && (
                  <>
                    <th className="px-4 py-6">Duration (s)</th>
                    <th className="px-4 py-6 text-left min-w-[180px]">Hybrid Insight</th>
                  </>
                )}
              </tr>
            </thead>
            <tbody className={`divide-y ${theme === 'dark' ? 'divide-slate-800' : 'divide-slate-100'}`}>
              {loading && logs.length === 0 ? (
                <tr><td colSpan="10" className="py-24 animate-pulse font-black text-slate-400 tracking-widest uppercase italic text-center">Decrypting Datastream...</td></tr>
              ) : logs.map((log) => (
                <tr key={log._id} onClick={() => setSelectedLog(log)} className={`group transition-all cursor-pointer border-b border-slate-50/50 ${theme === 'dark' ? 'hover:bg-slate-800/40' : 'hover:bg-indigo-50/20'}`}>
                  <td className={`px-4 py-3 font-mono text-[11px] font-bold ${style.subtext} italic`}>
                    <div className="flex items-center justify-center gap-2">
                       <Clock size={11} className="text-indigo-400 opacity-60" />
                       {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </div>
                  </td>
                  
                  <td className="px-4 py-3">
                    <div className="flex flex-col items-center font-mono text-[12px] font-black text-indigo-600 tracking-tighter">
                      <span>{log.sourceIP}</span>
                      <ArrowDown size={10} className="text-slate-300 -my-0.5 group-hover:text-indigo-400 transition-all" strokeWidth={3} />
                      <span className={`${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'} font-bold`}>{log.destinationIP}</span>
                    </div>
                  </td>

                  <td className="px-4 py-3">
                    <div className="flex flex-col items-center gap-1 font-mono text-[8.5px] font-black">
                       <span className={`px-2 py-0.5 rounded border w-16 text-center ${theme === 'dark' ? 'bg-slate-800 border-slate-700 text-slate-400' : 'bg-slate-100 border-slate-200 text-slate-500'}`}>
                         {log.protocol}:{log.srcPort || '0'}
                       </span>
                       <span className={`px-2 py-0.5 rounded border w-16 text-center ${theme === 'dark' ? 'bg-indigo-950/30 border-indigo-900/50 text-indigo-400' : 'bg-indigo-50/60 border-indigo-100 text-indigo-600'}`}>
                         {log.protocol}:{log.dstPort || '0'}
                       </span>
                    </div>
                  </td>

                  <td className="px-5 py-3">
                    <div className="flex flex-col items-center min-w-[75px]">
                       <span className={`text-[12px] font-black tabular-nums ${log.confidence > 0.7 ? 'text-rose-600' : style.text}`}>
                         {(log.confidence * 100).toFixed(2)}%
                       </span>
                       <div className={`w-12 h-1 rounded-full mt-1 overflow-hidden shadow-inner ring-1 ring-slate-200/50 ${theme === 'dark' ? 'bg-slate-800' : 'bg-slate-100'}`}>
                          <div 
                            className={`h-full transition-all duration-1000 ${getConfBarColor(log.confidence)}`} 
                            style={{ width: `${log.confidence * 100}%` }} 
                          />
                       </div>
                    </div>
                  </td>

                  <td className="px-4 py-3 text-center"><span className={badgeStyle(log.finalLabel)}>{log.finalLabel}</span></td>
                  <td className="px-4 py-3 text-center"><span className={badgeStyle(log.hybridLabel)}>{log.hybridLabel}</span></td>

                  <td className="px-4 py-3">
                    <div className="flex items-center justify-center gap-2">
                      <div className={`w-2.5 h-2.5 rounded-full ${log.severity?.toUpperCase() === 'HIGH' || log.severity?.toUpperCase() === 'ATTACK' ? 'bg-rose-500 animate-pulse ring-4 ring-rose-500/20' : 'bg-emerald-400 ring-2 ring-emerald-400/10'}`} />
                      <span className={`text-[10px] font-black uppercase ${style.subtext}`}>{log.severity}</span>
                    </div>
                  </td>

                  {showAdvanced && (
                     <>
                        <td className={`px-4 py-3 font-mono text-[11px] font-bold ${style.subtext} text-center`}>
                          {log.flowDuration ? log.flowDuration.toFixed(4) : "0.0000"}
                        </td>
                        <td className={`px-4 py-3 text-left text-[11px] italic max-w-[200px] truncate ${style.subtext}`}>
                           {log.hybridReason || "Verified flow baseline"}
                        </td>
                     </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 📑 PAGINATION */}
      <div className="flex justify-between items-center px-4 max-w-[1700px] mx-auto pt-2">
        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest opacity-60">Showing {logs.length} Flow Records | Page {page} of {totalPages}</p>
        <div className="flex gap-2">
          <button disabled={page === 1} onClick={() => setPage(page - 1)} className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-400 shadow-sm transition-all disabled:opacity-30"><ChevronLeft size={20} /></button>
          <button disabled={page === totalPages} onClick={() => setPage(page + 1)} className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-400 shadow-sm transition-all disabled:opacity-30"><ChevronRight size={20} /></button>
        </div>
      </div>

      {showExportModal && <ExportLogsModal theme={theme} isOpen={showExportModal} onClose={() => setShowExportModal(false)} onExport={(options) => handleExport(options.format, options)} />}
      {selectedLog && <LogDetailsModal theme={theme} log={selectedLog} onClose={() => setSelectedLog(null)} />}
    </div>
  );
}

export default Logs;