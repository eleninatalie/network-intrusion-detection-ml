#!/usr/bin/env python3
"""
Analysiere die exakte Struktur der CLEAN Daten
Finde heraus welche Features One-Hot sind und was Feature 0 wirklich ist
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("CLEAN DATEN STRUKTUR ANALYSE")
print("=" * 80)

# Lade Clean Daten
clean_data = pd.read_csv("UNSW_NB15_train_LEAKAGE_REMOVED.csv")

# Schaue die numerischen Features an
numeric_cols = [c for c in clean_data.columns if c != 'is_attack' and c.isdigit()]
numeric_cols = sorted([int(c) for c in numeric_cols])

print(f"\nAnzahl numerischer Features: {len(numeric_cols)}")
print(f"Feature Indizes: {numeric_cols[:20]}...{numeric_cols[-5:]}")

# Analysiere die Wertbereiche
print(f"\n" + "=" * 80)
print("FEATURE-WERT ANALYSE")
print("=" * 80)

print(f"\nUnique Value Counts (indikiert whether One-Hot Encoded):")

one_hot_features = []
continuous_features = []

for i in numeric_cols[:30]:  # Überprüfe die ersten 30
    col_name = str(i)
    values = clean_data[col_name]
    unique_count = values.nunique()
    
    # One-Hot Features haben typischerweise nur 0 und 1 als Werte
    value_set = set(values.unique())
    is_one_hot = value_set == {0.0, 1.0} or value_set == {0, 1}
    
    dtype_info = f"dtype: {values.dtype}, unique: {unique_count}"
    
    if is_one_hot:
        one_hot_features.append(i)
        print(f"  Feature {i:3d}: ✓ ONE-HOT (nur 0 und 1)")
    else:
        continuous_features.append(i)
        print(f"  Feature {i:3d}: ✗ KONTINUIERLICH ({unique_count} values, {values.min():.2f} - {values.max():.2f})")

print(f"\n  ... weitere Features ...")

# Zweite Hälfte auch überprüfen
for i in numeric_cols[-20:]:
    col_name = str(i)
    values = clean_data[col_name]
    unique_count = values.nunique()
    
    value_set = set(values.unique())
    is_one_hot = value_set == {0.0, 1.0} or value_set == {0, 1}
    
    if is_one_hot:
        one_hot_features.append(i)
        print(f"  Feature {i:3d}: ✓ ONE-HOT (nur 0 und 1)")
    else:
        continuous_features.append(i)
        print(f"  Feature {i:3d}: ✗ KONTINUIERLICH ({unique_count} values, {values.min():.2f} - {values.max():.2f})")

# Statistik
print(f"\n" + "=" * 80)
print("STATISTIK")
print("=" * 80)

print(f"\nGefundene One-Hot Features: {len(set(one_hot_features))}")
print(f"Gefundene Kontinuierliche Features: {len(set(continuous_features))}")
print(f"Total analysiert: {len(numeric_cols)}")

# TYPISCHE One-Hot Muster
print(f"\n" + "=" * 80)
print("ONE-HOT ENCODING DETEKTIERUNG")
print("=" * 80)

# Grade alle Features auf One-Hot überprüfen
all_one_hot = []
all_continuous = []

for col_name in numeric_cols:
    col_str = str(col_name)
    values = clean_data[col_str]
    
    value_set = set(values.unique())
    is_one_hot = value_set == {0.0, 1.0} or value_set == {0, 1}
    
    if is_one_hot:
        all_one_hot.append(col_name)
    else:
        all_continuous.append(col_name)

print(f"\nEXAKTE ZÄHLUNG (alle {len(numeric_cols)} Features):")
print(f"  One-Hot Features:     {len(all_one_hot)}")
print(f"  Kontinuierliche Features: {len(all_continuous)}")

print(f"\nOne-Hot Feature Indizes: {all_one_hot}")
print(f"\nKontinuierliche Feature Indizes: {all_continuous}")

# Versuche zu rekonstruieren was diese Features sind
print(f"\n" + "=" * 80)
print("REKONSTRUKTION: WAS SIND DIESE FEATURES?")
print("=" * 80)

original_data = pd.read_csv("UNSW_NB15_training-set.csv")

# Vergleiche kontinuierliche Features mit Original
print(f"\nVergleich kontinuierliche Features mit Original:")
print(f"  Original hat: dur, spkts, dpkts, sbytes, dbytes, rate, sttl, dttl, sload, dload, etc.")
print(f"  Wir haben: {len(all_continuous)} kontinuierliche Features")

# Versuch zu mappen
if len(all_continuous) >= 10:
    print(f"\n  Die {len(all_continuous)} kontinuierliche Features könnten sein:")
    print(f"    1. Original numerische Features (dur, spkts, dpkts, sbytes, dbytes, etc.)")  
    print(f"    + 2. One-Hot Encoded kategorische Features ({len(all_one_hot)} Features)")

# Sammlungsstatistik
print(f"\n" + "=" * 80)
print("FEATURE KLASSIFIKATION")
print("=" * 80)

print(f"""
Hypothese: UNSW-NB15 wurde vorbearbeitet mit:

1. KONTINUIERLICHE FEATURES (Originale numerische):
   - {len(all_continuous)} Features (Indizes: {sorted(all_continuous)[:10]}...)
   - Sind standardisiert (z-Score)
   - Könnten sein: dur, spkts, dpkts, sbytes, dbytes, rate, sttl, dttl, sload, dload, etc.

2. ONE-HOT ENCODED KATEGORISCHE FEATURES:
   - {len(all_one_hot)} Features (Indizes: {sorted(all_one_hot)[:10]}...)
   - Nur 0 und 1 als Werte
   - Könnten stammen aus: proto (131 Kategorien), service (13), state (7), is_ftp_login, etc.

FRAGE: Wurde One-Hot Encoding VOR oder NACH dem Leakage Removal durchgeführt?

Wenn NACH Leakage Removal:
✅ SICHER - Keine Leakage durch One-Hot Features

Wenn VOR Leakage Removal:
⚠️  RISIKO - One-Hot Features könnten indirekt attack_cat Information enthalten
""")

# Prüfe ob die CLEAN Daten die Original-Daten sind, nur transformiert
print(f"\n" + "=" * 80)
print("VERIFIZIERUNG: SIND CLEAN DATEN TRANSFORMIERTE ORIGINAL?")
print("=" * 80)

# Untersuche ein kontinuierliches Feature
if len(all_continuous) > 0:
    test_feature = all_continuous[0]
    test_col = str(test_feature)
    
    clean_vals = clean_data[test_col].values
    
    # Sollte standardisiert sein
    print(f"\nFeature {test_feature} (erstes kontinuierliches Feature):")
    print(f"  Mean: {clean_vals.mean():.6f}")
    print(f"  Std: {clean_vals.std():.6f}")
    print(f"  Min: {clean_vals.min():.6f}")
    print(f"  Max: {clean_vals.max():.6f}")
    
    if abs(clean_vals.mean()) < 0.01 and 0.99 < clean_vals.std() < 1.01:
        print(f"  ✅ Ist standardisiert (z-Score)")
    
    # Print Quantile
    print(f"\n  Quantile:")
    for q in [0, 0.25, 0.5, 0.75, 1.0]:
        val = np.quantile(clean_vals, q)
        print(f"    {q*100:3.0f}%: {val:8.4f}")
