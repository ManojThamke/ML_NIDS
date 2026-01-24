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
      <div className="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto p-6 relative shadow-2xl">

        {/* ❌ Close */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-gray-400 hover:text-gray-700 text-xl"
        >
          ✕
        </button>

        {/* ===== HEADER ===== */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold tracking-wide">
            Detection Log Details
          </h2>
          <span className="text-xs px-3 py-1 rounded-full bg-gray-100 text-gray-600">
            Real-Time NIDS Event
          </span>
        </div>

        {/* ===== SUMMARY CARDS ===== */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm mb-6">

          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-500 text-xs uppercase tracking-wide">
              Timestamp
            </p>
            <p className="font-mono mt-1">
              {new Date(log.timestamp).toLocaleString()}
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">
              Ensemble Confidence
            </p>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${confidenceBarClass(
                  log.confidence || 0
                )}`}
                style={{ width: `${(log.confidence || 0) * 100}%` }}
              />
            </div>
            <p className="text-sm font-semibold mt-1">
              {((log.confidence || 0) * 100).toFixed(2)}%
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-500 text-xs uppercase tracking-wide">
              Source IP
            </p>
            <p className="font-mono mt-1">{log.sourceIP}</p>
          </div>

          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-500 text-xs uppercase tracking-wide">
              Destination IP
            </p>
            <p className="font-mono mt-1">{log.destinationIP}</p>
          </div>

          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">
              Final Label
            </p>
            <span
              className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${labelClass(
                log.finalLabel
              )}`}
            >
              {log.finalLabel === "ATTACK" ? "🚨" : "✅"} {log.finalLabel}
            </span>
          </div>

          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">
              Severity Level
            </p>
            <span
              className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${severityClass(
                log.severity
              )}`}
            >
              {log.severity === "HIGH"
                ? "🔥"
                : log.severity === "MEDIUM"
                ? "⚠️"
                : "🟢"}{" "}
              {log.severity}
            </span>
          </div>

          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">
              Hybrid Decision
            </p>
            <span
              className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${labelClass(
                log.hybridLabel
              )}`}
            >
              {log.hybridLabel === "ATTACK" ? "🚨" : "✅"} {log.hybridLabel}
            </span>
          </div>

          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-500 text-xs uppercase tracking-wide">
              Aggregation Strategy
            </p>
            <p className="font-medium mt-1">
              {log.aggregationMethod || "Ensemble Voting"}
            </p>
          </div>

        </div>

        {/* ===== PER-MODEL CONFIDENCE ===== */}
        <div className="bg-gray-50 rounded-xl p-4 shadow-sm mb-8">
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

        {/* ===== EXTRACTED FLOW FEATURES ===== */}
        <div>
          <h3 className="font-semibold mb-3">
            Extracted Flow Features
          </h3>

          {!log.flowFeatures || Object.keys(log.flowFeatures).length === 0 ? (
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 border border-dashed border-gray-300 rounded-lg p-4 text-sm text-gray-700">
              <p className="font-medium mb-1">
                Flow Features Not Persisted
              </p>
              <p className="text-gray-600">
                Flow-level features were extracted in real time and used
                internally by the machine learning models for detection.
              </p>
              <p className="italic text-gray-500 mt-1">
                Feature values are not persisted to optimize real-time
                performance and storage efficiency.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              {Object.entries(log.flowFeatures).map(([key, value]) => (
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
