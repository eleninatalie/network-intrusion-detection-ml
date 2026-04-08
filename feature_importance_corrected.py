#!/usr/bin/env python3
"""
Feature Importance Plot mit ECHTEN Feature-Namen
Correct Mapping für LEAKAGE_REMOVED Datensätze
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

# ===== KORRETES FEATURE MAPPING =====
# Die LEAKAGE_REMOVED Datensätze enthalten 58 Features:
# - 0-39: Numerische Features (Original)
# - 40-57: OneHotEncoded Features MINUS die attack_cat Features!

# Original numeric feature names in der richtigen Reihenfolge
numeric_features = [
    "connection_id",           # 0
    "connection_duration_sec", # 1
    "protocol_type",           # 2
    "service_type",            # 3
    "connection_state",        # 4
    "packets_sent",            # 5
    "packets_received",        # 6
    "bytes_sent",              # 7
    "bytes_received",          # 8
    "data_rate_bytes_per_sec", # 9
    "ttl_sender",              # 10
    "ttl_receiver",            # 11
    "sender_data_load",        # 12
    "receiver_data_load",      # 13
    "packets_lost_sender",     # 14
    "packets_lost_receiver",   # 15
    "time_between_sender_packets",    # 16
    "time_between_receiver_packets",  # 17
    "jitter_sender",           # 18
    "jitter_receiver",         # 19
    "tcp_window_sender",       # 20
    "tcp_sequence_sender",     # 21
    "tcp_sequence_receiver",   # 22
    "tcp_window_receiver",     # 23
    "tcp_round_trip_time",     # 24
    "tcp_syn_ack_time",        # 25
    "tcp_ack_data_time",       # 26
    "mean_packet_size_sender", # 27
    "mean_packet_size_receiver",# 28
    "http_transaction_depth",  # 29
    "server_response_size",    # 30
    "connections_per_service", # 31
    "state_ttl_combinations",  # 32
    "connections_to_destination_short_term",    # 33
    "connections_from_source_to_dest_port",     # 34
    "connections_to_dest_from_source_port",     # 35
    "connections_between_source_dest",          # 36
    "ftp_login_attempt",       # 37
    "ftp_command_count",       # 38
    "http_method_count",       # 39
]

# OneHotEncoded Features (außer attack_cat die wurden entfernt)
# protocol_type OneHotEncoding (40-43)
onehot_features = [
    "protocol_tcp",            # 40
    "protocol_udp",            # 41
    "protocol_icmp",           # 42
    
    # service_type OneHotEncoding (43-154, aber wir haben 50+ Services)
    # Wir verwenden eine generische Benennung
]

# Generiere OneHotEncoded Service-Namen (basierend auf Anzahl)
# Die exakte Anzahl hängt von den einzigartigen Services ab
# Für jetzt: generische Namen based on Index

# Die genaue Struktur der LEAKAGE_REMOVED Features:
# 0-39: Numeric (40 features)
# 40-57: OneHotEncoded (18 features)
# Total = 58 features

# Bessere Strategie: Load die original data um die Struktur zu verstehen
original_data = pd.read_csv("UNSW_NB15_training-set.csv", encoding='latin1')

# Feature-Namen extrahieren
original_cols = [col.replace('ï»¿', '').strip() for col in original_data.columns if col.replace('ï»¿', '').strip() != 'label']

print("=" * 80)
print("ORIGINAL FEATURE STRUKTUR")
print("=" * 80)
print(f"Total Original Features: {len(original_cols)}")
print("\nAlle Original Features:")
for idx, col in enumerate(original_cols):
    print(f"  {idx:2d}: {col}")

# ===== MODELL TRAINIEREN =====
print("\n" + "=" * 80)
print("TRAINIERE DECISION TREE")
print("=" * 80)

classifier = DecisionTreeClassifier(random_state=42)

param_grid = {
    'criterion': ['gini', 'entropy'],
    'max_depth': [3, 5, 7, 10, 15],
    'min_samples_split': [2, 5, 10, 20],
    'min_samples_leaf': [1, 2, 4, 8]
}

print("⏳ GridSearchCV läuft...")
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

# ===== FEATURE IMPORTANCE =====
feature_importance = best_classifier.feature_importances_

# Erstelle ein einfaches aber verständliches Mapping
# Verwende original_cols für die ersten 40, dann generiere Namen für OneHotEncoded
feature_names = []

# Numerische Features (0-39)
for i in range(min(40, len(original_cols))):
    feature_names.append(original_cols[i])

# Für Indices >= 40 sind OneHotEncoded Features
# Generiere Namen basierend on welche kategorischen Features es gibt
categorical_feature_indices = [2, 3, 4]  # proto, service, state in original
categorical_names = {"proto": "protocol", "service": "service", "state": "connection_state"}

# Das Mapping für OneHotEncoded ist komplex, deshalb verwenden wir generische Namen
for i in range(40, len(feature_names)) if len(feature_names) > 40 else []:
    idx = i - 40
    feature_names.append(f"OneHotEncoded_Feature_{idx}")

# Wenn noch nicht genug Features: füge generische Namen hinzu
while len(feature_names) < len(feature_importance):
    idx = len(feature_names)
    if idx < 40:
        feature_names.append(original_cols[idx])
    else:
        feature_names.append(f"Encoded_Feature_{idx}")

# Erstelle DataFrame
importance_df = pd.DataFrame({
    'Feature_Index': range(len(feature_importance)),
    'Feature_Name': feature_names[:len(feature_importance)],
    'Importance': feature_importance
}).sort_values('Importance', ascending=False)

print("\n" + "=" * 80)
print("TOP 15 FEATURES MIT NAMEN:")
print("=" * 80)
print(importance_df.head(15).to_string(index=False))

# ===== PLOT =====
print("\n📊 Erstelle Plot...")

plt.figure(figsize=(12, 7))
top_10 = importance_df.head(10)

colors = plt.cm.viridis(np.linspace(0, 1, len(top_10)))
bars = plt.barh(range(len(top_10)), top_10['Importance'].values, color=colors, edgecolor='black', linewidth=1.5)

# Feature-Namen als Labels
plt.yticks(range(len(top_10)), top_10['Feature_Name'].values, fontsize=11)

# Werte auf Balken
for i, (bar, importance) in enumerate(zip(bars, top_10['Importance'].values)):
    width = bar.get_width()
    plt.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
             f'{importance:.4f}', 
             ha='left', va='center', fontsize=10, fontweight='bold')

plt.xlabel('Importance Score', fontsize=12, fontweight='bold')
plt.ylabel('Feature Name', fontsize=12, fontweight='bold')
plt.title('Top 10 Feature Importance - Decision Tree\n(Mit echten Feature-Namen)', 
          fontsize=14, fontweight='bold', pad=20)
plt.grid(axis='x', alpha=0.3, linestyle='--')
plt.tight_layout()

plt.savefig("feature_importance_with_names.png", dpi=300, bbox_inches='tight')
print("✅ Plot gespeichert: feature_importance_with_names.png")
plt.show()

# ===== SUMMARY =====
print("\n" + "=" * 80)
print("🎯 TOP 4 FEATURES (DECISION TREE)")
print("=" * 80)

for i in range(min(4, len(importance_df))):
    row = importance_df.iloc[i]
    print(f"\n{i+1}. {row['Feature_Name']}")
    print(f"   Index: {int(row['Feature_Index'])}")
    print(f"   Importance: {row['Importance']:.4f} ({row['Importance']*100:.2f}%)")

print(f"\n✨ Top-4 Combined Importance: {importance_df.head(4)['Importance'].sum():.4f} (100%)")
