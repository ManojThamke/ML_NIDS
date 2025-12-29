import { useEffect, useState, useCallback, useMemo } from "react";
import { getLogs, exportLogs } from "../api";
import TrafficTimelineChart from "../components/charts/TrafficTimelineChart";
import ExportLogsModal from "../components/ExportLogsModal";

function Logs() {
  const [logs, setLogs] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const [loading, setLoading] = useState(false);        // first load
  const [refreshing, setRefreshing] = useState(false); // auto refresh

  // 📤 Export Modal
  const [showExportModal, setShowExportModal] = useState(false);

  // 🔄 Auto refresh
  const [autoRefresh, setAutoRefresh] = useState(false);

  // 🔎 Filters
  const [label, setLabel] = useState("");
  const [search, setSearch] = useState("");
  const [minProb, setMinProb] = useState("");
  const [maxProb, setMaxProb] = useState("");

  /* ================= FETCH LOGS ================= */
  const fetchLogs = useCallback(async () => {
    try {
      if (logs.length === 0) setLoading(true);
      else setRefreshing(true);

      const res = await getLogs({
        page,
        label,
        search,
        minProb,
        maxProb,
      });

      setLogs(res.data.logs);
      setTotalPages(res.data.totalPages);
    } catch (err) {
      console.error("Failed to fetch logs:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [page, label, search, minProb, maxProb, logs.length]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  /* ================= AUTO REFRESH ================= */
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, [autoRefresh, fetchLogs]);

  /* ================= EXPORT ================= */
  const handleExport = async (format, options) => {
    try {
      const res = await exportLogs({
        format,
        range: options.range,
        onlyAttack: options.onlyAttack,
      });

      const blob = new Blob([res.data], {
        type:
          format === "csv"
            ? "text/csv;charset=utf-8;"
            : "application/json;charset=utf-8;",
      });

      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = `traffic_logs_${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();

      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export failed:", err);
    }
  };


  /* ================= INSIGHTS (DAY 75) ================= */
  const insights = useMemo(() => {
    const sourceMap = {};
    let attack = 0;
    let benign = 0;
    let highRisk = 0;

    logs.forEach((l) => {
      sourceMap[l.sourceIP] = (sourceMap[l.sourceIP] || 0) + 1;
      l.finalLabel === "ATTACK" ? attack++ : benign++;
      if (l.probability >= 0.7) highRisk++;
    });

    const topSources = Object.entries(sourceMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3);

    return { attack, benign, highRisk, topSources };
  }, [logs]);

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-2xl font-bold">Traffic Logs</h1>

      {/* 📊 DAY 75 – LOGS INSIGHTS */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl shadow border">
          <p className="text-sm text-gray-500">Attack Logs</p>
          <p className="text-2xl font-bold text-red-600">{insights.attack}</p>
        </div>

        <div className="bg-white p-4 rounded-xl shadow border">
          <p className="text-sm text-gray-500">Benign Logs</p>
          <p className="text-2xl font-bold text-green-600">{insights.benign}</p>
        </div>

        <div className="bg-white p-4 rounded-xl shadow border">
          <p className="text-sm text-gray-500">High Risk Traffic</p>
          <p className="text-2xl font-bold text-yellow-600">
            {insights.highRisk}
          </p>
        </div>

        <div className="bg-white p-4 rounded-xl shadow border">
          <p className="text-sm text-gray-500 mb-1">Top Source IPs</p>
          {insights.topSources.map(([ip, count]) => (
            <p key={ip} className="text-xs font-mono">
              {ip} ({count})
            </p>
          ))}
        </div>
      </div>

      {/* 🔍 Filters */}
      <div className="bg-white rounded-xl p-4 shadow border grid grid-cols-5 gap-4">
        <select
          value={label}
          onChange={(e) => {
            setPage(1);
            setLabel(e.target.value);
          }}
          className="border rounded px-3 py-2"
        >
          <option value="">All</option>
          <option value="ATTACK">Attack</option>
          <option value="BENIGN">Benign</option>
        </select>

        <input
          placeholder="Search IP"
          value={search}
          onChange={(e) => {
            setPage(1);
            setSearch(e.target.value);
          }}
          className="border rounded px-3 py-2"
        />

        <input
          type="number"
          step="0.01"
          placeholder="Min Prob"
          value={minProb}
          onChange={(e) => {
            setPage(1);
            setMinProb(e.target.value);
          }}
          className="border rounded px-3 py-2"
        />

        <input
          type="number"
          step="0.01"
          placeholder="Max Prob"
          value={maxProb}
          onChange={(e) => {
            setPage(1);
            setMaxProb(e.target.value);
          }}
          className="border rounded px-3 py-2"
        />

        <button
          onClick={() => {
            setPage(1);
            setLabel("");
            setSearch("");
            setMinProb("");
            setMaxProb("");
          }}
          className="bg-gray-200 rounded px-3 py-2"
        >
          Reset
        </button>
      </div>

      {/* 🔄 Controls */}
      <div className="flex items-center gap-4 text-sm">
        <label className="flex items-center gap-2 font-medium">
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={() => setAutoRefresh(!autoRefresh)}
            className="accent-pink-500"
          />
          Auto Refresh (5s)
        </label>

        {autoRefresh && (
          <span className="text-green-600">Live updating enabled</span>
        )}

        {refreshing && (
          <span className={`text-xs text-gray-500 transition-opacity
           ${refreshing ? "opacity-100" : "opacity-0"}`}>
            Refreshing…
          </span>
        )}

        <div className="ml-auto flex gap-2">
          <button
            onClick={() => setShowExportModal(true)}
            className="px-4 py-2 rounded-lg border border-pink-300 text-pink-600 hover:bg-pink-50"
          >
            📤 Export
          </button>

        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <TrafficTimelineChart logs={logs} />
      </div>


      {/* 📊 Table */}
      <div className="overflow-x-auto bg-white rounded-xl shadow border min-h-[420px]">
        <table className="min-w-full table-fixed text-sm">
          <thead className="bg-gray-100 text-gray-600 uppercase sticky top-0 z-10">
            <tr>
              <th className="w-[22%] px-4 py-3 text-left">Time</th>
              <th className="w-[20%] px-4 py-3 text-left">Source IP</th>
              <th className="w-[20%] px-4 py-3 text-left">Destination IP</th>
              <th className="w-[18%] px-4 py-3 text-center">Probability</th>
              <th className="w-[20%] px-4 py-3 text-center">Label</th>
            </tr>
          </thead>

          <tbody>
            {loading && (
              <tr>
                <td colSpan="5" className="text-center py-8 text-gray-500">
                  Loading logs…
                </td>
              </tr>
            )}

            {!loading && logs.length === 0 && (
              <tr>
                <td colSpan="5" className="text-center py-8 text-gray-500">
                  No logs found
                </td>
              </tr>
            )}

            {!loading &&
              logs.map((log) => (
                <tr
                  key={log._id}
                  className={`border-b ${log.finalLabel === "ATTACK"
                    ? "bg-red-50 hover:bg-red-100"
                    : "hover:bg-gray-50"
                    }`}
                >
                  <td className="px-4 py-3 font-mono">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 font-mono">{log.sourceIP}</td>
                  <td className="px-4 py-3 font-mono">{log.destinationIP}</td>
                  <td className="px-4 py-3 text-center font-semibold">
                    {(log.probability * 100).toFixed(2)}%
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${log.finalLabel === "ATTACK"
                        ? "bg-red-100 text-red-700"
                        : "bg-green-100 text-green-700"
                        }`}
                    >
                      {log.finalLabel}
                    </span>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex justify-between items-center mt-4 text-sm">
        <button
          disabled={page === 1 || loading}
          onClick={() => setPage(page - 1)}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Prev
        </button>

        <span className="font-medium">
          Page {page} / {totalPages}
        </span>

        <button
          disabled={page === totalPages || loading}
          onClick={() => setPage(page + 1)}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>

      {/* 📤 Export Modal */}
      <ExportLogsModal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        onExport={(options) => {
          handleExport(options.format, options);
        }}
      />

    </div>
  );
}

export default Logs;
