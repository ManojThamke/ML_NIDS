const os = require("os");

function getActiveInterface() {
  const nets = os.networkInterfaces();

  let wifi = null;
  let ethernet = null;

  for (const name of Object.keys(nets)) {
    for (const net of nets[name]) {
      if (net.family !== "IPv4" || net.internal) continue;

      const lname = name.toLowerCase();

      // Prefer Wi-Fi
      if (lname.includes("wi-fi") || lname.includes("wifi")) {
        wifi = name;
      }

      // Fallback Ethernet (ignore virtual)
      else if (
        lname.includes("ethernet") &&
        !lname.includes("virtual") &&
        !lname.includes("vethernet") &&
        !lname.includes("docker")
      ) {
        ethernet = name;
      }
    }
  }

  return wifi || ethernet || "Wi-Fi";
}

module.exports = { getActiveInterface };
