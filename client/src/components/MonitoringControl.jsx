import { startMonitoring, stopMonitoring, getMonitoringStatus } from "../api";
import { useState } from "react";
import { Play, Square, Loader2 } from "lucide-react"; // Matching your icon theme

/**
 * Compact MonitoringControl (V3.2)
 * Designed for Header Integration to avoid "chunky" vertical stacking.
 */
function MonitoringControl({ monitoring, setMonitoring }) {
  const [loading, setLoading] = useState(false);

  const syncStatus = async () => {
    try {
      const res = await getMonitoringStatus();
      setMonitoring(res.data.running);
    } catch (err) {
      console.error("Status sync failed", err);
    }
  };

  const handleClick = async () => {
    if (loading) return;
    try {
      setLoading(true);
      if (monitoring) {
        await stopMonitoring();
      } else {
        await startMonitoring();
      }
      await syncStatus();
    } catch (err) {
      console.error("❌ Monitoring toggle failed", err);
      alert("Failed to change monitoring state.");
      await syncStatus();
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className={`
        flex items-center gap-2 px-6 py-2.5 rounded-xl font-black text-[11px] uppercase tracking-wider 
        transition-all duration-300 shadow-sm hover:shadow-md active:scale-95
        ${loading 
          ? "bg-gray-100 text-gray-400 cursor-not-allowed" 
          : monitoring 
            ? "bg-rose-50 text-rose-600 hover:bg-rose-100 border border-rose-200" 
            : "bg-emerald-50 text-emerald-600 hover:bg-emerald-100 border border-emerald-200"
        }
      `}
    >
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : monitoring ? (
        <Square className="w-3.5 h-3.5 fill-current" />
      ) : (
        <Play className="w-3.5 h-3.5 fill-current" />
      )}
      
      <span>
        {loading ? "Syncing..." : monitoring ? "Stop Detection" : "Start Detection"}
      </span>
    </button>
  );
}

export default MonitoringControl;