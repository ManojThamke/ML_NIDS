import { useEffect } from "react";
import PerModelConfidenceChart from "./charts/PerModelConfidenceChart";

/* ================= COLOR + ICON HELPERS ================= */

const labelClass = (label) => {
  if (label === "ATTACK") return "bg-red-100 text-red-700";
  if (label === "SUSPICIOUS") return "bg-yellow-100 text-yellow-800";
  return "bg-green-100 text-green-700";
};

const labelEmoji = (label) => {
  if (label === "ATTACK") return "🚨";
  if (label === "SUSPICIOUS") return "⚠️";
  return "✅";
};

const severityClass = (severity) => {
  if (severity === "HIGH") return "bg-red-600 text-white";
  if (severity === "MEDIUM") return "bg-yellow-400 text-black";
  return "bg-green-200 text-green-800";
};

const confidenceBarClass = (confidence) => {
  if (confidence >= 0.7) return "bg-red-500";
  if (confidence >= 0.5) return "bg-yellow-400";
  return "bg-green-500";
};

function LogDetailsModal({ log, onClose }) {
  
  /* ===== ESC KEY CLOSE ===== */
  useEffect(() => {
    if (!log) return null;
    const handleEsc = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="log-details-title"
      onClick={onClose}   // ⬅ click outside closes
    >

      {/* OUTER MODAL */}
      <div
        className="bg-white rounded-2xl w-full max-w-4xl shadow-2xl relative"
        onClick={(e) => e.stopPropagation()} // ⬅ prevent inner clicks
      >

        {/* INNER SCROLL AREA */}
        <div className="max-h-[90vh] overflow-y-auto no-scrollbar p-6 rounded-2xl">

          {/* ❌ Close Button */}
          <button
            onClick={onClose}
            className="
              absolute top-5 right-5
              w-8 h-8 rounded-full
              flex items-center justify-center
              text-gray-500 hover:text-gray-800
              hover:bg-gray-100
              transition
            "
            aria-label="Close"
          >
            ✕
          </button>

          {/* ===== HEADER ===== */}
          <div className="mb-6">
            <h2
              id="log-details-title"
              className="text-xl font-bold tracking-wide"
            >
              Detection Log Details
            </h2>
          </div>

          {/* ===== SUMMARY GRID ===== */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm mb-6">

            {/* Timestamp */}
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-gray-500 text-xs uppercase tracking-wide">
                Timestamp
              </p>
              <p className="font-mono mt-1">
                {new Date(log.timestamp).toLocaleString()}
              </p>
            </div>

            {/* Ensemble Confidence */}
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">
                Ensemble Confidence
              </p>
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-3 rounded-full transition-all duration-700 ease-out ${confidenceBarClass(
                    log.confidence || 0
                  )}`}
                  style={{ width: `${(log.confidence || 0) * 100}%` }}
                />
              </div>
              <p className="text-sm font-semibold mt-1">
                {((log.confidence || 0) * 100).toFixed(2)}%
              </p>
            </div>

            {/* Source IP */}
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-gray-500 text-xs uppercase tracking-wide">
                Source IP
              </p>
              <p className="font-mono mt-1">{log.sourceIP}</p>
            </div>

            {/* Destination IP */}
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-gray-500 text-xs uppercase tracking-wide">
                Destination IP
              </p>
              <p className="font-mono mt-1">{log.destinationIP}</p>
            </div>

            {/* Final Label */}
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">
                Final Label
              </p>
              <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${labelClass(log.finalLabel)}`}>
                {labelEmoji(log.finalLabel)} {log.finalLabel}
              </span>
            </div>

            {/* Severity */}
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">
                Severity Level
              </p>
              <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${severityClass(log.severity)}`}>
                {log.severity === "HIGH"
                  ? "🔥"
                  : log.severity === "MEDIUM"
                  ? "⚠️"
                  : "🟢"}{" "}
                {log.severity}
              </span>
            </div>

            {/* Hybrid Decision */}
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">
                Hybrid Decision
              </p>
              <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${labelClass(log.hybridLabel)}`}>
                {labelEmoji(log.hybridLabel)} {log.hybridLabel}
              </span>
            </div>

            {/* Aggregation */}
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

          {/* ===== FLOW FEATURES ===== */}
          <div>
            <h3 className="font-semibold mb-3">
              Extracted Flow Features
            </h3>

            {!log.flowFeatures ||
            Object.keys(log.flowFeatures).length === 0 ? (
              <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg p-4 text-sm text-gray-700">
                <p className="font-medium mb-1">
                  Flow Features Not Persisted
                </p>
                <p className="text-gray-600">
                  Flow-level features are used internally for real-time detection.
                </p>
                <p className="italic text-gray-500 mt-1">
                  Stored selectively to optimize performance.
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
    </div>
  );
}

export default LogDetailsModal;
