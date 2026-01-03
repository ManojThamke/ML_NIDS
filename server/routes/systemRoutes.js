const express = require("express");
const router = express.Router();
const { getSystemInterface } = require("../controllers/systemController");

router.get("/interface", getSystemInterface);

module.exports = router;
