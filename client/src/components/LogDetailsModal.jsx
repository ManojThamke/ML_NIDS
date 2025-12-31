import PerModelProbabilityChart from "./charts/PerModelProbabilityChart";

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
        <h2 className="text-xl font-bold mb-4">Log Details</h2>

        <div className="grid grid-cols-2 gap-y-2 text-sm mb-6">
          <p><b>Time:</b> {new Date(log.timestamp).toLocaleString()}</p>
          <p><b>Final Label:</b> {log.finalLabel}</p>

          <p><b>Source IP:</b> {log.sourceIP}</p>
          <p><b>Destination IP:</b> {log.destinationIP}</p>

          <p><b>Final Probability:</b> {(log.probability * 100).toFixed(2)}%</p>
          <p><b>Model Used:</b> {log.modelUsed || "ENSEMBLE"}</p>
        </div>

        {/* ===== PER MODEL PROBABILITY ===== */}
        <div className="mb-10">
          <h3 className="font-semibold mb-3">
            Per-Model Probability (Explainability)
          </h3>

          {/* ✅ PASS PROP CORRECTLY */}
          <PerModelProbabilityChart perModel={log.perModel} />
        </div>

        {/* ===== EXTRACTED FEATURES ===== */}
        <div>
          <h3 className="font-semibold mb-3">
            Extracted Features
          </h3>

          {!log.features || Object.keys(log.features).length === 0 ? (
            <p className="text-gray-500 text-sm">
              No feature data available
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
                      ? value.toString()
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
