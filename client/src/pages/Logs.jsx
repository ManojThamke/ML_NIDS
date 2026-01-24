import { useEffect, useState, useCallback } from "react";
import { getLogs, exportLogs } from "../api";

import TrafficTimelineChart from "../components/charts/TrafficTimelineChart";
import TopAttackedDestinationsChart from "../components/charts/TopAttackedDestinationsChart";
import ExportLogsModal from "../components/ExportLogsModal";
import LogsInsights from "../components/LogsInsights";
import LogDetailsModal from "../components/LogDetailsModal";

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

function Logs() {
  const [logs, setLogs] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedLog, setSelectedLog] = useState(null);

  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const [showExportModal, setShowExportModal] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [label, setLabel] = useState("");
  const [search, setSearch] = useState("");
  const [minProb, setMinProb] = useState("");
  const [maxProb, setMaxProb] = useState("");

  /* ================= FETCH LOGS ================= */
  const fetchLogs = useCallback(async () => {
    try {
      logs.length === 0 ? setLoading(true) : setRefreshing(true);

      const res = await getLogs({
        page,
        limit: 50,
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
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-2xl font-bold">Traffic Logs</h1>

      <LogsInsights />

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 shadow border grid grid-cols-6 gap-4">
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
          <option value="SUSPICIOUS">Suspicious</option>
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
          placeholder="Min Confidence"
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
          placeholder="Max Confidence"
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

        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={showAdvanced}
            onChange={() => setShowAdvanced(!showAdvanced)}
          />
          Advanced
        </label>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-4 text-sm">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={() => setAutoRefresh(!autoRefresh)}
            className="accent-pink-500"
          />
          Auto Refresh (5s)
        </label>

        {refreshing && (
          <span className="text-xs text-gray-500 animate-pulse">
            Refreshing…
          </span>
        )}

        <div className="ml-auto">
          <button
            onClick={() => setShowExportModal(true)}
            className="px-4 py-2 rounded-lg border border-pink-300 text-pink-600 hover:bg-pink-50"
          >
            📤 Export
          </button>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-8">
          <TrafficTimelineChart />
        </div>
        <div className="col-span-4">
          <TopAttackedDestinationsChart />
        </div>
      </div>

      {/* Logs Table */}
      <div className="overflow-x-auto bg-white rounded-xl shadow border">
        <table className="min-w-full text-sm text-center">
          <thead className="bg-gray-100 uppercase text-xs">
            <tr>
              <th className="px-3 py-2">Time</th>
              <th className="px-3 py-2">Source IP</th>
              <th className="px-3 py-2">Destination IP</th>
              <th className="px-3 py-2">Confidence</th>
              <th className="px-3 py-2">ML</th>
              <th className="px-3 py-2">Hybrid</th>
              <th className="px-3 py-2">Severity</th>
              {showAdvanced && (
                <>
                  <th className="px-3 py-2">Protocol</th>
                  <th className="px-3 py-2">Port</th>
                  <th className="px-3 py-2">Reason</th>
                </>
              )}
            </tr>
          </thead>

          <tbody>
            {!loading &&
              logs.map((log) => (
                <tr
                  key={log._id}
                  onClick={() => setSelectedLog(log)}
                  className="border-b hover:bg-gray-50 cursor-pointer"
                >
                  <td className="px-3 py-2 font-mono">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-3 py-2 font-mono">{log.sourceIP}</td>
                  <td className="px-3 py-2 font-mono">{log.destinationIP}</td>
                  <td className="px-3 py-2 font-semibold">
                    {(log.confidence * 100).toFixed(2)}%
                  </td>

                  <td>
                    <span className={`px-3 py-1 rounded-full text-xs ${labelClass(log.finalLabel)}`}>
                      {log.finalLabel}
                    </span>
                  </td>

                  <td>
                    <span className={`px-3 py-1 rounded-full text-xs ${labelClass(log.hybridLabel)}`}>
                      {log.hybridLabel}
                    </span>
                  </td>

                  <td>
                    <span className={`px-3 py-1 rounded-full text-xs ${severityClass(log.severity)}`}>
                      {log.severity}
                    </span>
                  </td>

                  {showAdvanced && (
                    <>
                      <td className="text-xs">{log.protocol || "-"}</td>
                      <td className="text-xs">{log.dstPort || "-"}</td>
                      <td className="text-xs truncate max-w-[180px]">
                        {log.hybridReason || "-"}
                      </td>
                    </>
                  )}
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex justify-between items-center text-sm">
        <button
          disabled={page === 1}
          onClick={() => setPage(page - 1)}
          className="px-4 py-2 bg-gray-200 rounded"
        >
          Prev
        </button>

        <span>
          Page {page} / {totalPages}
        </span>

        <button
          disabled={page === totalPages}
          onClick={() => setPage(page + 1)}
          className="px-4 py-2 bg-gray-200 rounded"
        >
          Next
        </button>
      </div>

      <ExportLogsModal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        onExport={(options) => handleExport(options.format, options)}
      />

      {selectedLog && (
        <LogDetailsModal
          log={selectedLog}
          onClose={() => setSelectedLog(null)}
        />
      )}
    </div>
  );
}

export default Logs;
