import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:5000/api",
});

export const getAlerts = () => API.get("/alerts");
export const getAlertStats = () => API.get("/alerts/stats");

export const startMonitoring = () => API.post("/monitor/start");
export const stopMonitoring = () => API.post("/monitor/stop");
export const getMonitoringStatus = () => API.get("/monitor/status");
export const getModelMetrics = () => API.get("/models/metrics");
export const getModelSummary = () => API.get("/models/summary");
export const getLogs = (params) => API.get("/alerts/logs", { params });
export const exportLogs = (params) => API.get("/alerts/export", { params, responseType: 'blob' });
export const getLogsInsights = () => API.get("/alerts/logs/insights");
export const getTrafficTimeline = (range = "24h") => API.get(`/alerts/logs/timeline?range=${range}`);
export const getTopDestinations = () => API.get("/alerts/logs/top-destinations");
export const getDetectionDistribution = () => API.get("/stats/detection-distribution");
export const getConfidenceBands = () => API.get("/stats/confidence-bands");
export const getPerModelAverageConfidence = () => API.get("/stats/model-avg-confidence");
export const getModelDominanceFrequency = () => API.get("/stats/model-dominance-frequency");
export const getModelAgreementMatrix = () => API.get("/stats/model-agreement");
export const getEnsembleVsBestModel = () => API.get("/stats/ensemble-vs-best");
export const getAttackTimeline = (range = "1h") => API.get(`/stats/attack-timeline?range=${range}`);
export const getTopAttackedDestinations = (limit = 5) => API.get(`/stats/top-attacked-destinations?limit=${limit}`);
export const getRecentDetections = (limit = 10) => API.get(`/detections/recent?limit=${limit}`);
export const getDetectionStats = () => API.get("/detections/stats");
export const getDetectionLogs = (params) => API.get("/detections/logs", { params });
export const exportDetectionLogs = (params) => API.get("/detections/export", { params, responseType: 'blob' });
export const getDetectionTimeline = (range = "24h") => API.get(`/detections/timeline?range=${range}`);
// ================= SETTINGS (PHASE-1) =================

// Get latest detection settings
export const getSettings = () => API.get("/settings");

// Save / apply detection settings
export const saveSettings = (data) => API.post("/settings", data);

// auto i face or network connection type e.g.,Wi-Fi,Ethernet
export const getSystemInterface = () =>
  API.get("/system/interface");
