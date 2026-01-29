import React, { useEffect, useState } from "react";
import { getRecentDetections } from "../api";
import { Shield, Globe, Terminal, Zap, Info, ArrowDown } from "lucide-react";

/**
 * DetectionTable V4.9 (Icon Integrated Edition)
 * Fixed: Unused variable warning by integrating traffic icons into the status badges.
 */

/* ================= HELPER FUNCTIONS ================= */

// ✅ Now utilized in the table body to provide visual context
const getTrafficIcon = (label) => {
  const type = label?.toUpperCase();
  if (type === "ATTACK") return <Zap size={12} className="text-rose-500" />;
  if (type === "SUSPICIOUS") return <Terminal size={12} className="text-amber-500" />;
  return <Globe size={12} className="text-emerald-500" />;
};

const badgeStyle = (label) => {
  const base = "px-2.5 py-1 rounded text-[9px] font-black uppercase tracking-tight border inline-flex items-center gap-1.5";
  const type = label?.toUpperCase();
  switch (type) {
    case "ATTACK": return `${base} bg-rose-50 text-rose-600 border-rose-100`;
    case "SUSPICIOUS": return `${base} bg-amber-50 text-amber-600 border-amber-100`;
    default: return `${base} bg-emerald-50 text-emerald-700 border-emerald-100`;
  }
};

const getConfidenceColor = (conf) => {
  if (conf > 0.7) return "bg-rose-500";
  if (conf > 0.4) return "bg-amber-500";
  return "bg-emerald-500";
};

const getSeverityStyle = (severity) => {
  const type = severity?.toUpperCase();
  switch (type) {
    case "HIGH": return "bg-rose-500 animate-pulse ring-4 ring-rose-100";
    case "MEDIUM": return "bg-amber-400 ring-4 ring-amber-50";
    default: return "bg-emerald-400";
  }
};

const getForensicInsight = (conf, label) => {
  const type = label?.toUpperCase();
  if (type === "ATTACK" && conf > 0.7) return "Critical threat confirmed: Hybrid consensus high.";
  if (type === "BENIGN" && conf < 0.1) return "Stable ambient network noise detected.";
  if (type === "BENIGN") return "Verified safe traffic flow (Hybrid Validated).";
  return "Anomalous pattern detected for review.";
};

/* ================= COMPONENT ================= */

