"""
Helper-Funktion: Feature-Namen-Mapping für LEAKAGE_REMOVED Datensätze
"""

def get_feature_names_mapping():
    """
    Erstelle ein Mapping von Feature-Indizes zu echten Namen
    für die LEAKAGE_REMOVED Datensätze
    """
    
    # Original-Feature-Namen (aus UNSW-NB15)
    original_mapping = {
        0: "dur",                  # Connection Duration
        1: "proto",                # Protocol Type
        2: "service",              # Service Type
        3: "state",                # Connection State
        4: "spkts",                # Source Packets
        5: "dpkts",                # Dest Packets
        6: "sbytes",               # Source Bytes
        7: "dbytes",               # Dest Bytes
        8: "rate",                 # Data Rate
        9: "sttl",                 # Source TTL
        10: "dttl",                # Dest TTL
        11: "sload",               # Source Load
        12: "dload",               # Dest Load
        13: "sloss",               # Source Loss
        14: "dloss",               # Dest Loss
        15: "sinpkt",              # Source Inter-packet time
        16: "dinpkt",              # Dest Inter-packet time
        17: "sjit",                # Source Jitter
        18: "djit",                # Dest Jitter
        19: "swin",                # TCP Source Window
        20: "stcpb",               # TCP Source Sequence
        21: "dtcpb",               # TCP Dest Sequence
        22: "dwin",                # TCP Dest Window
        23: "tcprtt",              # TCP RoundTrip Time
        24: "synack",              # TCP SYN-ACK Time
        25: "ackdat",              # TCP ACK-Data Time
        26: "smean",               # Source Mean Packet Size
        27: "dmean",               # Dest Mean Packet Size
        28: "trans_depth",         # HTTP Transaction Depth
        29: "response_body_len",   # Response Body Length
        30: "ct_srv_src",          # Count Srv Src
        31: "ct_state_ttl",        # Count State TTL
        32: "ct_dst_ltm",          # Count Dst LTM
        33: "ct_src_dport_ltm",    # Count Src Dport LTM
        34: "ct_dst_sport_ltm",    # Count Dst Sport LTM
        35: "ct_dst_src_ltm",      # Count Dst Src LTM
        36: "is_ftp_login",        # Is FTP Login
        37: "ct_ftp_cmd",          # Count FTP Cmd
        38: "ct_flw_http_mthd",    # Count Flow HTTP Method
        39: "ct_src_ltm",          # Count Src LTM
        40: "ct_srv_dst",          # Count Srv Dst
        41: "is_sm_ips_ports",     # Is Same IPs Ports
    }
    
    # Descriptive names
    descriptive_names = {
        0: "Connection Duration (sec)",
        1: "Protocol Type",
        2: "Service Type",
        3: "Connection State",
        4: "Source Packets",
        5: "Destination Packets",
        6: "Source Bytes",
        7: "Destination Bytes",
        8: "Data Rate (bytes/sec)",
        9: "Source TTL",
        10: "Destination TTL",
        11: "Source Data Load",
        12: "Destination Data Load",
        13: "Source Packet Loss",
        14: "Destination Packet Loss",
        15: "Source Inter-Packet Time",
        16: "Destination Inter-Packet Time",
        17: "Source Jitter",
        18: "Destination Jitter",
        19: "TCP Source Window",
        20: "TCP Source Sequence",
        21: "TCP Destination Sequence",
        22: "TCP Destination Window",
        23: "TCP Round-Trip Time",
        24: "TCP SYN-ACK Time",
        25: "TCP ACK-Data Time",
        26: "Source Mean Packet Size",
        27: "Destination Mean Packet Size",
        28: "HTTP Transaction Depth",
        29: "Server Response Body Length",
        30: "Connections per Service",
        31: "State-TTL Combinations",
        32: "Connections to Destination (LTM)",
        33: "Connections from Source to Dest Port (LTM)",
        34: "Connections from Source to IP Port (LTM)",
        35: "Connections between Source-Dest",
        36: "FTP Login Attempt",
        37: "FTP Command Count",
        38: "HTTP Method Count",
        39: "Connections from Source (LTM)",
        40: "Connections to Service",
        41: "Same Source-Dest IP and Port",
    }
    
    return original_mapping, descriptive_names


def get_top_features_summary():
    """
    Gibt eine Zusammenfassung der Top-Features aus der Decision Tree Analyse
    """
    original_mapping, descriptive_names = get_feature_names_mapping()
    
    top_features = [
        {"index": 0, "original": "dur", "importance": 0.6935, "rank": 1},
        {"index": 7, "original": "sbytes", "importance": 0.2994, "rank": 2},
        {"index": 12, "original": "dload", "importance": 0.0055, "rank": 3},
        {"index": 29, "original": "response_body_len", "importance": 0.0016, "rank": 4},
    ]
    
    return top_features


if __name__ == "__main__":
    original_mapping, descriptive_names = get_feature_names_mapping()
    
    print("=" * 80)
    print("FEATURE-NAMEN MAPPING für LEAKAGE_REMOVED Datensätze")
    print("=" * 80)
    
    print("\n🔝 TOP 4 FEATURES (aus Decision Tree):")
    for feature in get_top_features_summary():
        idx = feature["index"]
        print(f"\n#{feature['rank']}: Feature {idx}")
        print(f"   Original Name: {feature['original']}")
        print(f"   Description: {descriptive_names[idx]}")
        print(f"   Importance: {feature['importance']:.4f}")
    
    print("\n" + "=" * 80)
    print("ALLE FEATURES MAPPING (42 numerische):")
    print("=" * 80)
    for idx, name in original_mapping.items():
        print(f"  {idx:2d}: {name:20s} → {descriptive_names[idx]}")

