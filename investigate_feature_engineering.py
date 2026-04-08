#!/usr/bin/env python3
"""
Kritische Untersuchung:
Warum hat UNSW_NB15_train_LEAKAGE_REMOVED 59 Features wenn Original 45 hat?
Wurden illegale Features engineered?
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("KRITISCHE UNTERSUCHUNG: FEATURE-ENGINEERING NACH LEAKAGE REMOVAL")
print("=" * 80)

# Lade Daten  
original_data = pd.read_csv("UNSW_NB15_training-set.csv")
clean_data = pd.read_csv("UNSW_NB15_train_LEAKAGE_REMOVED.csv")

print(f"\n📊 Datenformen:")
print(f"  Original:         {original_data.shape} Zeilen × {len(original_data.columns)} Spalten")
print(f"  LEAKAGE_REMOVED:  {clean_data.shape} Zeilen × {len(clean_data.columns)} Spalten")

print(f"\n⚠️  WARNUNG: Unterschiedliche Größe!")
print(f"   Original hat {len(original_data) - len(clean_data)} mehr Zeilen")
print(f"   Clean hat {len(clean_data.columns) - len(original_data.columns)} mehr Features!")

print(f"\n" + "=" * 80)
print("ORIGINAL SPALTEN")
print("=" * 80)

print("\nOriginal-Spalten:")
for i, col in enumerate(original_data.columns):
    print(f"  {i:2d}. {col}")

print(f"\n" + "=" * 80)
print("CLEAN SPALTEN")
print("=" * 80)

print(f"\nClean-Spalten (erste 20):")
clean_cols = list(clean_data.columns)
for i, col in enumerate(clean_cols[:20]):
    print(f"  {i:2d}. {col}")

print(f"\n... ({len(clean_cols) - 20} weitere Spalten)")
print(f"\nClean-Spalten (letzte 10):")
for i, col in enumerate(clean_cols[-10:], start=len(clean_cols)-10):
    print(f"  {i:2d}. {col}")

# Welche Features sind neu in Clean?
original_col_set = set(original_data.columns)
clean_col_set = set(clean_data.columns)

new_features = clean_col_set - original_col_set
removed_features = original_col_set - clean_col_set

print(f"\n" + "=" * 80)
print("FEATURE-VERGLEICH")
print("=" * 80)

print(f"\n❌ Entfernte Features ({len(removed_features)}):")
for feat in sorted(removed_features):
    print(f"  - {feat}")

print(f"\n✅ NEUE Features ({len(new_features)}):")
for feat in sorted(new_features):
    print(f"  + {feat}")

# Das ist sehr verdächtig!
print(f"\n" + "=" * 80)
print("ANALYSE: WO KOMMEN DIE NEUEN FEATURES HER?")
print("=" * 80)

# Überprüfe ob die neuen Features aus bekannten Features abgeleitet wurden
# Typische Feature Engineering: polynomial features, interactions, etc.

# Schaue nach der attack_cat Spalte
if 'attack_cat' in original_data.columns:
    print(f"\n⚠️  attack_cat EXISTIERT in Original-Daten!")
    if 'attack_cat' in clean_data.columns:
        print(f"    ❌ attack_cat EXISTIERT NOCH in CLEAN-Daten! (sollte entfernt sein)")
    else:
        print(f"    ✅ attack_cat wurde aus CLEAN entfernt")

# Schaue was konkret entfernt/hinzufügt wurde
print(f"\nDetaillierte Überprüfung:")

# 1. Wurden numerische Features zu "0", "1", etc. konvertiert?
original_numeric_count = original_data.select_dtypes(include=[np.number]).shape[1]
clean_numeric_count = clean_data.select_dtypes(include=[np.number]).shape[1]

print(f"\n  Numerische Features:")
print(f"    Original: {original_numeric_count}")
print(f"    Clean:    {clean_numeric_count}")

# 2. Schaue nach Spalte-Namen Pattern
print(f"\n  Pattern-Analyse der Feature-Namen (Clean):")
numeric_cols = [col for col in clean_data.columns if col.isdigit()]
print(f"    Numerische Spalten-Namen: {len(numeric_cols)} Spalten")
print(f"    Beispiele: {numeric_cols[:10]}")

# KRITISCHE FRAGE
print(f"\n" + "=" * 80)
print("🔴 KRITISCHE VERDACHT")
print("=" * 80)

print(f"""
BEFUND: Die Daten wurden VÖLLIG UNTERSCHIEDLICH VORBEREITET:

