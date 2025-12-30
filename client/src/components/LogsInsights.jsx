import { useEffect, useState } from "react";
import { getLogsInsights } from "../api";

function LogsInsights() {
  const [data, setData] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  /* ================= FETCH INSIGHTS ================= */
  const fetchInsights = async (isBackground = false) => {
    try {
      if (isBackground) setRefreshing(true);
      const res = await getLogsInsights();
      setData(res.data);
    } catch (err) {
      console.error("Insights fetch failed:", err);
    } finally {
      setRefreshing(false);
    }
  };


  /* ================= INITIAL LOAD ================= */
  useEffect(() => {
    fetchInsights(false);
  }, []);

  /* ================= AUTO REFRESH ================= */
  useEffect(() => {
    const interval = setInterval(() => {
      fetchInsights(true);
    }, 2000); // ⏱ every 10 seconds (recommended)

    return () => clearInterval(interval);
  }, []);

  if (!data) return null;

  return (

    <div className="mb-6">
      {/* 🔄 Refresh indicator (NO LAYOUT SHIFT) */}
      <p
        className={`
          text-xs text-gray-400 mb-2 transition-opacity
          ${refreshing ? "opacity-100 animate-pulse" : "opacity-0"}
        `}
      >
        Updating insights…
      </p>

      <div className="
      grid grid-cols-1 
      md:grid-cols-2 
      lg:grid-cols-4 
      gap-5 mb-6
    ">

        {/* 🔝 Top Source IPs */}
        <InsightCard title="Top Source IPs" icon="📤">
          {data.topSourceIPs.map((ip) => (
            <Row key={ip._id} label={ip._id} value={ip.count} />
          ))}
        </InsightCard>

        {/* 🎯 Top Destination IPs */}
        <InsightCard title="Top Destination IPs" icon="📥">
          {data.topDestinationIPs.map((ip) => (
            <Row key={ip._id} label={ip._id} value={ip.count} />
          ))}
        </InsightCard>

        {/* 📊 Traffic Distribution */}
        <InsightCard title="Traffic Distribution" icon="📊">
          <StatDot color="green" label="Benign" value={data.benignCount} />
          <StatDot color="red" label="Attack" value={data.attackCount} />
        </InsightCard>

        {/* 🚨 High Risk Logs */}
        <InsightCard title="High Risk Logs" icon="🚨">
          <p className="text-3xl font-bold text-red-600 tracking-tight">
            {data.highRiskCount}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Probability ≥ 70%
          </p>
        </InsightCard>
      </div>
    </div>
  );
}

/* =====================
   Helper Components
===================== */

function InsightCard({ title, icon, children }) {
  return (
    <div
      className="
        bg-white rounded-xl p-4 border shadow-sm
        min-h-[150px]
        hover:shadow-md hover:-translate-y-[1px]
        transition-all duration-200
      "
    >
      <h3 className="
        text-sm font-semibold mb-3 text-gray-700 
        flex items-center gap-2
      ">
        <span className="text-base">{icon}</span>
        {title}
      </h3>

      <div className="space-y-1">
        {children}
      </div>
    </div>
  );
}

// Row Component
function Row({ label, value }) {
  return (
    <div className="flex justify-between items-center text-sm py-1">
      <span className="font-mono text-gray-700 truncate max-w-[70%]">
        {label}
      </span>
      <span className="font-semibold text-gray-900 tabular-nums">
        {value}
      </span>
    </div>
  );
}

// Traffic Distribution Dot
function StatDot({ color, label, value }) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <span
        className={`w-3 h-3 rounded-full ${color === "green" ? "bg-green-500" : "bg-red-500"
          }`}
      />
      <span className="text-gray-700">
        {label}: <b className="tabular-nums">{value}</b>
      </span>
    </div>
  );
}

export default LogsInsights;
