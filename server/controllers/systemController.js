const { getActiveInterface } = require("../utils/systemInfo");

const getSystemInterface = (req, res) => {
  const iface = getActiveInterface();
  res.json({ interface: iface });
};

module.exports = { getSystemInterface };
