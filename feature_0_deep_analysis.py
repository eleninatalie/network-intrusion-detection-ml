#!/usr/bin/env python3
"""
TIEFANALYSE: Was ist Feature 0 wirklich?
Warum ist Feature 0 > 1.0366 IMMER NORMAL?
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

print("=" * 80)
print("FEATURE 0 TIEFANALYSE: DIE GEHEIMNISVOLLE PERFEKTE TRENNUNG")
print("=" * 80)

# Lade Daten
train_data = pd.read_csv("UNSW_NB15_train_LEAKAGE_REMOVED.csv")
original_data = pd.read_csv("UNSW_NB15_training-set.csv")

print(f"\nDF Formen:")
print(f"  Clean (LEAKAGE_REMOVED): {train_data.shape}")
print(f"  Original: {original_data.shape}")

# Was ist Feature 0 wirklich?
feature_0_clean = train_data['0']  # Numerischer Index
is_attack = train_data['is_attack']
feature_0_original = original_data.iloc[:train_data.shape[0], 0]

print(f"\n" + "=" * 80)
print("FEATURE 0 STATISTIK (im CLEAN Dataset)")
print("=" * 80)

print(f"\n📊 Allgemeine Statistik:")
print(f"  Min: {feature_0_clean.min():.6f}")
print(f"  Max: {feature_0_clean.max():.6f}")
print(f"  Mean: {feature_0_clean.mean():.6f}")
print(f"  Std: {feature_0_clean.std():.6f}")

print(f"\n📊 Nach Klasse (CLEAN):")
normal_data = feature_0_clean[is_attack == 0]
attack_data = feature_0_clean[is_attack == 1]

print(f"\n  NORMAL (n={len(normal_data)}):")
print(f"    Min: {normal_data.min():.6f}")
print(f"    Max: {normal_data.max():.6f}")
print(f"    Mean: {normal_data.mean():.6f}")
print(f"    Std: {normal_data.std():.6f}")

print(f"\n  ATTACK (n={len(attack_data)}):")
print(f"    Min: {attack_data.min():.6f}")
print(f"    Max: {attack_data.max():.6f}")
print(f"    Mean: {attack_data.mean():.6f}")
print(f"    Std: {attack_data.std():.6f}")

# Der magic threshold
magic_threshold = 1.0366
print(f"\n" + "=" * 80)
print(f"🎯 DER MAGIC THRESHOLD: {magic_threshold}")
print("=" * 80)

above_threshold = feature_0_clean > magic_threshold
below_threshold = feature_0_clean <= magic_threshold

print(f"\n✂️ Split Results:")
above_attack_count = (is_attack[above_threshold] == 1).sum()
above_normal_count = (is_attack[above_threshold] == 0).sum()
below_attack_count = (is_attack[below_threshold] == 1).sum()
below_normal_count = (is_attack[below_threshold] == 0).sum()

print(f"\n  Above threshold ({magic_threshold}):")
print(f"    Normal: {above_normal_count}")
print(f"    Attack: {above_attack_count}  ← {above_attack_count/above_normal_count*100 if above_normal_count > 0 else 0:.1%} Attack rate")

print(f"\n  Below or equal threshold ({magic_threshold}):")
print(f"    Normal: {below_normal_count}")
print(f"    Attack: {below_attack_count}  ← {below_attack_count/(below_normal_count+below_attack_count)*100:.1%} Attack rate")

# Was ist der Name dieses Features in den Original-Daten?
print(f"\n" + "=" * 80)
print("🔍 FEATURE-IDENTIFIKATION")
print("=" * 80)

print(f"\nUrsprüngliche Spalten im UNSW_NB15_training-set.csv:")
for i in range(min(10, len(original_data.columns))):
    print(f"  Column {i}: {original_data.columns[i]}")

# Es ist wahrscheinlich 'dur' - Connection Duration
# Was sind typische Connection Durations für Normal vs Attack?

print(f"\n" + "=" * 80)
print("📈 DISTRIBUTION ANALYSE")
print("=" * 80)

# Quantile
print(f"\nQuantile des NORMAL Datensatzes (Feature 0):")
for q in [0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0]:
    val = normal_data.quantile(q)
    print(f"  {q*100:3.0f}%: {val:10.6f}")

print(f"\nQuantile des ATTACK Datensatzes (Feature 0):")
for q in [0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0]:
    val = attack_data.quantile(q)
    print(f"  {q*100:3.0f}%: {val:10.6f}")

# Ist das Feature standardisiert/normalisiert?
print(f"\n" + "=" * 80)
print("🔬 IS FEATURE 0 STANDARDIZED/NORMALIZED?")
print("=" * 80)

# Prüfe ob es standardisiert ist (mean≈0, std≈1)
if abs(feature_0_clean.mean()) < 0.1 and abs(feature_0_clean.std() - 1.0) < 0.1:
    print("\n✅ JA - Feature 0 ist standardisiert (z-Score)!")
    print(f"   Mean: {feature_0_clean.mean():.6f} (sollte ≈ 0)")
    print(f"   Std: {feature_0_clean.std():.6f} (sollte ≈ 1)")
    
    # Wenn standardisiert, was sind die Original-Werte?
    mean_original = original_data.iloc[:train_data.shape[0], 0].mean()
    std_original = original_data.iloc[:train_data.shape[0], 0].std()
    
    print(f"\n   Vermutene Original-Werte:")
    print(f"     Mean: {mean_original:.6f}")
    print(f"     Std: {std_original:.6f}")
    
    # Berechne den Original-Threshold
    original_threshold = magic_threshold * std_original + mean_original
    print(f"\n   Original Threshold (denormalisiert):")
    print(f"     {magic_threshold:.4f} * {std_original:.4f} + {mean_original:.4f} = {original_threshold:.4f}")

# Hauptfrage: Warum ist Feature 0 > 1.0366 IMMER normal?
print(f"\n" + "=" * 80)
print("❓ WARUM FEATURE 0 > {magic_threshold} IMMER NORMAL?")
print("=" * 80)

print(f"""
HYPOTHESEN:

