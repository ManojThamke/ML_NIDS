import { useEffect, useState } from "react";
import { getAlerts } from "../api";

function AlertsTable() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const fetchAlerts = async () => {
      try {
        const res = await getAlerts();
        if (isMounted) {
          setAlerts(res.data);
          setLoading(false);
        }
      } catch (err) {
        console.error("Failed to fetch alerts:", err);
        setLoading(false);
      }
    };

    fetchAlerts(); // initial fetch
    const interval = setInterval(fetchAlerts, 1000); // polling every 5 sec

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="bg-white shadow rounded-xl p-4">
      <h2 className="text-lg font-semibold mb-4">
        Live Traffic Detections
      </h2>

      {loading ? (
        <p className="text-gray-500 text-sm">Loading packets...</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-left">
            <thead className="bg-gray-100 text-gray-700 text-xs uppercase">
              <tr>
                <th className="px-3 py-2">Time</th>
                <th className="px-3 py-2">Source IP</th>
                <th className="px-3 py-2">Destination IP</th>
                <th className="px-3 py-2">Probability</th>
                <th className="px-3 py-2">Label</th>
              </tr>
            </thead>
            <tbody>
              {alerts.length > 0 ? (
                alerts.map((alert) => (
                  <tr
                    key={alert._id}
                    className="border-b hover:bg-gray-50"
                  >
                    <td className="px-3 py-2">
                      {alert.timestamp}
                    </td>
                    <td className="px-3 py-2">
                      {alert.sourceIP}
                    </td>
                    <td className="px-3 py-2">
                      {alert.destinationIP}
                    </td>
                    <td className="px-3 py-2">
                      {(alert.probability * 100).toFixed(2)}%
                    </td>
                    <td className="px-3 py-2">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          alert.finalLabel === "ATTACK"
                            ? "bg-red-100 text-red-700"
                            : "bg-green-100 text-green-700"
                        }`}
                      >
                        {alert.finalLabel}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan="5"
                    className="text-center py-4 text-gray-500"
                  >
                    No packets yet
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default AlertsTable;
