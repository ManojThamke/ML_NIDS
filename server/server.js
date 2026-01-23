const express = require("express");
const cors = require("cors");
require("dotenv").config();

const connectDB = require("./config/db");
const alertRoutes = require("./routes/alertRoutes");
const monitorRoutes = require("./routes/monitorRoutes");
const modelRoutes = require("./routes/modelRoutes")
const statsRoutes = require("./routes/statsRoutes");
const settingsRoutes = require("./routes/settingsRoutes");
const systemRoutes = require("./routes/systemRoutes");
const detectionRoutes = require("./routes/detectionroutes");

const app = express();
const PORT = process.env.PORT || 5000;

/* =======================
   Database Connection
======================= */
connectDB();

/* =======================
   Middlewares
======================= */
app.use(cors());
app.use(express.json());

/* =======================
   Routes
======================= */
app.use("/api/alerts", alertRoutes);   // Alerts API
app.use("/api/monitor", monitorRoutes); // Start/Stop monitoring
app.use("/api/models", require("./routes/modelRoutes"));  //models comparison
app.use("/api/stats", require("./routes/statsRoutes")); // Stats API
app.use("/api/settings", settingsRoutes);
app.use("/api/system", systemRoutes);
app.use("/api/detections", detectionRoutes); // Detection Logs

/* =======================
   Health Check
======================= */
app.get("/", (req, res) => {
  res.send("MongoDB Connected ✅ | ML-NIDS Backend Running");
});

/* =======================
   Server Start
======================= */
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
