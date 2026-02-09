const { getSystemInterfaces } = require("../utils/systemInfo");

const getSystemInterface = (req, res) => {
  try {
    const interfaces = getSystemInterfaces();
    res.json(interfaces);   // ✅ ARRAY
  } catch (err) {
    res.status(500).json([]);
  }
};

module.exports = { getSystemInterface };
