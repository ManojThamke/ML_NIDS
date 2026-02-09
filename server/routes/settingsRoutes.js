const express = require("express");
const router = express.Router();

const {
  getSettings,
  saveSettings,
} = require("../controllers/settingsController");

/* ======================================================
   SETTINGS ROUTES – Phase-2 ML-NIDS
====================================================== */

/**
 * GET /api/settings
 * Fetch latest detection settings
 */
router.get("/", getSettings);

/**
 * POST /api/settings
 * Save / update detection settings
 */
router.post("/", saveSettings);

module.exports = router;
