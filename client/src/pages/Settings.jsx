import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  saveSettings,
  getSettings,
  getSystemInterface,
  getMonitoringStatus,
} from "../api";
import {
  Settings2, Cpu, Network, Zap,
  Terminal, RotateCcw, Save, Lock,
  AlertCircle, Activity, ChevronRight
} from "lucide-react";

const DEFAULT_MODELS = [
  "LogisticRegression", "DecisionTree", "RandomForest",
  "KNN", "NaiveBayes", "GradientBoosting",
  "XGBoost", "LightGBM", "MLP",
];

function Settings({ theme = "light" }) {
  const [models, setModels] = useState(DEFAULT_MODELS);
  const [threshold, setThreshold] = useState(0.5);
  const [voteK, setVoteK] = useState(3);
  const [flowTimeout, setFlowTimeout] = useState(10);
  const [iface, setIface] = useState("");
  const [interfaces, setInterfaces] = useState([]);
  const [protocol, setProtocol] = useState("both");
  const [monitoring, setMonitoring] = useState(false);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const containerStyle =
    theme === "light"
      ? "bg-white/80 backdrop-blur-md border-slate-200/60 shadow-xl text-slate-800"
      : "bg-slate-900/90 backdrop-blur-md border-slate-800 shadow-2xl text-slate-100";

  useEffect(() => {
    getMonitoringStatus()
      .then((res) => setMonitoring(res.data.running))
      .catch(() => setMonitoring(false));

    getSettings()
      .then((res) => {
        if (!res.data) return;
        setModels(res.data.models ?? DEFAULT_MODELS);
        setThreshold(res.data.threshold ?? 0.5);
        setVoteK(res.data.voteK ?? 3);
        setFlowTimeout(res.data.flowTimeout ?? 10);
        setIface(res.data.interface ?? "");
        setProtocol(res.data.protocol ?? "both");
      })
      .catch(console.warn);

    getSystemInterface()
      .then((res) => setInterfaces(res.data ?? []))
      .catch(() => setInterfaces([]));
  }, []);

  const toggleModel = (model) => {
    if (monitoring) return;
    setModels((prev) => {
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
    if (monitoring || models.length === 0 || !iface) {
      setStatus({ type: "warning", msg: "Please select a network interface" });
      return;
    }
    try {
      setLoading(true);
      await saveSettings({ models, threshold, voteK, flowTimeout, interface: iface, protocol });
      setStatus({ type: "success", msg: "Configuration synchronized" });
    } catch {
      setStatus({ type: "error", msg: "Failed to save settings" });
    } finally {
      setLoading(false);
    }
  };

  const pythonCommand = `python detector_live_capture_v2.py --iface "${iface || "<select-interface>"}" --protocol ${protocol} --models ${models.join(",")} --threshold ${threshold} --vote ${voteK} --run_mode service`;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 space-y-8 max-w-[1550px] mx-auto pb-12"
    >
      {/* HEADER SECTION */}
      <div className="flex justify-between items-center px-2">
        <div className="relative">
          <motion.div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-600 rounded-2xl shadow-lg shadow-indigo-500/30">
              <Settings2 size={24} className="text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-black tracking-tight italic">ENGINE CONFIG</h1>
              <div className="flex items-center gap-2 mt-1">
                <span className="h-1 w-1 bg-indigo-500 rounded-full animate-ping" />
                <p className="text-[10px] font-bold text-indigo-500 uppercase tracking-[0.4em]">
                  Detection Infrastructure Control
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        <AnimatePresence>
          {monitoring && (
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="flex items-center gap-3 bg-amber-500/10 border border-amber-500/30 px-5 py-2 rounded-2xl text-amber-500 backdrop-blur-sm shadow-lg shadow-amber-500/5"
            >
              <Lock size={16} className="animate-pulse" />
              <span className="text-[11px] font-black uppercase tracking-widest">System Locked</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* MODEL MATRIX */}
        <div className={`lg:col-span-8 ${containerStyle} rounded-[2.5rem] p-8 border shadow-2xl relative overflow-hidden`}>
          <div className="absolute top-0 right-0 p-8 opacity-5">
            <Cpu size={120} />
          </div>
          
          <div className="flex items-center gap-3 mb-8">
            <div className="h-8 w-1 bg-indigo-500 rounded-full" />
            <h3 className="text-[12px] font-black uppercase tracking-[0.25em] text-slate-500">
              Model Ensemble Matrix
            </h3>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {DEFAULT_MODELS.map((m, index) => (
              <motion.button
                key={m}
                whileHover={!monitoring ? { scale: 1.02, translateY: -2 } : {}}
                whileTap={!monitoring ? { scale: 0.98 } : {}}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                disabled={monitoring}
                onClick={() => toggleModel(m)}
                className={`group relative p-5 rounded-[1.5rem] border-2 transition-all duration-300 flex flex-col items-start gap-3 ${
                  models.includes(m)
                    ? "bg-indigo-600 border-indigo-400 shadow-lg shadow-indigo-600/20 text-white"
                    : "bg-slate-50/50 dark:bg-slate-800/50 border-transparent text-slate-400 hover:border-slate-300 dark:hover:border-slate-600"
                } ${monitoring ? "opacity-60 cursor-not-allowed" : "cursor-pointer"}`}
              >
                <div className={`p-2 rounded-lg ${models.includes(m) ? "bg-white/20" : "bg-slate-200 dark:bg-slate-700"}`}>
                   <Activity size={14} />
                </div>
                <span className="text-[11px] font-black uppercase tracking-tight">{m}</span>
                {models.includes(m) && (
                  <motion.div layoutId="activeModel" className="absolute top-3 right-3 h-2 w-2 bg-white rounded-full shadow-[0_0_10px_white]" />
                )}
              </motion.button>
            ))}
          </div>
        </div>

        {/* PARAMETERS PANEL */}
        <div className="lg:col-span-4 space-y-6">
          <div className={`${containerStyle} rounded-[2.5rem] p-8 border shadow-xl`}>
            <div className="flex justify-between items-center mb-6">
              <span className="text-[11px] font-black uppercase text-indigo-500 tracking-wider">Detection Threshold</span>
              <span className="font-mono font-black text-xl text-indigo-600 bg-indigo-50 dark:bg-indigo-900/30 px-3 py-1 rounded-lg">
                {(threshold * 100).toFixed(0)}%
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={0.9}
              step={0.05}
              value={threshold}
              disabled={monitoring}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
          </div>

          <div className={`${containerStyle} rounded-[2.5rem] p-8 space-y-6 border shadow-xl relative`}>
            <div className="space-y-4">
              <div className="group">
                <label className="text-[10px] font-black uppercase text-slate-400 mb-2 block group-focus-within:text-indigo-500 transition-colors">Voting Weight (K)</label>
                <input
                  type="number"
                  min={1}
                  max={models.length}
                  value={voteK}
                  disabled={monitoring}
                  onChange={(e) => setVoteK(Number(e.target.value))}
                  className="w-full rounded-2xl bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent focus:border-indigo-500 outline-none p-3 text-sm font-bold transition-all"
                />
              </div>

              <div className="group">
                <label className="text-[10px] font-black uppercase text-slate-400 mb-2 block">Capture Protocol</label>
                <select
                  value={protocol}
                  disabled={monitoring}
                  onChange={(e) => setProtocol(e.target.value)}
                  className="w-full rounded-2xl bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent focus:border-indigo-500 outline-none p-3 text-sm font-bold transition-all appearance-none cursor-pointer"
                >
                  <option value="both">TCP + UDP (Standard)</option>
                  <option value="tcp">TCP Only</option>
                  <option value="udp">UDP Only</option>
                  <option value="icmp">ICMP (Control)</option>
                  <option value="arp">ARP (Ethernet)</option>
                  <option value="all">ALL Traffic</option>
                </select>
              </div>

              <div className="group">
                <label className="text-[10px] font-black uppercase text-slate-400 mb-2 block">Interface Gateway</label>
                <select
                  value={iface}
                  disabled={monitoring}
                  onChange={(e) => setIface(e.target.value)}
                  className="w-full rounded-2xl bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent focus:border-indigo-500 outline-none p-3 text-sm font-bold transition-all cursor-pointer"
                >
                  <option value="">Choose Interface...</option>
                  {interfaces.map((i) => <option key={i} value={i}>{i}</option>)}
                </select>
                <p className="text-[9px] text-slate-400 mt-3 flex items-start gap-2 italic">
                  <AlertCircle size={10} className="shrink-0" />
                  Use VirtualBox Host-Only for internal VM monitoring.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* TERMINAL PREVIEW */}
      <motion.div 
        layout
        className="bg-slate-950 rounded-[2.5rem] p-8 border border-slate-800 shadow-2xl relative group overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="flex items-center gap-3 mb-4">
          <Terminal size={16} className="text-emerald-500" />
          <p className="text-[11px] font-black text-emerald-500 uppercase tracking-widest">
            Live CLI Execution String
          </p>
        </div>
        <div className="relative font-mono text-[13px] leading-relaxed bg-black/40 p-4 rounded-xl border border-emerald-500/20">
          <span className="text-emerald-600 mr-2 font-black">$</span>
          <code className="text-emerald-400">
            {pythonCommand}
            <span className="inline-block w-2 h-4 bg-emerald-500 ml-1 animate-pulse" />
          </code>
        </div>
      </motion.div>

      {/* FOOTER ACTIONS */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-6 px-2">
        <div className="flex gap-4 w-full sm:w-auto">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={applySettings}
            disabled={loading || monitoring}
            className="flex-1 sm:flex-none px-10 py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-black text-xs uppercase tracking-widest flex items-center justify-center gap-3 shadow-lg shadow-indigo-500/20 disabled:grayscale transition-all"
          >
            {loading ? <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Save size={16} />} 
            Sync Config
          </motion.button>

          <button
            onClick={resetDefaults}
            disabled={monitoring}
            className="flex-1 sm:flex-none px-10 py-4 border-2 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-2xl font-black text-xs uppercase tracking-widest flex items-center justify-center gap-3 transition-all disabled:opacity-50"
          >
            <RotateCcw size={16} /> Restore
          </button>
        </div>

        <AnimatePresence mode="wait">
          {status && (
            <motion.div 
              key={status.msg}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className={`flex items-center gap-3 px-6 py-3 rounded-2xl text-[11px] font-black uppercase tracking-wider backdrop-blur-sm border ${
                status.type === "success" ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-500" :
                status.type === "warning" ? "bg-amber-500/10 border-amber-500/20 text-amber-500" : 
                "bg-rose-500/10 border-rose-500/20 text-rose-500"
              }`}
            >
              <AlertCircle size={16} /> {status.msg}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

export default Settings;