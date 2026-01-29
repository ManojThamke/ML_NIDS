import { useState, useEffect } from "react";
import {
  saveSettings,
  getSettings,
  getSystemInterface,
  getMonitoringStatus,
} from "../api";
import { 
  Settings2, Cpu, Network, Zap, 
  Terminal, RotateCcw, Save, Lock, 
  AlertCircle, Activity, Globe 
} from "lucide-react";

const DEFAULT_MODELS = [
  "LogisticRegression", "DecisionTree", "RandomForest",
  "KNN", "NaiveBayes", "GradientBoosting",
  "XGBoost", "LightGBM", "MLP",
];

function Settings({ theme = 'light' }) {
  const [models, setModels] = useState(DEFAULT_MODELS);
  const [threshold, setThreshold] = useState(0.5);
  const [voteK, setVoteK] = useState(3);
  const [flowTimeout, setFlowTimeout] = useState(10);
  const [iface, setIface] = useState("");
  const [protocol, setProtocol] = useState("both");
  const [monitoring, setMonitoring] = useState(false);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const containerStyle = theme === 'light' 
    ? "bg-white border-slate-100 shadow-[0_15px_40px_rgba(79,70,229,0.06)] shadow-indigo-100/30 text-slate-800"
    : "bg-slate-900 border-slate-800 shadow-[0_20px_50px_rgba(0,0,0,0.5)] shadow-black text-slate-100";

  useEffect(() => {
    getMonitoringStatus().then(res => setMonitoring(res.data.running)).catch(() => setMonitoring(false));
    getSettings().then(res => {
      if (!res.data) return;
      setModels(res.data.models ?? DEFAULT_MODELS);
      setThreshold(res.data.threshold ?? 0.5);
      setVoteK(res.data.voteK ?? 3);
      setFlowTimeout(res.data.flowTimeout ?? 10);
      setIface(res.data.interface ?? "");
      setProtocol(res.data.protocol ?? "both");
    }).catch(console.warn);
  }, []);

  const toggleModel = (model) => {
    if (monitoring) return;
    setModels((prev) => {
      // 🔒 Functional Logic Guard: Prevent unselecting the last model
      if (prev.length === 1 && prev.includes(model)) {
        setStatus({ type: "warning", msg: "At least one model must be selected" });
        return prev;
      }
      const updated = prev.includes(model) ? prev.filter((m) => m !== model) : [...prev, model];
      if (voteK > updated.length) setVoteK(updated.length);
      return updated;
    });
  };

  const resetDefaults = () => {
    if (monitoring) return;
    setModels(DEFAULT_MODELS);
    setThreshold(0.5);
    setVoteK(3);
    setFlowTimeout(10);
    setProtocol("both");
    setIface("");
    setStatus({ type: "success", msg: "Settings reset to defaults" });
  };

  const applySettings = async () => {
    if (monitoring || models.length === 0 || !iface) return;
    try {
      setLoading(true);
      await saveSettings({ models, threshold, voteK, flowTimeout, interface: iface, protocol });
      setStatus({ type: "success", msg: "Configuration Synchronized" });
    } catch {
      setStatus({ type: "error", msg: "Protocol Sync Failure" });
    } finally { setLoading(false); }
  };

  const pythonCommand = `python detector_live_capture_v2.py --iface "${iface || "<auto>"}" --protocol ${protocol} --models ${models.join(",")} --threshold ${threshold} --vote ${voteK} --run_mode service`.trim();

  return (
    <div className="p-4 space-y-6 max-w-[1550px] mx-auto animate-in fade-in duration-700 pb-8">
      
      {/* 🚀 HEADER - SLIDE FROM LEFT */}
      <div className="flex justify-between items-end px-2">
        <div className="animate-in slide-in-from-left-6 duration-700 ease-out">
          <div className="flex items-center gap-3 mb-0.5">
             <Settings2 size={28} className="text-indigo-600 drop-shadow-sm" />
             <h1 className={`text-3xl font-black tracking-tighter ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
               Engine Config
             </h1>
          </div>
          <p className="text-[10px] font-bold text-indigo-500 uppercase tracking-[0.4em] ml-1 opacity-70">Detection Infrastructure</p>
        </div>
        {monitoring && (
          <div className="flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 px-4 py-1.5 rounded-xl text-amber-500 animate-pulse shadow-sm">
            <Lock size={14} />
            <span className="text-[10px] font-black uppercase tracking-widest">Locked</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* 🧠 MODEL MATRIX - STAGGERED FADE-IN WATERFALL */}
        <div className={`lg:col-span-8 ${containerStyle} rounded-[2rem] p-6 flex flex-col animate-in slide-in-from-bottom-8 duration-1000 ease-in-out`}>
          <div className="flex items-center gap-2 mb-6">
            <Cpu className="text-indigo-500" size={18} />
            <h3 className="text-[11px] font-black uppercase tracking-[0.2em] opacity-80">Model Ensemble Matrix</h3>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {DEFAULT_MODELS.map((m, idx) => (
              <button
                key={m}
                disabled={monitoring}
                onClick={() => toggleModel(m)}
                // Dynamic animation delay for staggered effect
                style={{ animationDelay: `${idx * 75}ms` }}
                className={`p-4 rounded-2xl border-2 transition-all duration-300 flex flex-col justify-center min-h-[85px] relative overflow-hidden group animate-in fade-in slide-in-from-bottom-4 fill-mode-both ${
                  models.includes(m)
                    ? "bg-indigo-600 border-indigo-500 text-white shadow-xl translate-y-[-2px] scale-[1.02]"
                    : "bg-slate-50 dark:bg-slate-800/50 border-slate-100 dark:border-slate-800 text-slate-400 opacity-60 hover:opacity-100 hover:scale-[1.01]"
                }`}
              >
                <div className="flex justify-between items-center relative z-10">
                   <span className="text-[10.5px] font-black uppercase tracking-tight tabular-nums">{m}</span>
                   {models.includes(m) && <Zap size={14} fill="currentColor" className="text-white animate-pulse" />}
                </div>
                {models.includes(m) && <Zap size={50} className="absolute -right-4 -bottom-4 opacity-10 rotate-12 transition-transform group-hover:rotate-45 duration-700" />}
              </button>
            ))}
          </div>
        </div>

        {/* ⚙️ PARAMETERS - SLIDE FROM RIGHT */}
        <div className="lg:col-span-4 flex flex-col gap-6 animate-in slide-in-from-right-10 duration-1000 ease-in-out">
          
          <div className={`${containerStyle} rounded-[2rem] p-6 flex flex-col justify-center min-h-[120px] transition-all hover:shadow-indigo-200/20`}>
            <div className="flex justify-between items-center mb-4">
              <span className="text-[10px] font-black uppercase text-indigo-500 tracking-widest flex items-center gap-2">
                <Activity size={14} /> Threshold
              </span>
              <span className="text-sm font-black italic tabular-nums">{threshold * 100}%</span>
            </div>
            <input type="range" min={0} max={0.9} step={0.05} value={threshold} disabled={monitoring} 
              onChange={(e) => setThreshold(Number(e.target.value))} 
              className="w-full accent-indigo-600 cursor-pointer h-1.5 bg-slate-100 dark:bg-slate-800 rounded-lg appearance-none transition-all hover:h-2" />
          </div>

          <div className={`${containerStyle} rounded-[2rem] p-6 space-y-5 flex-grow`}>
            <div className="space-y-2 group">
              <label className="text-[9px] font-black uppercase text-slate-400 tracking-[0.2em] group-hover:text-indigo-500 transition-colors">Vote-K Consensus</label>
              <input type="number" value={voteK} disabled={monitoring} min={1} max={models.length}
                onChange={(e) => setVoteK(Number(e.target.value))}
                className="w-full bg-slate-50 dark:bg-slate-950 border-none rounded-xl p-2.5 font-black text-xs outline-none focus:ring-2 focus:ring-indigo-500/50 shadow-inner transition-all" />
            </div>
            <div className="space-y-2 group">
              <label className="text-[9px] font-black uppercase text-slate-400 tracking-[0.2em] group-hover:text-indigo-500 transition-colors">Protocol Node</label>
              <select value={protocol} disabled={monitoring} onChange={(e) => setProtocol(e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-950 border-none rounded-xl p-2.5 font-black text-xs outline-none appearance-none cursor-pointer transition-all hover:bg-slate-100 dark:hover:bg-slate-900">
                <option value="both">TCP + UDP</option>
                <option value="tcp">TCP ONLY</option>
                <option value="udp">UDP ONLY</option>
              </select>
            </div>
            <div className="space-y-2 group">
              <label className="text-[9px] font-black uppercase text-slate-400 tracking-[0.2em] group-hover:text-indigo-500 transition-colors">Node Interface</label>
              <select value={iface} disabled={monitoring} onChange={(e) => setIface(e.target.value)}
                className="w-full bg-slate-50 dark:bg-slate-950 border-none rounded-xl p-2.5 font-black text-xs outline-none">
                <option value="">AUTO-DETECT</option>
                <option value="Wi-Fi">Wi-Fi</option>
                <option value="Ethernet">Hardware</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* ⌨️ TERMINAL - REVEAL WITH ZOOM */}
      <div className="bg-slate-950 rounded-[2rem] p-6 border border-slate-800 shadow-2xl relative overflow-hidden group animate-in zoom-in-95 fade-in duration-1000 delay-300">
        <Terminal size={120} className="absolute -right-6 -top-6 opacity-5 text-emerald-500 group-hover:opacity-10 group-hover:scale-110 transition-all duration-1000" />
        <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest mb-3 flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> Execution Protocol Preview
        </p>
        <code className="text-emerald-400/90 font-mono text-[11px] leading-relaxed block overflow-x-auto whitespace-pre-wrap selection:bg-emerald-500/30">
          {pythonCommand}
        </code>
      </div>

      {/* 📑 ACTIONS - SPRING INTERACTIONS */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800 animate-in fade-in duration-1000 delay-500">
        <div className="flex gap-4">
          <button onClick={applySettings} disabled={loading || monitoring}
            className="flex items-center gap-2 px-8 py-2.5 bg-indigo-600 text-white rounded-xl font-black text-[11px] uppercase shadow-lg shadow-indigo-200/40 hover:scale-105 hover:bg-indigo-700 active:scale-95 transition-all duration-200 disabled:opacity-30 disabled:scale-100">
            <Save size={14} /> Commit Changes
          </button>
          <button onClick={resetDefaults} disabled={monitoring}
            className="flex items-center gap-2 px-8 py-2.5 border-2 border-slate-100 dark:border-slate-800 text-slate-500 rounded-xl font-black text-[11px] uppercase hover:bg-slate-50 dark:hover:bg-slate-800 hover:border-slate-200 active:scale-95 transition-all duration-200">
            <RotateCcw size={14} /> Revert
          </button>
        </div>
        {status && (
          <div className={`flex items-center gap-2 px-6 py-2 rounded-xl text-[10px] font-black uppercase shadow-sm animate-in slide-in-from-right-12 duration-700 bounce-in ${
            status.type === 'success' ? 'bg-emerald-500/10 text-emerald-500' : 
            status.type === 'warning' ? 'bg-amber-500/10 text-amber-500' :
            'bg-rose-500/10 text-rose-500'
          }`}>
            <AlertCircle size={14} /> {status.msg}
          </div>
        )}
      </div>
    </div>
  );
}

export default Settings;