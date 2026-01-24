import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:5000/api",
});

/* ================= ALERTS & LOGS ================= */

export const getAlerts = () => API.get("/alerts");
export const getAlertStats = () => API.get("/alerts/stats");

export const getLogs = (params) =>
  API.get("/alerts/logs", { params });

export const exportLogs = (params) =>
  API.get("/alerts/export", {
    params,
    responseType: "blob",
  });

export const getLogsInsights = () =>
  API.get("/alerts/logs/insights");

export const getTrafficTimeline = (range = "24h") =>
  API.get(`/alerts/logs/timeline?range=${range}`);

export const getTopDestinations = () =>
  API.get("/alerts/logs/top-destinations");

/* ================= MONITORING ================= */

export const startMonitoring = () =>
  API.post("/monitor/start");

export const stopMonitoring = () =>
  API.post("/monitor/stop");

export const getMonitoringStatus = () =>
  API.get("/monitor/status");

/* ================= MODELS (EVALUATION ENGINE) ================= */

export const getModelMetrics = () =>
  API.get("/models/metrics");

export const getModelSummary = () =>
  API.get("/models/summary");

/* ================= STATS (OPERATIONAL ANALYTICS) ================= */

/* Distribution */
export const getDetectionDistribution = () =>
  API.get("/stats/distribution");

/* Confidence analytics (NOT evaluation) */
export const getConfidenceBands = () =>
  API.get("/stats/confidence/bands");

export const getPerModelAverageConfidence = () =>
  API.get("/stats/confidence/per-model");

export const getEnsembleVsBestModel = () =>
  API.get("/stats/confidence/ensemble-vs-best");

/* Model behavior analytics */
export const getModelDominanceFrequency = () =>
  API.get("/stats/models/dominance");

export const getModelAgreementMatrix = () =>
  API.get("/stats/models/agreement");

/* Attack intelligence */
export const getAttackTimeline = (range = "1h") =>
  API.get(`/stats/attacks/timeline?range=${range}`);

export const getTopAttackedDestinations = (limit = 5) =>
  API.get(`/stats/attacks/top-destinations?limit=${limit}`);

/* ================= DETECTIONS (OPTIONAL / LEGACY) ================= */

export const getRecentDetections = (limit = 10) =>
  API.get(`/detections/recent?limit=${limit}`);

export const getDetectionStats = () =>
  API.get("/detections/stats");

export const getDetectionLogs = (params) =>
  API.get("/detections/logs", { params });

export const exportDetectionLogs = (params) =>
  API.get("/detections/export", {
    params,
    responseType: "blob",
  });

export const getDetectionTimeline = (range = "24h") =>
  API.get(`/detections/timeline?range=${range}`);

/* ================= SETTINGS (PHASE-1) ================= */

export const getSettings = () =>
  API.get("/settings");

export const saveSettings = (data) =>
  API.post("/settings", data);

/* ================= SYSTEM ================= */

export const getSystemInterface = () =>
  API.get("/system/interface");
