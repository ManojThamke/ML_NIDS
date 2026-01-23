import { useEffect, useState } from "react";
import { getRecentDetections } from "../api";

function DetectionTable() {
  const [detections, setDetections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const fetchDetections = async () => {
      try {
        const res = await getRecentDetections(10);
        if (isMounted) {
          setDetections(res.data);
          setLoading(false);
        }
      } catch (err) {
        console.error("Failed to fetch detections:", err);
        setLoading(false);
      }
    };

    fetchDetections();
    const interval = setInterval(fetchDetections, 2000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="bg-white shadow rounded-xl p-4">
      <h2 className="text-lg font-semibold mb-4">
        Live Network Detections
      </h2>

      {loading ? (
        <p className="text-gray-500 text-sm">Loading traffic...</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-left">
            <thead className="bg-gray-100 text-gray-700 text-xs uppercase">
              <tr>
                <th className="px-3 py-2">Time</th>
                <th className="px-3 py-2">Source IP</th>
                <th className="px-3 py-2">Destination IP</th>
                <th className="px-3 py-2">Confidence</th>
                <th className="px-3 py-2">ML Label</th>
                <th className="px-3 py-2">Hybrid</th>
                <th className="px-3 py-2">Severity</th>
              </tr>
            </thead>

            <tbody>
              {detections.length > 0 ? (
                detections.map((d) => (
                  <tr
                    key={d._id}
                    className="border-b hover:bg-gray-50"
                  >
                    <td className="px-3 py-2">
                      {new Date(d.timestamp).toLocaleTimeString()}
                    </td>

                    <td className="px-3 py-2">{d.sourceIP}</td>
                    <td className="px-3 py-2">{d.destinationIP}</td>

                    <td className="px-3 py-2">
                      {(d.confidence * 100).toFixed(2)}%
                    </td>

                    <td className="px-3 py-2">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          d.finalLabel === "ATTACK"
                            ? "bg-red-100 text-red-700"
                            : "bg-green-100 text-green-700"
                        }`}
                      >
                        {d.finalLabel}
                      </span>
                    </td>

                    <td className="px-3 py-2">
                      <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-700">
                        {d.hybridLabel}
                      </span>
                    </td>

                    <td className="px-3 py-2">
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold ${
                          d.severity === "HIGH"
                            ? "bg-red-600 text-white"
                            : d.severity === "MEDIUM"
                            ? "bg-orange-500 text-white"
                            : "bg-gray-200 text-gray-700"
                        }`}
                      >
                        {d.severity}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan="7"
                    className="text-center py-4 text-gray-500"
                  >
                    No detections yet
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

export default DetectionTable;
