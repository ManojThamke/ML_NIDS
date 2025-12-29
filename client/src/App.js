import { useEffect, useState } from "react";
import { Routes, Route } from "react-router-dom";

import {
  getAlerts,
  getAlertStats,
  getMonitoringStatus,
} from "./api";

import Layout from "./layout/Layout";
import Dashboard from "./pages/Dashboard";
import Logs from "./pages/Logs";   // ✅ ADD THIS

function App() {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [monitoring, setMonitoring] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [alertsRes, statsRes, statusRes] = await Promise.all([
          getAlerts(),
          getAlertStats(),
          getMonitoringStatus(),
        ]);

        setAlerts(alertsRes.data);
        setStats(statsRes.data);
        setMonitoring(statusRes.data.running);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Layout monitoring={monitoring}>
      <Routes>
        {/* ✅ Dashboard */}
        <Route
          path="/"
          element={
            <Dashboard
              alerts={alerts}
              stats={stats}
              monitoring={monitoring}
              setMonitoring={setMonitoring}
            />
          }
        />

        {/* ✅ Logs Page */}
        <Route path="/logs" element={<Logs />} />

        {/* (Later) */}
        {/* <Route path="/stats" element={<StatsPage />} /> */}
        {/* <Route path="/models" element={<ModelsPage />} /> */}
        {/* <Route path="/settings" element={<SettingsPage />} /> */}
      </Routes>
    </Layout>
  );
}

export default App;