1. UNTERSCHIEDLICHE ZEILEN-COUNTS:
   - Original:  {len(original_data):6d} Zeilen
   - Clean:     {len(clean_data):6d} Zeilen
   - Differenz: -{len(original_data) - len(clean_data):6d} Zeilen (möglicherweise richtig entfernt)

2. UNTERSCHIEDLICHE SPALTEN-STRUKTUR:
   - Original:  {len(original_data.columns):2d} Spalten (benannte Features wie 'dur', 'proto', 'sbytes')
   - Clean:     {len(clean_data.columns):2d} Spalten (numerische Indizes '0', '1', '2'...)
   
3. SPALTEN IN CLEAN, DIE NICHT IN ORIGINAL SIND:
   {len(new_features):2d} neue Features wurden hinzugefügt!
   
4. SPALTEN IN ORIGINAL NICHT IN CLEAN:
   {len(removed_features):2d} Features wurden entfernt!

INTERPRETATION:
→ Die "LEAKAGE_REMOVED" Daten sind nicht einfach eine Bereinigung der Original-Daten
→ Sie wurden mit Encoding, Feature Engineering und/oder Transformation behandelt
→ Feature-Namen wurden numerisch kodiert (0, 1, 2, ...)
→ Es ist NICHT KLAR, ob das Feature Engineering VOR oder NACH der Separierung des Targets erfolgte

KRITISCHES RISIKO:
⚠️  Wenn Features nach Entfernung von attack_cat engineered wurden
⚠️  Könnten sie INDIREKT noch attack_cat Information enthalten!
""")

# Versuche zu rekonstruieren
print(f"\n" + "=" * 80)
print("VERIFIKATION: Sind die neuen Features legitim?")
print("=" * 80)

# Zahle die genauen neuen Features
print(f"\nNeu hinzugefügte Features (Sortierted):")
for i, feat in enumerate(sorted(new_features), 1):
    if i <= 15:  # Zeige erste 15
        print(f"  {i:2d}. {feat}")
    elif i == 16:
        print(f"  ...")

print(f"\nEntfernte Features:")
for feat in sorted(removed_features):
    print(f"  - {feat}")

# EMPFEHLUNG
print(f"\n" + "=" * 80)
print("⚠️  EMPFEHLUNG")
print("=" * 80)

print(f"""
1. VERIFIZIERUNG NOTWENDIG:
   → Wie wurden die LEAKAGE_REMOVED Daten genau verarbeitet?
   → Wurde Feature Engineering VOR oder NACH Leakage Removal gemacht?
   → Welche neuen Features wurden hinzugefügt und WARUM?

2. VERDACHT AUF INDIREKTE LEAKAGE:
   → Feature 0 hat perfekte Trennung (Feature > 1.0366 = immer Normal)
   → Das ist suspekt für ein einzelnes Feature
   → Wenn Feature 0 engineered wurde nach attack_cat-Entfernung
   → Könnte es indirekt attack_cat Information enthalten!

3. NÄCHSTER SCHRITT:
   → Analysiere die ORIGINALEN Daten OHNE Feature Engineering
   → Trainiere Decision Tree auf ORIGINAL + manuell bereinigt
   → Vergleiche Performance Original vs. LEAKAGE_REMOVED
""")
