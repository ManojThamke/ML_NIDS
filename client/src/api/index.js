import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:5000/api",
});

export const getAlerts = () => API.get("/alerts");
export const getAlertStats = () => API.get("/alerts/stats");

export const startMonitoring = () => API.post("/monitor/start");
export const stopMonitoring = () => API.post("/monitor/stop");
export const getMonitoringStatus = () => API.get("/monitor/status");
export const getModelMetrics = () => API.get("/model-metrics");
export const getLogs = (params) => API.get("/alerts/logs", { params });
export const exportLogs = (params) => API.get("/alerts/export", { params, responseType: 'blob' });
export const getLogsInsights = () => API.get("/alerts/logs/insights");
export const getTrafficTimeline = (range = "24h") => API.get(`/alerts/logs/timeline?range=${range}`);
export const getTopDestinations = () => API.get("/alerts/logs/top-destinations");
export const getDetectionDistribution = () => API.get("/stats/detection-distribution");
export const getProbabilityBands = () => API.get("/stats/probability-bands");