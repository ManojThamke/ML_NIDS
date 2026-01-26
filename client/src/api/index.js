import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:5000/api",
});

/* =====================================================
   ALERTS (PRIMARY PIPELINE OUTPUT)
===================================================== */

/* Latest alerts (dashboard table) */
export const getAlerts = () => API.get("/alerts");

/* Alert summary cards */
export const getAlertStats = () => API.get("/alerts/stats");

/* Alert logs (filter + pagination) */
export const getAlertLogs = (params) =>
  API.get("/alerts/logs", { params });

/* Export alerts */
export const exportAlertLogs = (params) =>
  API.get("/alerts/export", {
    params,
    responseType: "blob",
  });

/* ALERTS */
export const getAlertInsights = () =>
  API.get("/alerts/logs/insights");

export const getAlertTimeline = (range = "24h") =>
  API.get(`/alerts/logs/timeline?range=${range}`);

export const getAlertTopDestinations = (limit = 5) =>
  API.get(`/alerts/logs/top-destinations?limit=${limit}`);



/* =====================================================
   MONITORING (REAL-TIME ENGINE CONTROL)
===================================================== */

export const startMonitoring = () =>
  API.post("/monitor/start");

export const stopMonitoring = () =>
  API.post("/monitor/stop");

export const getMonitoringStatus = () =>
  API.get("/monitor/status");


/* =====================================================
   MODELS (EVALUATION ENGINE – UPCOMING)
===================================================== */

export const getModelMetrics = () =>
  API.get("/models/metrics");

export const getModelSummary = () =>
  API.get("/models/summary");


/* =====================================================
   STATS (ANALYTICS, NOT RAW LOGS)
===================================================== */

/* Distribution */
export const getDetectionDistribution = () =>
  API.get("/stats/distribution");

/* Confidence analytics */
export const getConfidenceBands = () =>
  API.get("/stats/confidence/bands");

export const getPerModelAverageConfidence = () =>
  API.get("/stats/confidence/per-model");

export const getEnsembleVsBestModel = () =>
  API.get("/stats/confidence/ensemble-vs-best");

/* Model behavior */
export const getModelDominanceFrequency = () =>
  API.get("/stats/models/dominance");

export const getModelAgreementMatrix = () =>
  API.get("/stats/models/agreement");

/* Attack intelligence */
export const getAttackTimeline = (range = "24h") =>
  API.get(`/stats/attacks/timeline?range=${range}`);

export const getTopAttackedDestinations = (limit = 5) =>
  API.get(`/stats/attacks/top-destinations?limit=${limit}`);


/* =====================================================
   DETECTIONS (LEGACY / RAW PYTHON OUTPUT)
===================================================== */

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


/* =====================================================
   SETTINGS
===================================================== */

export const getSettings = () =>
  API.get("/settings");

export const saveSettings = (data) =>
  API.post("/settings", data);


/* =====================================================
   SYSTEM
===================================================== */

export const getSystemInterface = () =>
  API.get("/system/interface");

