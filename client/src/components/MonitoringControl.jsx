import { startMonitoring, stopMonitoring } from "../api";

function MonitoringControl({ monitoring, setMonitoring }) {
  const handleClick = async () => {
    try {
      if (monitoring) {
        await stopMonitoring();
        setMonitoring(false);
      } else {
        await startMonitoring();
        setMonitoring(true);
      }
    } catch (err) {
      console.error("Monitoring toggle failed", err);
    }
  };

  return (
    <div className="bg-white p-4 rounded-xl shadow border flex justify-between items-center">
      <h2 className="font-semibold">Monitoring Control</h2>

      <button
        onClick={handleClick}
        className={`px-5 py-2 rounded text-white font-medium ${
          monitoring ? "bg-red-600" : "bg-green-600"
        }`}
      >
        {monitoring ? "Stop Monitoring" : "Start Monitoring"}
      </button>
    </div>
  );
}

export default MonitoringControl;
