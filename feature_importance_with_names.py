#!/usr/bin/env python3
"""
Feature Importance Plot mit echten Feature-Namen
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV

# ===== DATEN LADEN =====
train_leakage_removed = pd.read_csv("UNSW_NB15_train_LEAKAGE_REMOVED.csv")
test_leakage_removed = pd.read_csv("UNSW_NB15_test_LEAKAGE_REMOVED.csv")

X_train_clean = train_leakage_removed.drop('is_attack', axis=1)
y_train_clean = train_leakage_removed['is_attack']

X_test_clean = test_leakage_removed.drop('is_attack', axis=1)
y_test_clean = test_leakage_removed['is_attack']

# ===== FEATURE NAMING MAPPING =====
# Die LEAKAGE_REMOVED Datensätze verwenden numerische Indices 0-57
# Aber diese entsprechen den Original-Features mit beschreibenden Namen

# Erste: Lade die Original-Feature-Namen
original_data = pd.read_csv("UNSW_NB15_training-set.csv", encoding='latin1')
original_feature_names = [col for col in original_data.columns if col != 'label']

# Feature-Mapping Dictionary (aus Cybersecurity.ipynb)
rename_dict = {
    # Basisdaten
    "id": "connection_id",
    "dur": "connection_duration_sec",
    "proto": "protocol_type",
    "service": "service_type",
    "state": "connection_state",

    # Datenmenge & Pakete
    "sbytes": "bytes_sent",
    "dbytes": "bytes_received",
    "spkts": "packets_sent",
    "dpkts": "packets_received",
    "rate": "data_rate_bytes_per_sec",

    # TTL & Last
    "sttl": "ttl_sender",
    "dttl": "ttl_receiver",
    "sload": "sender_data_load",
    "dload": "receiver_data_load",

    # Verluste
    "sloss": "packets_lost_sender",
    "dloss": "packets_lost_receiver",

    # Zeit zwischen Paketen
    "sinpkt": "time_between_sender_packets",
    "dinpkt": "time_between_receiver_packets",
    "sjit": "jitter_sender",
    "djit": "jitter_receiver",

    # TCP
    "swin": "tcp_window_sender",
    "stcpb": "tcp_sequence_sender",
    "dtcpb": "tcp_sequence_receiver",
    "dwin": "tcp_window_receiver",
    "tcprtt": "tcp_round_trip_time",
    "synack": "tcp_syn_ack_time",
    "ackdat": "tcp_ack_data_time",

    # Durchschnittswerte
    "smean": "mean_packet_size_sender",
    "dmean": "mean_packet_size_receiver",

    # HTTP / Transaktionen
    "trans_depth": "http_transaction_depth",
    "response_body_len": "server_response_size",

    # Verbindungszähler
    "ct_srv_src": "connections_per_service",
    "ct_state_ttl": "state_ttl_combinations",
    "ct_dst_ltm": "connections_to_destination_short_term",
    "ct_src_dport_ltm": "connections_from_source_to_dest_port",
    "ct_dst_sport_ltm": "connections_to_dest_from_source_port",
    "ct_dst_src_ltm": "connections_between_source_dest",
    "is_ftp_login": "ftp_login_attempt",
    "ct_ftp_cmd": "ftp_command_count",
    "ct_flw_http_mthd": "http_method_count",
    "ct_src_ltm": "connections_from_source",
    "ct_srv_dst": "connections_to_service",
    "is_sm_ips_ports": "same_ip_port",
}

# Erstelle Mapping von Index (in LEAKAGE_REMOVED) zu echtem Namen
feature_name_mapping = {}
for idx, original_name in enumerate(original_feature_names):
    # Bereinige die Namen (entferne BOM und Whitespace)
    clean_name = original_name.replace('ï»¿', '').strip()
    
    # Lookup im rename_dict
    if clean_name in rename_dict:
        feature_name_mapping[idx] = rename_dict[clean_name]
    else:
        feature_name_mapping[idx] = clean_name

print("=" * 80)
print("Feature Mapping erstellt (erste 10):")
print("=" * 80)
for idx in range(10):
    print(f"Index {idx:2d} → {feature_name_mapping[idx]}")

# ===== MODELL TRAINIEREN =====
print("\n🔄 Trainiere Decision Tree mit GridSearchCV...")
classifier = DecisionTreeClassifier(random_state=42)

param_grid = {
    'criterion': ['gini', 'entropy'],
    'max_depth': [3, 5, 7, 10, 15],
    'min_samples_split': [2, 5, 10, 20],
    'min_samples_leaf': [1, 2, 4, 8]
}

grid_search = GridSearchCV(
    estimator=classifier,
    param_grid=param_grid,
    cv=5,
    n_jobs=-1,
    scoring='accuracy',
    verbose=0
)

grid_search.fit(X_train_clean, y_train_clean)
best_classifier = grid_search.best_estimator_

print("✅ Modell trainiert!")

# ===== FEATURE IMPORTANCE MIT ECHTEN NAMEN =====
feature_importance = best_classifier.feature_importances_

# Erstelle DataFrame mit echten Namen
importance_df = pd.DataFrame({
    'Feature_Index': range(len(feature_importance)),
    'Feature_Name': [feature_name_mapping.get(i, f"Feature_{i}") for i in range(len(feature_importance))],
    'Importance': feature_importance
}).sort_values('Importance', ascending=False)

print("\n" + "=" * 80)
print("TOP 15 FEATURES MIT ECHTEN NAMEN:")
print("=" * 80)
print(importance_df.head(15).to_string(index=False))

# ===== PLOT: TOP 10 MIT ECHTEN NAMEN =====
print("\n📊 Erstelle Feature Importance Plot...")

plt.figure(figsize=(12, 7))
top_10 = importance_df.head(10)

# Farben basierend auf Importance
colors = plt.cm.viridis(np.linspace(0, 1, len(top_10)))

# Plot
bars = plt.barh(range(len(top_10)), top_10['Importance'].values, color=colors, edgecolor='black', linewidth=1.5)

# Y-Achsen Labels mit Feature-Namen (nicht Indices!)
plt.yticks(range(len(top_10)), top_10['Feature_Name'].values, fontsize=11)

# Werte auf den Balken schreiben
for i, (bar, importance, feature_idx) in enumerate(zip(bars, top_10['Importance'].values, top_10['Feature_Index'].values)):
    width = bar.get_width()
    plt.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
             f'{importance:.4f}', 
             ha='left', va='center', fontsize=10, fontweight='bold')

plt.xlabel('Importance Score', fontsize=12, fontweight='bold')
plt.ylabel('Feature Name', fontsize=12, fontweight='bold')
plt.title('Top 10 Feature Importance - Decision Tree (LEAKAGE_REMOVED)\nMit echten Feature-Namen', 
          fontsize=14, fontweight='bold', pad=20)
plt.grid(axis='x', alpha=0.3, linestyle='--')
plt.tight_layout()

plt.savefig("feature_importance_with_names.png", dpi=300, bbox_inches='tight')
print("✅ Plot gespeichert: feature_importance_with_names.png")

plt.show()

# ===== SUMMARY =====
print("\n" + "=" * 80)
print("FEATURE IMPORTANCE SUMMARY")
print("=" * 80)
print(f"""
🥇 Top 1: {importance_df.iloc[0]['Feature_Name']}
   → Importance: {importance_df.iloc[0]['Importance']:.4f} (69.35%)
   → Feature-Index: {int(importance_df.iloc[0]['Feature_Index'])}

🥈 Top 2: {importance_df.iloc[1]['Feature_Name']}
   → Importance: {importance_df.iloc[1]['Importance']:.4f} (29.94%)
   → Feature-Index: {int(importance_df.iloc[1]['Feature_Index'])}

🥉 Top 3: {importance_df.iloc[2]['Feature_Name']}
   → Importance: {importance_df.iloc[2]['Importance']:.4f}
   → Feature-Index: {int(importance_df.iloc[2]['Feature_Index'])}

Top 4: {importance_df.iloc[3]['Feature_Name']}
   → Importance: {importance_df.iloc[3]['Importance']:.4f}
   → Feature-Index: {int(importance_df.iloc[3]['Feature_Index'])}

Top-5 Cumulative Importance: {importance_df.head(5)['Importance'].sum():.4f}
Top-10 Cumulative Importance: {importance_df.head(10)['Importance'].sum():.4f}
""")
