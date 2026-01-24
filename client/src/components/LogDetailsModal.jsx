import PerModelConfidenceChart from "./charts/PerModelConfidenceChart";

/* ================= COLOR HELPERS ================= */

const labelClass = (label) => {
  if (label === "ATTACK") return "bg-red-100 text-red-700";
  if (label === "SUSPICIOUS") return "bg-yellow-100 text-yellow-800";
  return "bg-green-100 text-green-700"; // BENIGN
};

const severityClass = (severity) => {
  if (severity === "HIGH") return "bg-red-600 text-white";
  if (severity === "MEDIUM") return "bg-yellow-400 text-black";
  return "bg-green-200 text-green-800"; // LOW
};

const confidenceBarClass = (confidence) => {
  if (confidence >= 0.7) return "bg-red-500";
  if (confidence >= 0.5) return "bg-yellow-400";
  return "bg-green-500";
};

function LogDetailsModal({ log, onClose }) {
  if (!log) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto p-6 relative shadow-xl">

        {/* ❌ Close */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-gray-400 hover:text-gray-700 text-xl"
        >
          ✕
        </button>

        {/* ===== HEADER ===== */}
        <h2 className="text-xl font-bold mb-6">
          Detection Log Details
        </h2>

        {/* ===== SUMMARY ===== */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm mb-6">

          <div>
            <p className="text-gray-500">Timestamp</p>
            <p className="font-mono">
              {new Date(log.timestamp).toLocaleString()}
            </p>
          </div>

          <div>
            <p className="text-gray-500">Ensemble Confidence</p>
            <div className="mt-1">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${confidenceBarClass(
                    log.confidence || 0
                  )}`}
                  style={{ width: `${(log.confidence || 0) * 100}%` }}
                />
              </div>
              <p className="text-xs font-semibold mt-1">
                {((log.confidence || 0) * 100).toFixed(2)}%
              </p>
            </div>
          </div>

          <div>
            <p className="text-gray-500">Source IP</p>
            <p className="font-mono">{log.sourceIP}</p>
          </div>

          <div>
            <p className="text-gray-500">Destination IP</p>
            <p className="font-mono">{log.destinationIP}</p>
          </div>

          <div>
            <p className="text-gray-500">Final Label</p>
            <span
              className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${labelClass(
                log.finalLabel
              )}`}
            >
              {log.finalLabel}
            </span>
          </div>

          <div>
            <p className="text-gray-500">Severity Level</p>
            <span
              className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${severityClass(
                log.severity
              )}`}
            >
              {log.severity}
            </span>
          </div>

          <div>
            <p className="text-gray-500">Hybrid Decision</p>
            <span
              className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${labelClass(
                log.hybridLabel
              )}`}
            >
              {log.hybridLabel}
            </span>
          </div>

          <div>
            <p className="text-gray-500">Aggregation Strategy</p>
            <p className="font-medium">
              {log.aggregationMethod || "Ensemble Voting"}
            </p>
          </div>
        </div>

        {/* ===== PER-MODEL CONFIDENCE ===== */}
        <div className="mb-8">
          <h3 className="font-semibold mb-3">
            Per-Model Confidence (Explainability)
          </h3>

          {log.modelProbabilities &&
          Object.keys(log.modelProbabilities).length > 0 ? (
            <PerModelConfidenceChart
              modelProbabilities={log.modelProbabilities}
            />
          ) : (
            <p className="text-sm text-gray-500">
              No per-model confidence data available
            </p>
          )}
        </div>

        {/* ===== EXTRACTED FEATURES ===== */}
        <div>
          <h3 className="font-semibold mb-3">
            Extracted Flow Features
          </h3>

          {!log.features || Object.keys(log.features).length === 0 ? (
            <p className="text-gray-500 text-sm">
              Feature data not stored for this detection
            </p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              {Object.entries(log.features).map(([key, value]) => (
                <div
                  key={key}
                  className="flex justify-between bg-gray-50 px-3 py-2 rounded"
                >
                  <span className="text-gray-600">{key}</span>
                  <span className="font-mono font-medium text-gray-900">
                    {typeof value === "number"
                      ? value.toFixed(4)
                      : value}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

export default LogDetailsModal;
