import React from "react";
import { useLocation } from "react-router-dom";
import { ShieldCheck, Database } from "lucide-react";
import MonitoringControl from "./MonitoringControl"; // Ensure correct path

/**
 * Topbar Component (V3.3)
 * Handles global navigation titles, engine status, and central control.
 */
function Topbar({ monitoring, setMonitoring }) {
  const location = useLocation();

  // 🔹 Dynamic title logic based on current route
  const getTitle = () => {
    switch (location.pathname) {
      case "/": return "Security Overview";
      case "/logs": return "Forensic Traffic Logs";
      case "/stats": return "System Analytics";
      case "/models": return "Ensemble Intelligence";
      case "/settings": return "Engine Configuration";
      default: return "ML-NIDS Control";
    }
  };

  return (
    <div className="flex justify-between items-center px-8 py-5 border-b bg-white sticky top-0 z-[1000] shadow-sm">
      
      {/* 🛡️ LEFT: Dynamic Title & Versioning */}
      <div className="flex flex-col">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-black text-gray-800 tracking-tight leading-none">
            {getTitle()}
          </h1>
          <span className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-600 text-[10px] font-black uppercase tracking-widest border border-indigo-100">
            v3.2 Stable
          </span>
        </div>
        <p className="text-[10px] text-gray-400 font-bold uppercase tracking-[0.2em] mt-1.5">
          Real-time Hybrid Intrusion Detection Telemetry
        </p>
      </div>

      {/* 🛰️ RIGHT: Consolidated Control & Telemetry */}
      <div className="flex items-center gap-6">
        
        {/* 1. Database Sync Indicator (Metadata) */}
        <div className="hidden xl:flex flex-col items-end">
          <span className="text-[9px] font-black text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
            <Database size={10} /> Database Sync
          </span>
          <div className="flex items-center gap-1.5 mt-0.5">
            <div className={`w-1.5 h-1.5 rounded-full ${monitoring ? "bg-emerald-500 animate-pulse" : "bg-amber-400"}`} />
            <span className={`text-[10px] font-black ${monitoring ? "text-emerald-600" : "text-amber-600"}`}>
              {monitoring ? "ACTIVE FEED" : "STANDBY"}
            </span>
          </div>
        </div>

        {/* 2. Primary Engine Action (Moved from Dashboard to prevent duplication) */}
        <MonitoringControl monitoring={monitoring} setMonitoring={setMonitoring} />

        {/* 3. Engine Status Badge with Ripple Animation */}
        <div className={`flex items-center gap-3 px-4 py-2 rounded-xl border transition-all duration-500 ${
          monitoring ? "bg-emerald-50 border-emerald-100 shadow-sm" : "bg-rose-50 border-rose-100"
        }`}>
          <div className="relative flex items-center justify-center w-4 h-4">
            {monitoring && (
              <span className="absolute w-full h-full rounded-full bg-emerald-400 opacity-40 animate-ping" />
            )}
            <div className={`relative w-2 h-2 rounded-full ${monitoring ? "bg-emerald-500" : "bg-rose-500"}`} />
          </div>
          <span className={`text-[11px] font-black uppercase tracking-widest ${monitoring ? "text-emerald-600" : "text-rose-600"}`}>
            {monitoring ? "Engine Running" : "Engine Halted"}
          </span>
        </div>

        {/* 4. Protected Engine Icon */}
        <div className="p-2 bg-gray-900 text-white rounded-lg shadow-md group relative cursor-help">
          <ShieldCheck size={18} />
          {/* Tooltip for viva explanation */}
          <div className="absolute top-full right-0 mt-2 hidden group-hover:block w-32 bg-gray-900 text-[8px] p-2 rounded shadow-xl z-[1100] border border-gray-700 leading-tight">
            MFA-Protected Control Engine
          </div>
        </div>
      </div>
    </div>
  );
}

export default Topbar;