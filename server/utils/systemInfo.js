const os = require("os");

/**
 * Return ALL usable network interfaces (friendly names)
 * Windows / Linux / macOS safe
 */
function getSystemInterfaces() {
  const nets = os.networkInterfaces();
  const results = new Set();

  for (const name of Object.keys(nets)) {
    for (const net of nets[name]) {
      if (net.internal) continue;
      if (net.family !== "IPv4") continue;

      const lname = name.toLowerCase();

      // Ignore junk / virtual noise
      if (
        lname.includes("loopback") ||
        lname.includes("docker") ||
        lname.includes("vmware")
      ) continue;

      // Normalize names for UI
      if (lname.includes("wi-fi") || lname.includes("wifi")) {
        results.add("Wi-Fi");
      }
      else if (lname.includes("ethernet")) {
        results.add(name); // Ethernet / Ethernet 2
      }
      else if (lname.includes("virtualbox") || lname.includes("host-only")) {
        results.add("VirtualBox Host-Only");
      }
      else {
        results.add(name);
      }
    }
  }

  return Array.from(results);
}

module.exports = { getSystemInterfaces };
