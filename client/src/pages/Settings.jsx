import { useState, useEffect } from "react";
import {
  saveSettings,
  getSettings,
  getSystemInterface,
  getMonitoringStatus,
} from "../api";

/* ================= DEFAULTS (PHASE-1) ================= */
const DEFAULT_MODELS = [
  "rf",
  "lgb",
  "xgb",
  "svm",
  "knn",
  "mlp",
  "naive_bayes",
];

const DEFAULT_THRESHOLD = 0.4;

function Settings() {
  /* ================= STATE ================= */
  const [models, setModels] = useState(DEFAULT_MODELS);
  const [agg, setAgg] = useState("mean");
  const [smooth, setSmooth] = useState(3);
  const [threshold, setThreshold] = useState(DEFAULT_THRESHOLD);
  const [iface, setIface] = useState(""); // empty = auto-detect

  const [monitoring, setMonitoring] = useState(false);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  /* ================= MONITORING STATUS ================= */
  useEffect(() => {
    async function fetchStatus() {
      try {
        const res = await getMonitoringStatus();
        setMonitoring(res.data.running);
      } catch {
        setMonitoring(false);
      }
    }
    fetchStatus();
  }, []);

  /* ================= LOAD SAVED SETTINGS ================= */
  useEffect(() => {
    async function loadSettings() {
      try {
        const res = await getSettings();
        if (!res.data) return;

        setModels(res.data.models ?? DEFAULT_MODELS);
        setAgg(res.data.aggregation ?? "mean");
        setSmooth(res.data.smoothing ?? 3);
        setThreshold(res.data.threshold ?? DEFAULT_THRESHOLD);
        setIface(res.data.interface ?? "");
      } catch {
        console.warn("Using default settings");
      }
    }
    loadSettings();
  }, []);

  /* ================= AUTO-DETECT INTERFACE (ONCE) ================= */
  useEffect(() => {
    async function detectInterfaceOnce() {
      try {
        const res = await getSystemInterface();
        if (res.data?.interface) {
          setIface(res.data.interface);
        }
      } catch {
        console.warn("Auto interface detection failed");
      }
    }

    if (!iface) detectInterfaceOnce();
    // eslint-disable-next-line
  }, []);

  /* ================= HELPERS ================= */
  const toggleModel = (model) => {
    setModels((prev) =>
      prev.includes(model)
        ? prev.filter((m) => m !== model)
        : [...prev, model]
    );
  };

  const resetDefaults = () => {
    if (monitoring) return;

    setModels(DEFAULT_MODELS);
    setAgg("mean");
    setSmooth(3);
    setThreshold(DEFAULT_THRESHOLD);
    setIface("");
    setStatus("🔄 Settings reset to default values");
  };

  const applySettings = async () => {
    if (monitoring) {
      setStatus("⚠️ Stop monitoring before changing settings");
      return;
    }

    if (models.length === 0) {
      setStatus("⚠️ Please select at least one model");
      return;
    }

    try {
      setLoading(true);
      setStatus(null);

      await saveSettings({
        models,
        aggregation: agg,
        smoothing: smooth,
        threshold,
        interface: iface || "", // EMPTY STRING ONLY
      });


      setStatus("✅ Settings saved successfully");
    } catch {
      setStatus("❌ Failed to save settings");
    } finally {
      setLoading(false);
    }
  };

  const pythonCommand = `
python realtime_detector_multi.py \
--models ${models.join(",")} \
--agg ${agg} \
--smooth ${smooth} \
--threshold ${threshold} \
${iface ? `--iface "${iface}"` : ""} \
--run_mode service
`.trim();


  /* ================= UI ================= */
  return (
    <div className="p-8 space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Settings</h1>

      {monitoring && (
        <div className="bg-yellow-50 border border-yellow-300 text-yellow-800 px-4 py-2 rounded-lg text-sm">
          🔒 Monitoring is running. Stop monitoring to modify settings.
        </div>
      )}

      {/* ================= DETECTION SETTINGS ================= */}
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <h3 className="font-semibold text-gray-800 mb-4">
          Detection Settings (Phase-1)
        </h3>

        {/* Model Selection */}
        <div className="mb-6">
          <label className="text-sm font-medium text-gray-600 mb-2 block">
            Select Models
          </label>

          <div className="grid grid-cols-3 gap-3">
            {DEFAULT_MODELS.map((model) => (
              <button
                key={model}
                disabled={monitoring}
                onClick={() => toggleModel(model)}
                className={`px-4 py-2 rounded-full text-sm border transition
                  ${models.includes(model)
                    ? "bg-pink-100 border-pink-400 text-pink-700 font-semibold"
                    : "bg-gray-50 border-gray-300 text-gray-600"
                  }
                  ${monitoring ? "opacity-60 cursor-not-allowed" : "hover:bg-gray-100"}
                `}
              >
                {model.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Aggregation + Smoothing */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <label className="text-sm font-medium text-gray-600 mb-2 block">
              Aggregation Strategy
            </label>
            <select
              value={agg}
              disabled={monitoring}
              onChange={(e) => setAgg(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            >
              <option value="mean">Mean (Recommended)</option>
              <option value="max">Max</option>
              <option value="weighted">Weighted</option>
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-600 mb-2 block">
              Smoothing Window
            </label>
            <input
              type="number"
              min={1}
              max={10}
              value={smooth}
              disabled={monitoring}
              onChange={(e) => setSmooth(Number(e.target.value))}
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>
        </div>

        {/* Threshold */}
        <div>
          <label className="flex justify-between text-sm font-medium text-gray-600 mb-1">
            <span>Global Threshold</span>
            <span className="text-pink-600 font-semibold">{threshold}</span>
          </label>

          <input
            type="range"
            min={0}
            max={0.9}
            step={0.05}
            value={threshold}
            disabled={monitoring}
            onChange={(e) => setThreshold(Number(e.target.value))}
            className="w-full accent-pink-600"
          />

          <p className={`text-xs mt-1 ${threshold === 0
              ? "text-red-700 font-semibold"
              : threshold <= 0.3
                ? "text-red-600"
                : threshold <= 0.6
                  ? "text-yellow-600"
                  : "text-green-600"
            }`}>
            {threshold === 0 && "🚨 Testing mode: all traffic flagged"}
            {threshold > 0 && threshold <= 0.3 && "🔴 Less strict, more alerts"}
            {threshold > 0.3 && threshold <= 0.6 && "🟡 Balanced detection (recommended)"}
            {threshold > 0.6 && "🟢 More strict, fewer alerts"}
          </p>
        </div>
      </div>

      {/* ================= NETWORK ================= */}
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <h3 className="font-semibold text-gray-800 mb-4">
          Network Interface
        </h3>

        <select
          value={iface}
          disabled={monitoring}
          onChange={(e) => setIface(e.target.value)}
          className="w-full border rounded-lg px-3 py-2 text-sm"
        >
          <option value="">Auto Detect</option>
          <option value="Wi-Fi">Wi-Fi</option>
          <option value="Ethernet">Ethernet</option>
        </select>

        <p className="text-xs text-gray-500 mt-1">
          Active interface is auto-detected by default
        </p>
      </div>

      {/* ================= ACTIONS ================= */}
      <div className="flex justify-between items-center">
        <div className="flex gap-3">
          <button
            onClick={applySettings}
            disabled={loading || monitoring}
            className={`px-6 py-2 rounded-lg text-sm font-semibold text-white
              ${monitoring
                ? "bg-gray-400 cursor-not-allowed"
                : loading
                  ? "bg-pink-300"
                  : "bg-pink-600 hover:bg-pink-700"
              }`}
          >
            {monitoring ? "Monitoring Active" : loading ? "Saving…" : "Apply Settings"}
          </button>

          <button
            onClick={resetDefaults}
            disabled={monitoring}
            className="px-6 py-2 rounded-lg border text-gray-600 text-sm hover:bg-gray-50 disabled:opacity-60"
          >
            Reset to Default
          </button>
        </div>

        {status && (
          <div className="text-sm px-3 py-1 rounded-md bg-gray-50 border">
            {status}
          </div>
        )}
      </div>

      {/* ================= COMMAND PREVIEW ================= */}
      <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <p className="text-xs text-gray-400 mb-2">
          Detection Engine Command (Preview)
        </p>
        <pre className="text-green-400 text-sm font-mono whitespace-pre-wrap">
          {pythonCommand}
        </pre>
      </div>
    </div>
  );
}

export default Settings;
