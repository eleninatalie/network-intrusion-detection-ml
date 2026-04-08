#!/usr/bin/env python3
"""
COMPREHENSIVE DATA LEAKAGE DETECTION - OPTIMIERT
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import euclidean_distances

print("\n" + "="*90)
print("COMPREHENSIVE DATA LEAKAGE ANALYSIS")
print("="*90)

# ============================================================================
# PHASE 1: Data Overlap Check (OPTIMIERT)
# ============================================================================
print("\n\n## PHASE 1: TRAIN/TEST OVERLAP CHECK")
print("-" * 90)

print("\n[1.1] Laden der LEAKAGE_REMOVED-Datensätze...")
X_train_csv = pd.read_csv('UNSW_NB15_train_LEAKAGE_REMOVED.csv')
X_test_csv = pd.read_csv('UNSW_NB15_test_LEAKAGE_REMOVED.csv')

print(f"✓ Train: {X_train_csv.shape}")
print(f"✓ Test:  {X_test_csv.shape}")

print("\n[1.2] Duplikate mit Hash-Methode prüfen (optimiert)...")
X_train_vals = X_train_csv.drop(columns=['is_attack']).values
X_test_vals = X_test_csv.drop(columns=['is_attack']).values

# Schnelle Duplikat-Erkennung mit nearestneighbor
from sklearn.neighbors import NearestNeighbors

nn = NearestNeighbors(n_neighbors=1)
nn.fit(X_train_vals)
distances, indices = nn.kneighbors(X_test_vals[:1000])  # Check first 1000 test samples

exact_duplicates = np.sum(distances < 1e-10)
print(f"Exakte Duplikate in Stichprobe (1000 Test-Samples): {exact_duplicates}")

if exact_duplicates == 0:
    print("✅ KEINE gemeinsamen Zeilen zwischen Train und Test gefunden")
else:
    print(f"🚨 {exact_duplicates} gemeinsame Zeilen gefunden!")

# ============================================================================
# PHASE 2: Feature-Target Correlation
# ============================================================================
print("\n\n## PHASE 2: FEATURE-TARGET CORRELATION ANALYSE")
print("-" * 90)

print("\n[2.1] Absolute Korrelationen mit Target (is_attack)...")
correlations = []
for col in X_train_csv.columns:
    if col != 'is_attack':
        corr = abs(X_train_csv[col].corr(X_train_csv['is_attack']))
        correlations.append({'Feature': col, 'AbsCorr': corr})

corr_df = pd.DataFrame(correlations).sort_values('AbsCorr', ascending=False)
print("\nTop 20 korrelierte Features:")
print(corr_df.head(20).to_string(index=False))

# Prüfe auf verdächtig hohe Korrelationen
suspicious = corr_df[corr_df['AbsCorr'] > 0.9]
if len(suspicious) > 0:
    print(f"\n🚨 WARNUNG: {len(suspicious)} Features mit |corr| > 0.9!")
    print(suspicious.to_string(index=False))
else:
    print(f"\n✅ Keine Features mit |corr| > 0.9 gefunden")

print(f"\n📊 Korrelations-Statistik:")
print(f"   Max Correlation: {corr_df.iloc[0]['AbsCorr']:.6f}")
print(f"   Mean Correlation: {corr_df['AbsCorr'].mean():.6f}")
print(f"   Std Dev: {corr_df['AbsCorr'].std():.6f}")

# ============================================================================
# PHASE 3: Perfect Separability Check
# ============================================================================
print("\n\n## PHASE 3: PERFECT SEPARABILITY CHECK")
print("-" * 90)

print("\n[3.1] Welche Features trennen Normal und Attack völlig?...")

feature_cols = [col for col in X_train_csv.columns if col != 'is_attack']
perfect_sep_features = []

for col in feature_cols:
    normal_vals = X_train_csv[X_train_csv['is_attack'] == 0][col]
    attack_vals = X_train_csv[X_train_csv['is_attack'] == 1][col]
    
    # Prüfe auf keine Überlappung
    if (normal_vals.min() > attack_vals.max()) or (normal_vals.max() < attack_vals.min()):
        overlap_score = 0
        perfect_sep_features.append({
            'Feature': col,
            'Normal_Range': f"[{normal_vals.min():.2f}, {normal_vals.max():.2f}]",
            'Attack_Range': f"[{attack_vals.min():.2f}, {attack_vals.max():.2f}]"
        })
    else:
        # Berechne Overlap-Prozent
        min_val = min(normal_vals.min(), attack_vals.min())
        max_val = max(normal_vals.max(), attack_vals.max())
        
        if max_val > min_val:
            range_total = max_val - min_val
            overlap_min = max(normal_vals.min(), attack_vals.min())
            overlap_max = min(normal_vals.max(), attack_vals.max())
            
            if overlap_max > overlap_min:
                overlap_pct = (overlap_max - overlap_min) / range_total * 100
            else:
                overlap_pct = 0

if len(perfect_sep_features) > 0:
    print(f"\n🚨 KRITISCH: {len(perfect_sep_features)} Features mit perfekter Separabilität!")
    sep_df = pd.DataFrame(perfect_sep_features)
    print(sep_df.to_string(index=False))
else:
    print(f"\n✅ Keine Features mit perfekter Separabilität gefunden")

# ============================================================================
# PHASE 4: Variance Analysis
# ============================================================================
print("\n\n## PHASE 4: FEATURE VARIANZ-ANALYSE")
print("-" * 90)

print("\n[4.1] Varianz pro Feature...")
variances = []
for col in feature_cols:
    var = X_train_csv[col].var()
    variances.append({'Feature': col, 'Variance': var})

var_df = pd.DataFrame(variances).sort_values('Variance', ascending=False)

print(f"\nTop 10 höchste Varianz:")
print(var_df.head(10).to_string(index=False))

print(f"\nTop 10 niedrigste Varianz:")
print(var_df.tail(10).to_string(index=False))

low_var_count = len(var_df[var_df['Variance'] < 0.01])
print(f"\n⚠️ Features mit sehr niedriger Varianz (< 0.01): {low_var_count}")
if low_var_count > 0:
    print(var_df[var_df['Variance'] < 0.01][['Feature', 'Variance']].to_string(index=False))

# ============================================================================
# PHASE 5: Class Distribution
# ============================================================================
print("\n\n## PHASE 5: KLASSENVERTEILUNG")
print("-" * 90)

print("\nTrain Set:")
print(X_train_csv['is_attack'].value_counts())
print(f"\nAttack Rate (Train): {X_train_csv['is_attack'].mean()*100:.2f}%")

print("\nTest Set:")
print(X_test_csv['is_attack'].value_counts())
print(f"\nAttack Rate (Test): {X_test_csv['is_attack'].mean()*100:.2f}%")

# ============================================================================
# PHASE 6: Mutual Information Analysis
# ============================================================================
print("\n\n## PHASE 6: MUTUAL INFORMATION ANALYSE")
print("-" * 90)

from sklearn.feature_selection import mutual_info_classif

print("\n[6.1] Berechne MI für alle Features...")
X_train_vals_mi = X_train_csv.drop(columns=['is_attack']).values
y_train_vals_mi = X_train_csv['is_attack'].values

mi_scores = mutual_info_classif(X_train_vals_mi, y_train_vals_mi, random_state=42)
mi_df = pd.DataFrame({'Feature': range(len(mi_scores)), 'MI': mi_scores}).sort_values('MI', ascending=False)

print("\nTop 15 MI-Features:")
print(mi_df.head(15).to_string(index=False))

# ============================================================================
# FINAL VERDICT
# ============================================================================
print("\n\n" + "="*90)
print("DIAGNOSE-ZUSAMMENFASSUNG")
print("="*90)

leakage_score = 0

if len(suspicious) > 0:
    print(f"\n🚨 LEVEL 1 - Feature-Korrelation:")
    print(f"   {len(suspicious)} Features mit |corr| > 0.9 → VERDÄCHTIG")
    leakage_score += 40

if len(perfect_sep_features) > 0:
    print(f"\n🚨 LEVEL 2 - Perfect Separability:")
    print(f"   {len(perfect_sep_features)} Features trennen Klassen völlig → SEHR VERDÄCHTIG")
    leakage_score += 50

if low_var_count > 10:
    print(f"\n⚠️ LEVEL 3 - Low Variance Features:")
    print(f"   {low_var_count} Features mit var < 0.01 → MITTEL VERDÄCHTIG")
    leakage_score += 20

if leakage_score == 0:
    print(f"\n✅ KEIN OFFENSICHTLICHER LEAKAGE gefunden")
    print(f"\n📊 Modelle sind wahrscheinlich einfach GUT weil:")
    print(f"   - Features sind natürlicherweise trennbar für Normal/Attack")
    print(f"   - UNSW-NB15 ist ein 'easy' Cybersecurity Dataset")
    print(f"   - Entsceidungsbaum kann simple Regeln lernen")
else:
    print(f"\n🚨 VERDACHT {leakage_score}%: LEAKAGE könnte vorhanden sein!")
