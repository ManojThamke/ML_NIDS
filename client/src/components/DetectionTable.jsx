import { useEffect, useState } from "react";
import { getRecentDetections } from "../api";

/* ================= COLOR HELPERS ================= */

const labelStyle = (label) => {
  switch (label) {
    case "ATTACK":
      return "bg-red-100 text-red-700";
    case "SUSPICIOUS":
      return "bg-yellow-100 text-yellow-800";
    default:
      return "bg-green-100 text-green-700";
  }
};

const severityStyle = (severity) => {
  switch (severity) {
    case "HIGH":
      return "bg-red-600 text-white";
    case "MEDIUM":
      return "bg-yellow-400 text-black";
    default:
      return "bg-green-200 text-green-800";
  }
};

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
          <table className="min-w-full text-sm text-center">
            <thead className="bg-gray-100 text-gray-700 text-xs uppercase">
              <tr>
                <th className="px-3 py-2 text-center">Time</th>
                <th className="px-3 py-2 text-center">Source IP</th>
                <th className="px-3 py-2 text-center">Destination IP</th>
                <th className="px-3 py-2 text-center">Confidence</th>
                <th className="px-3 py-2 text-center">ML Label</th>
                <th className="px-3 py-2 text-center">Hybrid</th>
                <th className="px-3 py-2 text-center">Severity</th>
              </tr>
            </thead>

            <tbody>
              {detections.length > 0 ? (
                detections.map((d) => (
                  <tr
                    key={d._id}
                    className="border-b hover:bg-gray-50"
                  >
                    <td className="px-3 py-2 text-center">
                      {new Date(d.timestamp).toLocaleTimeString()}
                    </td>

                    <td className="px-3 py-2 text-center font-mono">
                      {d.sourceIP}
                    </td>

                    <td className="px-3 py-2 text-center font-mono">
                      {d.destinationIP}
                    </td>

                    <td className="px-3 py-2 text-center font-semibold">
                      {(d.confidence * 100).toFixed(2)}%
                    </td>

                    <td className="px-3 py-2 text-center">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${labelStyle(
                          d.finalLabel
                        )}`}
                      >
                        {d.finalLabel}
                      </span>
                    </td>

                    <td className="px-3 py-2 text-center">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${labelStyle(
                          d.hybridLabel
                        )}`}
                      >
                        {d.hybridLabel}
                      </span>
                    </td>

                    <td className="px-3 py-2 text-center">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${severityStyle(
                          d.severity
                        )}`}
                      >
                        {d.severity}
                      </span>
                    </td>

                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" className="py-4 text-gray-500 text-center">
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
