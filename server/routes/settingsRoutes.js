const express = require("express");
const router = express.Router();
const {
  getSettings,
  saveSettings,
} = require("../controllers/settingsController");

router.get("/", getSettings);   // fetch latest settings
router.post("/", saveSettings); // save new settings

module.exports = router;