1. 🎯 ECHTE PATTERN HYPOTHESE:
   - Features > {magic_threshold} entspricht KURZEN connections
   - Attacks haben typischerweise LÄNGERE connections (mehr Datenfluss)
   - Das wäre LEGITIM!

2. ⚠️ LEAKAGE-HYPOTHESE:
   - Feature 0 könnte indirekt aus attack_cat ABGELEITET sein
   - Oder Feature 0 ist nicht wirklich "Connection Duration"
   - Besonderheit: Wurde "LEAKAGE_REMOVED" wirklich richtig entfernt?

3. 🤔 NORMALISIERUNGS-HYPOTHESE:
   - Die Normalisierung führte zu unerwarteten Splits
   - Aber: Normalisierung sollte nur Skalierung sein, nicht die Separabilität ändern

NÄCHSTER SCHRITT: Prüfe Feature 0 gegen Original-Daten
""")

# Vergleiche mit Original-Daten
print(f"\n" + "=" * 80)
print("🔗 VERGLEICH MIT ORIGINAL-DATEN")
print("=" * 80)

# Die ersten 100 Zeilen prüfen
original_f0 = original_data.iloc[:min(100, len(train_data)), 0].values
clean_f0 = train_data['0'].iloc[:min(100, len(train_data))].values

# Rekonstruiere Original-Wert
if abs(feature_0_clean.mean()) < 0.1:  # Ist standardisiert
    reconstructed = clean_f0 * std_original + mean_original
    correlation = np.corrcoef(original_f0, reconstructed)[0, 1]
    print(f"\nKorrelation Original vs Rekonstruiert: {correlation:.6f}")
    
    if correlation > 0.99:
        print("✅ Feature 0 ist standardisierte Version des Original-Features")

# Fazit
print(f"\n" + "=" * 80)
print("📋 FAZIT ZUR FEATURE 0 ANALYSE")
print("=" * 80)

print(f"""
BEOBACHTUNGEN:
1. Feature 0 (vermutlich 'dur' - Connection Duration) trennt perfekt:
   - Werte > {magic_threshold} = IMMER NORMAL
   - Werte <= {magic_threshold} = NORMAL oder ATTACK
   
2. Das ist sehr verdächtig! Aber:
   - Könnte legitime Netzwerk-Charakteristik sein
   - Attacks könnten systematisch längere/kürzere Verbindungen haben
   
3. Feature ist standardisiert (z-Score normalisiert)
   
4. KRITISCH: Wurde der LEAKAGE-Removal richtig durchgeführt?
   - Falls attack_cat correlated mit connection duration war
   - Und wir nur attack_cat entfernt haben...
   - ... könnte Feature 0 noch die Information "kodiert" haben!

EMPFEHLUNG:
→ Prüfe, ob Feature 0 mit dem Original attack_cat korreliert war
→ Prüfe Original-Daten um sicherzustellen dass perfekte Trennung nicht künstlich ist
""")