function DetectionTable() {
  const [detections, setDetections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const fetchDetections = async () => {
      try {
        const res = await getRecentDetections(10);
        if (isMounted) {
          setDetections(res.data || []);
          setLoading(false);
        }
      } catch (err) { if (isMounted) setLoading(false); }
    };
    fetchDetections();
    const interval = setInterval(fetchDetections, 2000);
    return () => { isMounted = false; clearInterval(interval); };
  }, []);

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-gray-100 mt-4">
      
      {/* Header */}
      <div className="px-8 py-6 border-b border-gray-50 flex justify-between items-center bg-gray-50/30">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gray-900 text-white rounded-2xl shadow-lg">
            <Shield size={22} />
          </div>
          <div>
            <h2 className="text-xl font-black text-gray-800 tracking-tight leading-none">Security Forensics</h2>
            <p className="text-[10px] text-gray-400 font-bold uppercase tracking-[0.25em] mt-2">Hybrid Inspection Telemetry</p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-100">
           <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
           <span className="text-[10px] font-black text-emerald-600 uppercase tracking-wider">Live Sync</span>
        </div>
      </div>

      <div className="overflow-visible">
        <table className="min-w-full">
          <thead className="bg-white text-gray-400 text-[10px] uppercase font-black tracking-widest border-b border-gray-50">
            <tr>
              <th className="px-6 py-5 text-center">Timeline</th>
              <th className="px-6 py-5 text-center">Flow Identity</th>
              <th className="px-6 py-5 text-center">Ports</th>
              <th className="px-6 py-5 text-center">Confidence</th>
              <th className="px-6 py-5 text-center">ML Model</th>
              <th className="px-6 py-5 text-center">Hybrid Sys</th>
              <th className="px-6 py-5 text-center">Severity</th>
              <th className="px-6 py-5 text-center">Insight</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-50 bg-white">
            {loading ? (
              <tr><td colSpan="8" className="py-20 text-center text-gray-400 font-bold uppercase tracking-widest animate-pulse">Initializing Forensic Stream...</td></tr>
            ) : detections.map((d) => (
              <tr key={d._id} className="hover:bg-indigo-50/10 transition-all duration-200">
                
                {/* Timeline */}
                <td className="px-6 py-6 text-center">
                  <div className="flex flex-col items-center">
                    <span className="text-xs font-black text-gray-700 font-mono italic">{new Date(d.timestamp).toLocaleTimeString()}</span>
                    <span className="text-[9px] text-gray-300 font-bold uppercase mt-1">ID: {d._id.slice(-6)}</span>
                  </div>
                </td>

                {/* Flow Identity */}
                <td className="px-6 py-6 text-center">
                  <div className="flex flex-col items-center gap-0.5 text-xs font-bold text-gray-600 font-mono">
                    <span>{d.sourceIP}</span>
                    <ArrowDown size={12} className="text-gray-400 my-1" strokeWidth={3} />
                    <span className="text-gray-400">{d.destinationIP}</span>
                  </div>
                </td>

                {/* Ports */}
                <td className="px-6 py-6 text-center">
                  <div className="flex flex-col items-center gap-1 font-mono text-[9px] font-black italic">
                     <span className="text-indigo-500 bg-indigo-50 px-1.5 py-0.5 rounded w-12 text-center">P:{d.sourcePort || '80'}</span>
                     <span className="text-gray-400 bg-gray-50 px-1.5 py-0.5 rounded w-12 text-center">P:{d.destinationPort || '443'}</span>
                  </div>
                </td>

                {/* Confidence */}
                <td className="px-6 py-6 text-center">
                  <div className="inline-flex flex-col items-center">
                     <span className="text-sm font-black text-gray-800 tabular-nums">{(d.confidence * 100).toFixed(2)}%</span>
                     <div className="w-16 bg-gray-100 h-1 rounded-full mt-2 overflow-hidden shadow-inner">
                        <div className={`h-full transition-all duration-1000 ${getConfidenceColor(d.confidence)}`} style={{ width: `${d.confidence * 100}%` }} />
                     </div>
                  </div>
                </td>

                {/* ✅ ML MODEL: Integrated Icon */}
                <td className="px-6 py-6 text-center">
                  <span className={badgeStyle(d.finalLabel)}>
                    {getTrafficIcon(d.finalLabel)}
                    {d.finalLabel}
                  </span>
                </td>

                {/* ✅ HYBRID SYS: Integrated Icon */}
                <td className="px-6 py-6 text-center">
                  <span className={badgeStyle(d.hybridLabel)}>
                    {getTrafficIcon(d.hybridLabel)}
                    {d.hybridLabel}
                  </span>
                </td>

                {/* Severity Status */}
                <td className="px-6 py-6 text-center">
                  <div className="flex items-center justify-center gap-2">
                    <div className={`w-2.5 h-2.5 rounded-full ${getSeverityStyle(d.severity)}`} />
                    <span className="text-xs font-black text-gray-700 tracking-tighter uppercase">{d.severity}</span>
                  </div>
                </td>

                {/* Insight Tooltip */}
                <td className="px-6 py-6 text-center">
                  <div className="relative flex justify-center group">
                    <Info size={16} className="text-gray-300 cursor-help hover:text-indigo-500 transition-colors" />
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 hidden group-hover:block z-[9999] w-max max-w-[280px]">
                      <div className="bg-gray-900 text-white text-[10px] p-3 rounded-xl shadow-2xl leading-relaxed animate-in fade-in slide-in-from-bottom-2 border border-gray-800 text-center">
                         <div className="text-indigo-400 font-black uppercase tracking-[0.2em] text-[8px] mb-1.5 border-b border-gray-800 pb-1">Expert Analysis</div>
                         <p className="font-medium whitespace-normal">{getForensicInsight(d.confidence, d.hybridLabel)}</p>
                         <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-8 border-transparent border-t-gray-900" />
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DetectionTable;