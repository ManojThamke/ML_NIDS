import { useEffect, useState } from "react";
import { getLogsInsights } from "../api";

function LogsInsights() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getLogsInsights()
      .then((res) => setData(res.data))
      .catch(console.error);
  }, []);

  if (!data) return null;

  return (
    <div className="grid grid-cols-4 gap-4 mb-6">
      
      {/* 🔝 Top Source IPs */}
      <InsightCard title="Top Source IPs">
        {data.topSourceIPs.map((ip) => (
          <Row key={ip._id} label={ip._id} value={ip.count} />
        ))}
      </InsightCard>

      {/* 🎯 Top Destination IPs */}
      <InsightCard title="Top Destination IPs">
        {data.topDestinationIPs.map((ip) => (
          <Row key={ip._id} label={ip._id} value={ip.count} />
        ))}
      </InsightCard>

      {/* 📊 Traffic Distribution */}
      <InsightCard title="Traffic Distribution">
        <p className="text-sm text-gray-600">
          🟢 Benign: <b>{data.benignCount}</b>
        </p>
        <p className="text-sm text-gray-600">
          🔴 Attack: <b>{data.attackCount}</b>
        </p>
      </InsightCard>

      {/* 🚨 High Risk Logs */}
      <InsightCard title="High Risk Logs">
        <p className="text-3xl font-bold text-red-600">
          {data.highRiskCount}
        </p>
        <p className="text-xs text-gray-500">
          Probability ≥ 70%
        </p>
      </InsightCard>
    </div>
  );
}

/* =====================
   Helper Components
===================== */

function InsightCard({ title, children }) {
  return (
    <div className="bg-white rounded-xl p-4 shadow border">
      <h3 className="text-sm font-semibold mb-2 text-gray-700">
        {title}
      </h3>
      {children}
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between text-sm py-1">
      <span className="font-mono text-gray-700 truncate">
        {label}
      </span>
      <span className="font-semibold">{value}</span>
    </div>
  );
}

export default LogsInsights;
