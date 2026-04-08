#!/usr/bin/env python3
"""
Rekonstruiere die Feature-Namen aus den numerischen Indizes
Vergleiche mit Original-Features
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("FEATURE-NAME REKONSTRUKTION")
print("=" * 80)

# Lade Original
original_data = pd.read_csv("UNSW_NB15_training-set.csv")
clean_data = pd.read_csv("UNSW_NB15_train_LEAKAGE_REMOVED.csv")

# Mache ein Sample der beiden Dataframes um Patterns zu sehen
print("\n" + "=" * 80)
print("VERGLEICH: FEATURE 0 (CLEAN) vs. Original Features")
print("=" * 80)

# Lade auch die TEST-Daten um mehr Kontexte zu haben
test_clean = pd.read_csv("UNSW_NB15_test_LEAKAGE_REMOVED.csv")
test_original_raw = pd.read_csv("UNSW_NB15_test.csv")

print(f"\nClean Feature 0 (erste 20 Zeilen):")
print(clean_data['0'].head(20).values)

print(f"\nOriginal 'dur' Feature (erste 20 Zeilen):")
print(original_data['dur'].head(20).values)

# Versuche die Indizes zu mappen
print(f"\n" + "=" * 80)
print("VERSUCH: MAPPING CLEAN-INDIZES ZU ORIGINAL-FEATURES")
print("=" * 80)

# Methode 1: Versuche Correlations-Matching
print(f"\nMethode 1: Korrelations-Matching")
print(f"  Berechne Correlation zwischen Clean Feature 0 und allen Original Features...")

mapping = {}
clean_0 = clean_data['0'].astype(float)

for orig_col in original_data.columns[1:]:  # Überspringe 'id'
    if orig_col == 'attack_cat' or orig_col == 'label':  # Ignoriere diese
        continue
    
    try:
        orig_values = original_data[orig_col]
        # Versuche zu normalisieren/standardisieren für Vergleich
        if orig_values.dtype == 'object':
            print(f"    {orig_col}: ist kategorisch, überspringe")
            continue
        
        # Standardisiere beide
        orig_normalized = (orig_values - orig_values.mean()) / orig_values.std()
        clean_normalized = (clean_0 - clean_0.mean()) / clean_0.std()
        
        # Korrelation
        corr = np.corrcoef(orig_normalized.dropna()[:min(1000, len(orig_normalized))], 
                           clean_normalized[:min(1000, len(clean_normalized))])
        
        if corr.shape[0] > 1:
            corr_val = abs(corr[0, 1])
            if corr_val > 0.5:
                print(f"    {orig_col}: {corr_val:.4f} ← POTENTIELLER MATCH!")
                mapping[orig_col] = corr_val
    except Exception as e:
        pass

# Methode 2: Index-Position Mapping
print(f"\n\nMethode 2: Position-basiertes Mapping")
print(f"  Clean Feature 0 ist vielleicht Original Feature Index 0 oder 1 (nach 'id')?")

if len(original_data.columns) > 1:
    maybe_dur = original_data.iloc[:, 1]  # 2nd column after id
    print(f"    Original Column 1 ('dur') - Vergleich:")
    print(f"      Original 'dur' [0:5]: {maybe_dur.head().values}")
    print(f"      Clean '0' [0:5]: {clean_0.head().values}")

# Methode 3: Feature-Namen aus Git/Dokumentation
print(f"\n\nMethode 3: Bekannte Feature-Nummern-Mapping (aus UNSW-NB15 Docs)")
print(f"""
    UNSW-NB15 hat standardisiert 42 Features + 3 Labels:
    0  id
    1  dur (Feature 0 im Model!)
    2  proto
    3  service
    4  state
    5  spkts
    6  dpkts
    7  sbytes  
    8  dbytes  (Feature 7 im Model!)
    ...
    43 attack_cat
    44 label
    
    Das bedeutet:
    - Clean Feature '0' = Original 'dur' (Index 1)
    - Clean Feature '7' = Original 'sbytes' (Index 7) oder 'dbytes' (Index 8)?
""")

# Prüfe auf exakte Übereinstimmung
print(f"\n" + "=" * 80)
print("EXAKTE VERIFIZIERUNG")
print("=" * 80)

# Überprüfe ob Clean Feature 0 = Original dur ist
dur_original = original_data['dur'].values[:len(clean_data)]  # Gleiche Länge
feat0_clean = clean_data['0'].values

print(f"\nVergleich Clean '0' vs. Original 'dur':")
print(f"  Original 'dur' ist numerisch: {np.issubdtype(dur_original.dtype, np.number)}")
print(f"  Clean '0' ist numerisch: {np.issubdtype(feat0_clean.dtype, np.number)}")

# Normalisierung prüfen
dur_mean = dur_original.mean()
dur_std = dur_original.std()

print(f"\n  Original 'dur' Statistik:")
print(f"    Mean: {dur_mean:.2f}")
print(f"    Std: {dur_std:.2f}")
print(f"    Min: {dur_original.min():.2f}")
print(f"    Max: {dur_original.max():.2f}")

print(f"\n  Clean '0' Statistik:")
print(f"    Mean: {feat0_clean.mean():.6f}")
print(f"    Std: {feat0_clean.std():.6f}")
print(f"    Min: {feat0_clean.min():.6f}")
print(f"    Max: {feat0_clean.max():.6f}")

# Sind sie standardisiert?
if abs(feat0_clean.mean()) < 0.01 and abs(feat0_clean.std() - 1.0) < 0.01:
    print(f"\n  ✅ Clean '0' IST STANDARDISIERT")
    
    # Versuche zu denormalisieren
    denormalized = feat0_clean * dur_std + dur_mean
    
    print(f"\n  Denormalisiert würde Clean '0' sein:")
    print(f"    Mean: {denormalized.mean():.2f}")
    print(f"    Std: {denormalized.std():.2f}")
    print(f"    Min: {denormalized.min():.2f}")
    print(f"    Max: {denormalized.max():.2f}")
    
    # Vergleich
    correlation = np.corrcoef(dur_original, denormalized)[0, 1]
    print(f"\n  Korrelation Original 'dur' vs. Denormalisiert Clean '0': {correlation:.6f}")
    
    if correlation > 0.98:
        print(f"  ✅✅✅ MATCH! Clean '0' = Standardisiertes Original 'dur'!")

# ABER WAR DORT ONE-HOT ENCODING?
print(f"\n" + "=" * 80)
print("WARNUNG: WURDEN KATEGORISCHE FEATURES ONE-HOT ENCODED?")
print("=" * 80)

categorical_cols = original_data.select_dtypes(include=['object']).columns.tolist()
print(f"\nKategorische Spalten in Original:")
for col in categorical_cols:
    unique_count = original_data[col].nunique()
    print(f"  {col}: {unique_count} unique values")

print(f"""
⚠️  Wenn diese Spalten One-Hot Encoded wurden:
    - 'proto' mit N values → N binäre Features
    - 'service' mit M values → M binäre Features
    - 'state' mit L values → L binäre Features
    
    Das könnte das Lückenmuster in den Indizes erklären!
    (0, 1, 2, ... dann plötzlich 150, 156, 157 - das könnten separate One-Hot Groups sein!)

👉 KRITISCH: Wenn One-Hot Encoding VOR der Trennung der Attack-Information erfolgte
   Dann sind die engineerten Features vielleicht okay.
   
   ABER: Wenn One-Hot Encoding NACH Feature Selection durchgeführt wurde
   ODER: Wenn neue Features WÄHREND der Bereinigung hinzugefügt wurden
   DANN: Könnte indirekte Leakage vorhanden sein!
""")
