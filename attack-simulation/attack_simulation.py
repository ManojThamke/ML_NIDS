import time

def simulate_attack_on_dashboard(logic_function):
    """
    Feeds a synthetic High-Risk DDoS attack into the NIDS logic.
    """
    # Synthetic feature vector based on CICIDS2018 (DDoS profile)
    # Characteristics: High flow duration, huge packet count, small packet size
    synthetic_attack_data = {
        'destination_port': 80,
        'flow_duration': 1500000,
        'total_fwd_packets': 5000,
        'total_backward_packets': 0,
        'fwd_packet_length_mean': 20.5,
        'flow_packets_per_s': 3333.33, # High frequency
        'timestamp': time.strftime('%H:%M:%S')
    }

    print(f"[{synthetic_attack_data['timestamp']}] 🚨 Injecting Synthetic DDoS Attack...")
    
    # Passing data to your hybrid logic function
    result = logic_function(synthetic_attack_data)
    
    return result

# Mock Hybrid Logic for Demonstration
def apply_hybrid_logic(data):
    if data['flow_packets_per_s'] > 2000:
        return "ALERT: HIGH-RISK DDOS DETECTED"
    return "Normal"

# Execution
status = simulate_attack_on_dashboard(apply_hybrid_logic)
print(f"System Output: {status}")