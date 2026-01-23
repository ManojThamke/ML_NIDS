import { startMonitoring, stopMonitoring, getMonitoringStatus } from "../api";
import { useState } from "react";

function MonitoringControl({ monitoring, setMonitoring }) {
  const [loading, setLoading] = useState(false);

  const syncStatus = async () => {
    const res = await getMonitoringStatus();
    setMonitoring(res.data.running);
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

      // 🔑 ALWAYS trust backend status
      await syncStatus();

    } catch (err) {
      console.error("❌ Monitoring toggle failed", err);
      alert("Failed to change monitoring state. Check backend logs.");
      await syncStatus();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-4 rounded-xl shadow border flex justify-between items-center">
      <h2 className="font-semibold text-gray-800">
        Monitoring Control
      </h2>

      <button
        onClick={handleClick}
        disabled={loading}
        className={`px-5 py-2 rounded text-white font-medium transition ${
          monitoring
            ? "bg-red-600 hover:bg-red-700"
            : "bg-green-600 hover:bg-green-700"
        } ${loading ? "opacity-60 cursor-not-allowed" : ""}`}
      >
        {loading
          ? "Processing..."
          : monitoring
          ? "Stop Monitoring"
          : "Start Monitoring"}
      </button>
    </div>
  );
}

export default MonitoringControl;
