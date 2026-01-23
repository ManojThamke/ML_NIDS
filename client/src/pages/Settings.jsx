import { useState, useEffect } from "react";
import {
  saveSettings,
  getSettings,
  getSystemInterface,
  getMonitoringStatus,
} from "../api";

/* ================= DEFAULTS (PHASE-2) ================= */

const DEFAULT_MODELS = [
  "LogisticRegression",
  "DecisionTree",
  "RandomForest",
  "KNN",
  "NaiveBayes",
  "GradientBoosting",
  "XGBoost",
  "LightGBM",
  "MLP",
];

const DEFAULT_THRESHOLD = 0.5;
const DEFAULT_VOTE_K = 3;
const DEFAULT_FLOW_TIMEOUT = 10;

function Settings() {
  /* ================= STATE ================= */

  const [models, setModels] = useState(DEFAULT_MODELS);
  const [threshold, setThreshold] = useState(DEFAULT_THRESHOLD);
  const [voteK, setVoteK] = useState(DEFAULT_VOTE_K);
  const [flowTimeout, setFlowTimeout] = useState(DEFAULT_FLOW_TIMEOUT);
  const [iface, setIface] = useState("");

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
        setThreshold(res.data.threshold ?? DEFAULT_THRESHOLD);
        setVoteK(res.data.voteK ?? DEFAULT_VOTE_K);
        setFlowTimeout(res.data.flowTimeout ?? DEFAULT_FLOW_TIMEOUT);
        setIface(res.data.interface ?? "");
      } catch {
        console.warn("Using default Phase-2 settings");
      }
    }
    loadSettings();
  }, []);

  /* ================= AUTO-DETECT INTERFACE ================= */

  useEffect(() => {
    async function detectInterface() {
      try {
        const res = await getSystemInterface();
        if (res.data?.interface) {
          setIface(res.data.interface);
        }
      } catch {
        console.warn("Interface auto-detection failed");
      }
    }

    if (!iface) detectInterface();
    // eslint-disable-next-line
  }, []);

  /* ================= HELPERS ================= */

  const toggleModel = (model) => {
    setModels((prev) => {
      // 🔒 Enforce at least one model
      if (prev.length === 1 && prev.includes(model)) {
        setStatus("⚠️ At least one model must be selected");
        return prev;
      }

      const updated = prev.includes(model)
        ? prev.filter((m) => m !== model)
        : [...prev, model];

      // Adjust voteK if needed
      if (voteK > updated.length) {
        setVoteK(updated.length);
      }

      return updated;
    });
  };

  const resetDefaults = () => {
    if (monitoring) return;

    setModels(DEFAULT_MODELS);
    setThreshold(DEFAULT_THRESHOLD);
    setVoteK(DEFAULT_VOTE_K);
    setFlowTimeout(DEFAULT_FLOW_TIMEOUT);
    setIface("");
    setStatus("🔄 Settings reset to Phase-2 defaults");
  };

  const applySettings = async () => {
    if (monitoring) {
      setStatus("⚠️ Stop monitoring before changing settings");
      return;
    }

    if (models.length === 0) {
      setStatus("⚠️ Select at least one model");
      return;
    }

    if (!iface) {
      setStatus("⚠️ Network interface is required");
      return;
    }

    try {
      setLoading(true);
      setStatus(null);

      await saveSettings({
        models,
        threshold,
        voteK,
        flowTimeout,
        interface: iface,
      });

      setStatus("✅ Settings saved successfully");
    } catch {
      setStatus("❌ Failed to save settings");
    } finally {
      setLoading(false);
    }
  };

  /* ================= COMMAND PREVIEW ================= */

  const pythonCommand = `
python detector_live_capture_v2.py \\
--iface "${iface || "<auto-detect>"}" \\
--models ${models.join(",")} \\
--threshold ${threshold} \\
--vote ${voteK} \\
--timeout ${flowTimeout} \\
--run_mode service
`.trim();

  /* ================= UI ================= */

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">
        Detection Settings (Phase-2)
      </h1>

      {monitoring && (
        <div className="bg-yellow-50 border border-yellow-300 text-yellow-800 px-4 py-2 rounded-lg text-sm">
          🔒 Monitoring is running. Stop monitoring to modify settings.
        </div>
      )}

      {/* ================= MODELS ================= */}
      <div className="bg-white rounded-xl p-6 shadow border">
        <h3 className="font-semibold mb-4">Model Selection</h3>

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
                ${monitoring
                  ? "opacity-60 cursor-not-allowed"
                  : "hover:bg-gray-100"
                }
              `}
            >
              {model}
            </button>
          ))}
        </div>
      </div>

      {/* ================= THRESHOLD ================= */}
      <div className="bg-white rounded-xl p-6 shadow border">
        <label className="flex justify-between text-sm font-medium mb-2">
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
      </div>

      {/* ================= VOTING ================= */}
      <div className="bg-white rounded-xl p-6 shadow border grid grid-cols-2 gap-6">
        <div>
          <label className="text-sm font-medium block mb-1">
            Vote-K (Ensemble)
          </label>
          <input
            type="number"
            min={1}
            max={models.length}
            value={voteK}
            disabled={monitoring}
            onChange={(e) => setVoteK(Number(e.target.value))}
            className="w-full border rounded px-3 py-2 text-sm"
          />
          <p className="text-xs text-gray-500 mt-1">
            Must be ≤ number of selected models
          </p>
        </div>

        <div>
          <label className="text-sm font-medium block mb-1">
            Flow Timeout (seconds)
          </label>
          <input
            type="number"
            min={1}
            value={flowTimeout}
            disabled={monitoring}
            onChange={(e) => setFlowTimeout(Number(e.target.value))}
            className="w-full border rounded px-3 py-2 text-sm"
          />
        </div>
      </div>

      {/* ================= NETWORK ================= */}
      <div className="bg-white rounded-xl p-6 shadow border">
        <label className="text-sm font-medium block mb-1">
          Network Interface
        </label>
        <select
          value={iface}
          disabled={monitoring}
          onChange={(e) => setIface(e.target.value)}
          className="w-full border rounded px-3 py-2 text-sm"
        >
          <option value="">Auto Detect</option>
          <option value="Wi-Fi">Wi-Fi</option>
          <option value="Ethernet">Ethernet</option>
        </select>
        <p className="text-xs text-gray-500 mt-1">
          Active interface is auto-detected by backend if left empty
        </p>
      </div>

      {/* ================= ACTIONS ================= */}
      <div className="flex gap-4">
        <button
          onClick={applySettings}
          disabled={loading || monitoring}
          className="px-6 py-2 rounded-lg bg-pink-600 text-white font-semibold disabled:opacity-60"
        >
          {loading ? "Saving…" : "Apply Settings"}
        </button>

        <button
          onClick={resetDefaults}
          disabled={monitoring}
          className="px-6 py-2 rounded-lg border text-gray-600"
        >
          Reset to Default
        </button>
      </div>

      {status && (
        <div className="text-sm px-3 py-2 border rounded bg-gray-50">
          {status}
        </div>
      )}

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
