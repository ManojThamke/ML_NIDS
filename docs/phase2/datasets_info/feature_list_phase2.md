# Phase-2 Feature List — Detailed Specification

**Project:** ML-Based Network Intrusion Detection System (ML-NIDS) — Phase 2
**File:** feature_list_phase2.md

This document lists the final 26 features for the Phase-2 advanced feature extractor.
Each entry contains: feature name, explanation, calculation, and why it helps detection.

---

# 🟦 A. FLOW-LEVEL FEATURES (5)

### **1. flow_duration** *(float)*

Total time between the first and last packet of the flow.
**Calc:** `last_timestamp - first_timestamp`
**Why:** DoS attacks → long flows; scans → extremely short flows.

### **2. total_fwd_packets** *(int)*

Packets from source → destination.
**Calc:** increment on forward packets.
**Why:** Asymmetry in packet counts reveals attacks.

### **3. total_bwd_packets** *(int)*

Packets from destination → source.
**Calc:** increment on backward packets.
**Why:** Detects one-way floods or unresponsive victims.

### **4. total_length_fwd** *(float)*

Sum of forward packet sizes.
**Calc:** `sum(len(pkt))` for forward direction.
**Why:** Data upload, flooding.

### **5. total_length_bwd** *(float)*

Sum of backward packet sizes.
**Why:** Detects response behaviors.

---

# 🟩 B. PACKET LENGTH FEATURES (4)

### **6. pkt_len_mean** *(float)*

Mean of packet sizes.
**Why:** Tool-generated attacks have uniform packet sizes.

### **7. pkt_len_std** *(float)*

Standard deviation of packet sizes.
**Why:** Low std = scripted floods.

### **8. fwd_pkt_len_min** *(int)*

Minimum forward packet size.
**Why:** Scans often use tiny packets.

### **9. bwd_pkt_len_min** *(int)*

Minimum backward packet size.
**Why:** Detect service fingerprinting patterns.

---

# 🟨 C. IAT (INTER-ARRIVAL TIME) FEATURES (4)

### **10. flow_iat_mean** *(float)*

Avg time between consecutive packets.
**Why:** Bots produce very stable IATs.

### **11. flow_iat_std** *(float)*

Std deviation of flow IAT.
**Why:** High variance = normal browsing; low variance = attack tools.

### **12. fwd_iat_mean** *(float)*

Avg IAT in forward direction only.
**Why:** Forward-only traffic indicates attacks.

### **13. bwd_iat_mean** *(float)*

Avg IAT in backward packets.
**Why:** Servers respond with predictable timing.

---

# 🟥 D. TCP FLAG COUNTERS (5)

### **14. fin_count** *(int)*

Number of FIN flags.
**Why:** FIN scans / session termination patterns.

### **15. syn_count** *(int)*

Number of SYN flags.
**Why:** SYN floods.

### **16. rst_count** *(int)*

Number of RST flags.
**Why:** Scanners abort connections with RST.

### **17. psh_count** *(int)*

Number of PSH flags.
**Why:** Used during bulk data transfer.

### **18. ack_count** *(int)*

Number of ACK flags.
**Why:** ACK storms / handshake analysis.

---

# 🟧 E. RATE FEATURES (2)

### **19. bytes_per_sec** *(float)*

Traffic throughput = total bytes / flow duration.
**Why:** DoS traffic has extremely high throughput.

### **20. pkts_per_sec** *(float)*

Packet rate = total packets / flow duration.
**Why:** Identifies high-rate floods.

---

# 🟪 F. ENTROPY & TRANSPORT FEATURES (3)

### **21. payload_entropy** *(float)*

Shannon entropy of payload bytes.
**Why:** High entropy = encrypted/tunneled traffic (often malicious).

### **22. ttl** *(int)*

Time-to-Live of packets (mean or mode).
**Why:** Spoofed packets often modify TTL.

### **23. window_size** *(int)*

Typical TCP window size (mean/mode).
**Why:** Useful for OS fingerprinting or anomaly detection.

---

# 🟫 G. PROTOCOL FLAGS (2)

### **24. is_tcp (0/1)**

Whether flow uses TCP.
**Why:** Enables TCP-specific logic.

### **25. is_udp (0/1)**

Whether flow uses UDP.
**Why:** Detect UDP floods, DNS attacks, etc.

---

# 🟦 H. UNIQUE FLOW BEHAVIOR FEATURE (1)

### **26. unique_dst_ports_in_flow** *(int)*

Number of unique destination ports accessed within the same flow key.
**Why:** Detects port scanning and sweeping.

---

# ✔ Notes & Implementation Rules

* Use **float** for time and rate features.
* Use **int** for counts and flags.
* Use **0/1** for protocol indicators.
* For real-time flows:

  * If backward packets are missing → set defaults safely.
  * Avoid divide-by-zero by adding small epsilon (`1e-6`).
* Ensure final output is a **26-length vector always**, even if some fields are missing.


