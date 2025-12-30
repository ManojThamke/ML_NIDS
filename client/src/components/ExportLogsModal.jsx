import { useState } from "react";

function ExportLogsModal({ isOpen, onClose, onExport }) {
  const [format, setFormat] = useState("csv");
  const [range, setRange] = useState("24h");
  const [onlyAttack, setOnlyAttack] = useState(false);
  const [includeMeta, setIncludeMeta] = useState(false);
  const [includeModelProb, setIncludeModelProb] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = () => {
    onExport({
      format,
      range,
      onlyAttack,
      includeMeta,
      includeModelProb,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="bg-white rounded-2xl w-[380px] p-6 shadow-xl relative">

        {/* ❌ Close */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-gray-400 hover:text-gray-600"
        >
          ✕
        </button>

        {/* Title */}
        <h2 className="text-xl font-bold mb-4 text-gray-800">
          Export Data
        </h2>

        {/* Export Format */}
        <div className="mb-4">
          <p className="text-sm font-medium mb-2">Export Format</p>

          <label className="flex items-center gap-2 mb-2">
            <input
              type="radio"
              checked={format === "csv"}
              onChange={() => setFormat("csv")}
              className="accent-pink-500"
            />
            CSV
          </label>

          <label className="flex items-center gap-2 mb-2">
            <input 
            type="radio" 
            checked={format === "json"}
            onChange={() => setFormat("json")}
            className="accent-pink-500" />
            JSON
          </label>
        </div>

        {/* Data Range */}
        <div className="mb-4">
          <p className="text-sm font-medium mb-2">Data Range</p>
          <select
            value={range}
            onChange={(e) => setRange(e.target.value)}
            className="w-full border rounded-lg px-3 py-2"
          >
            <option value="1h">Last 1 hour</option>
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
          </select>
        </div>

        {/* Options */}
        <div className="space-y-2 mb-5 text-sm">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={includeMeta}
              onChange={() => setIncludeMeta(!includeMeta)}
              className="accent-pink-500"
            />
            Include Raw Packet Metadata
          </label>

          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={includeModelProb}
              onChange={() => setIncludeModelProb(!includeModelProb)}
              className="accent-pink-500"
            />
            Include Per-Model Probabilities
          </label>

          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={onlyAttack}
              onChange={() => setOnlyAttack(!onlyAttack)}
              className="accent-pink-500"
            />
            Include Only ATTACK Alerts
          </label>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={handleSubmit}
            className="flex-1 bg-pink-500 hover:bg-pink-600 text-white py-2 rounded-lg font-medium"
          >
            Export
          </button>

          <button
            onClick={onClose}
            className="flex-1 border rounded-lg py-2"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

export default ExportLogsModal;
