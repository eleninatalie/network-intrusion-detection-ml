#!/usr/bin/env python3
"""
Data Leakage Detection in Top Features
Analyse der Top-4 Features auf Leakage-Indikatoren
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, pearsonr, entropy

print("=" * 80)
print("DATA LEAKAGE DETECTION in TOP FEATURES")
print("=" * 80)

# Lade die LEAKAGE_REMOVED Daten
train_data = pd.read_csv("UNSW_NB15_train_LEAKAGE_REMOVED.csv")

# Feature-Namen Mapping
feature_names = {
    0: "dur (Connection Duration)",
    7: "dbytes (Destination Bytes)",
    12: "dload (Destination Data Load)",
    29: "response_body_len (Server Response Size)",
}

top_features_indices = [0, 7, 12, 29]

print("\n" + "=" * 80)
print("ANALYSE: Top-4 Features auf Leakage prüfen")
print("=" * 80)

# Überprüfe jedes Top-Feature
for idx in top_features_indices:
    feature_col = str(idx)
    feature_name = feature_names[idx]
    
    print(f"\n{'='*80}")
    print(f"Feature {idx}: {feature_name}")
    print(f"{'='*80}")
    
    # ------- 1. STATISTIKEN -------
    feature_data = train_data[feature_col]
    print(f"\n1️⃣ GRUNDSTATISTIKEN:")
    print(f"   Mean: {feature_data.mean():.6f}")
    print(f"   Std:  {feature_data.std():.6f}")
    print(f"   Min:  {feature_data.min():.6f}")
    print(f"   Max:  {feature_data.max():.6f}")
    print(f"   Unique Values: {feature_data.nunique()}")
    
    # ------- 2. CORRELATION MIT TARGET -------
    target = train_data['is_attack']
    pearson_corr, pearson_pval = pearsonr(feature_data, target)
    spearman_corr, spearman_pval = spearmanr(feature_data, target)
    
    print(f"\n2️⃣ CORRELATION MIT TARGET (is_attack):")
    print(f"   Pearson Correlation:  {pearson_corr:.6f} (p-value: {pearson_pval:.2e})")
    print(f"   Spearman Correlation: {spearman_corr:.6f} (p-value: {spearman_pval:.2e})")
    print(f"   ⚠️  Correlation > 0.8 würde auf Leakage hindeuten!")
    
    # ------- 3. SEPARATION ZWISCHEN NORMAL & ATTACK -------
    normal_values = feature_data[target == 0]
    attack_values = feature_data[target == 1]
    
    print(f"\n3️⃣ SEPARATION NORMAL vs ATTACK:")
    print(f"   Normal  - Mean: {normal_values.mean():.6f}, Std: {normal_values.std():.6f}")
    print(f"   Attack  - Mean: {attack_values.mean():.6f}, Std: {attack_values.std():.6f}")
    print(f"   Differenz (|Mean_Attack - Mean_Normal|): {abs(attack_values.mean() - normal_values.mean()):.6f}")
    
    # Prüfe auf Overlap
    normal_range = (normal_values.min(), normal_values.max())
    attack_range = (attack_values.min(), attack_values.max())
    
    overlap_min = max(normal_range[0], attack_range[0])
    overlap_max = min(normal_range[1], attack_range[1])
    
    if overlap_min <= overlap_max:
        overlap_pct = (overlap_max - overlap_min) / (max(normal_range[1], attack_range[1]) - min(normal_range[0], attack_range[0])) * 100
        print(f"   Overlap zwischen Ranges: JA ({overlap_pct:.1f}%)")
    else:
        print(f"   ⚠️  OVERLAP: NEIN! Ranges sind komplett getrennt!")
        print(f"       Normal Range:  [{normal_range[0]:.6f}, {normal_range[1]:.6f}]")
        print(f"       Attack Range:  [{attack_range[0]:.6f}, {attack_range[1]:.6f}]")
        print(f"       → VERDACHT auf LEAKAGE!")
    
    # ------- 4. VERTEILUNG ANALYSE -------
    print(f"\n4️⃣ VERTEILUNGS-ANALYSE:")
    print(f"   Normal  - Quartile: Q1={normal_values.quantile(0.25):.4f}, Median={normal_values.quantile(0.5):.4f}, Q3={normal_values.quantile(0.75):.4f}")
    print(f"   Attack  - Quartile: Q1={attack_values.quantile(0.25):.4f}, Median={attack_values.quantile(0.5):.4f}, Q3={attack_values.quantile(0.75):.4f}")
    
    # Berechne wie viel % der Values bereits den Attack vorhersagen
    if attack_values.min() > normal_values.max():
        pct_perfect = 100
        print(f"   ⚠️  CRITICAL: ALL Attack-values > ALL Normal-values!")
        print(f"       → Feature könnte ALLEIN 100% Accuracy geben!")
    elif attack_values.max() < normal_values.min():
        pct_perfect = 100
        print(f"   ⚠️  CRITICAL: ALL Attack-values < ALL Normal-values!")
        print(f"       → Feature könnte ALLEIN 100% Accuracy geben!")
    else:
        # Berechne misclassification wenn man nur dieses Feature verwendet
        threshold = (normal_values.max() + attack_values.min()) / 2
        correct = ((feature_data <= threshold) & (target == 0)).sum() + ((feature_data > threshold) & (target == 1)).sum()
        accuracy_single_feature = correct / len(feature_data) * 100
        print(f"   Single-Feature Accuracy (mit optimalem Threshold): {accuracy_single_feature:.2f}%")
        if accuracy_single_feature > 95:
            print(f"   ⚠️  WARNING: Dieses Feature ALLEIN liefert {accuracy_single_feature:.1f}% Accuracy!")
            print(f"       → Könnte verstecktes Leakage sein!")

# ===== GLOBALE LEAKAGE-CHECK =====
print("\n\n" + "=" * 80)
print("GLOBALE LEAKAGE-DETEKTIONS-TESTS")
print("=" * 80)

# Test 1: Gibt es Features mit perfekter Separation?
print("\n🔍 Test 1: Perfekte Separation?")

perfect_features = []
for col in train_data.columns:
    if col == 'is_attack':
        continue
    
    feature_data = train_data[col]
    target = train_data['is_attack']
    
    normal_vals = feature_data[target == 0]
    attack_vals = feature_data[target == 1]
    
    # Prüfe auf Nicht-Überlapps
    if (normal_vals.max() < attack_vals.min()) or (attack_vals.max() < normal_vals.min()):
        perfect_features.append(col)
        print(f"   ⚠️  Feature {col} hat PERFEKTE SEPARATION!")

if not perfect_features:
    print(f"   ✅ Keine Features mit perfekter Separation gefunden")

# Test 2: Maximale Correlation mit Target
print("\n🔍 Test 2: Maximum Correlation mit Target?")
max_corr = 0
max_corr_feature = None

for col in train_data.columns:
    if col == 'is_attack':
        continue
    
    corr = abs(train_data[col].corr(train_data['is_attack']))
    if corr > max_corr:
        max_corr = corr
        max_corr_feature = col

print(f"   Maximum Absolute Correlation: {max_corr:.6f} (Feature {max_corr_feature})")
if max_corr > 0.8:
    print(f"   ⚠️  WARNING: Very High Correlation detected!")
    print(f"       Feature {max_corr_feature} could be causing 100% accuracy!")
else:
    print(f"   ✅ Correlations are reasonable (< 0.8)")

# Test 3: Logistische Regression nur mit Top-4 Features
print("\n🔍 Test 3: Accuracy mit nur Top-4 Features?")
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

X_top4 = train_data[['0', '7', '12', '29']].values
y = train_data['is_attack'].values

scaler = StandardScaler()
X_top4_scaled = scaler.fit_transform(X_top4)

lr = LogisticRegression(random_state=42, max_iter=1000)
lr.fit(X_top4_scaled, y)
lr_accuracy = lr.score(X_top4_scaled, y)

print(f"   Logistic Regression mit Top-4 Features: {lr_accuracy:.4f} ({lr_accuracy*100:.2f}%)")
if lr_accuracy > 0.95:
    print(f"   ⚠️  High accuracy with only 4 features!")
    print(f"       → Dataset might be artificially separable")

# ===== ZUSAMMENFASSUNG =====
print("\n\n" + "=" * 80)
print("🎯 ZUSAMMENFASSUNG - LEAKAGE-VERDACHT")
print("=" * 80)

leakage_score = 0

# Scoring
if max_corr > 0.8:
    print(f"\n❌ HIGH CORRELATION DETECTED: {max_corr:.4f}")
    print(f"   → Feature {max_corr_feature} might be leaking target information")
    leakage_score += 3

if perfect_features:
    print(f"\n❌ PERFECT SEPARATION DETECTED")
    print(f"   Features with non-overlapping ranges: {perfect_features}")
    leakage_score += 3
    
if lr_accuracy > 0.95:
    print(f"\n⚠️  TOP-4 FEATURES ALONE: {lr_accuracy*100:.1f}% Accuracy")
    print(f"   → Dataset is extremely separable with only 4 features")
    leakage_score += 2

if leakage_score == 0:
    print(f"\n✅ NO MAJOR LEAKAGE INDICATORS FOUND")
    print(f"   → 100% Accuracy appears to be from genuine data separability")
    print(f"   → UNSW-NB15 dataset is inherently very well-separated")
    print(f"   → Decision Tree can solve it with just Duration + Bytes")
else:
    print(f"\n⚠️  LEAKAGE SUSPICION LEVEL: {leakage_score}/6")
