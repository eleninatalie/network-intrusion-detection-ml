#!/usr/bin/env python3
"""
CRITICAL: Welche 2 Features nutzt der Decision Tree?
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text

X_train_csv = pd.read_csv('UNSW_NB15_train_LEAKAGE_REMOVED.csv')
X_test_csv = pd.read_csv('UNSW_NB15_test_LEAKAGE_REMOVED.csv')

X_train = X_train_csv.drop(columns=['is_attack']).values
y_train = X_train_csv['is_attack'].values
X_test = X_test_csv.drop(columns=['is_attack']).values
y_test = X_test_csv['is_attack'].values

print("\n" + "="*90)
print("CRITICAL: WELCHE FEATURES NUTZT DER BAUM?")
print("="*90)

# Train Decision Tree
dt = DecisionTreeClassifier(max_depth=15, random_state=42, class_weight='balanced')
dt.fit(X_train, y_train)

print("\nFeature Importances (alle 58):")
fi = pd.DataFrame({
    'Feature_Index': range(len(dt.feature_importances_)),
    'Importance': dt.feature_importances_
}).sort_values('Importance', ascending=False)

print(fi.to_string(index=False))

print("\n\nTop Features:")
top_features = fi[fi['Importance'] > 0]['Feature_Index'].tolist()
print(f"Features mit Importance > 0: {top_features}")

# Exportiere den Baum
print("\n" + "="*90)
print("BAUM-STRUKTUR (Decision Rules):")
print("="*90)

tree_rules = export_text(dt, feature_names=[f"Feature_{i}" for i in range(X_train.shape[1])])
print(tree_rules)

# Teste: Funktioniert Klassifikation NUR mit 2 Features?
print("\n" + "="*90)
print("TEST: FUNKTIONIERT ES NUR MIT DEN TOP FEATURES?")
print("="*90)

for n_features in [1, 2, 3, 5, 10]:
    top_feat_idx = fi.head(n_features)['Feature_Index'].tolist()
    
    X_train_subset = X_train[:, top_feat_idx]
    X_test_subset = X_test[:, top_feat_idx]
    
    dt_subset = DecisionTreeClassifier(max_depth=15, random_state=42, class_weight='balanced')
    dt_subset.fit(X_train_subset, y_train)
    
    from sklearn.metrics import accuracy_score
    test_acc = accuracy_score(y_test, dt_subset.predict(X_test_subset))
    
    print(f"Mit Top {n_features} Features: Test Accuracy = {test_acc:.6f}")

# Untersuche dieFeatureshat genauer
print("\n" + "="*90)
print("DETAILED FEATURE ANALYSIS - TOP 2 FEATURES")
print("="*90)

top_2_features = fi.head(2)['Feature_Index'].tolist()
print(f"\nTop 2 Features: {top_2_features}")

for feat_idx in top_2_features:
    feat_name = f"Feature_{feat_idx}"
    X_feat = X_train[:, feat_idx]
    
    normal_vals = X_feat[y_train == 0]
    attack_vals = X_feat[y_train == 1]
    
    print(f"\n{feat_name}:")
    print(f"  Normal  - Mean: {normal_vals.mean():.4f}, Std: {normal_vals.std():.4f}, Range: [{normal_vals.min():.4f}, {normal_vals.max():.4f}]")
    print(f"  Attack  - Mean: {attack_vals.mean():.4f}, Std: {attack_vals.std():.4f}, Range: [{attack_vals.min():.4f}, {attack_vals.max():.4f}]")
    
    # Berechne Überlappung
    if (normal_vals.min() > attack_vals.max()) or (normal_vals.max() < attack_vals.min()):
        print(f"  ⚠️ KEINE ÜBERLAPPUNG - Features trennen perfekt!")
    else:
        union_min = min(normal_vals.min(), attack_vals.min())
        union_max = max(normal_vals.max(), attack_vals.max())
        overlap_min = max(normal_vals.min(), attack_vals.min())
        overlap_max = min(normal_vals.max(), attack_vals.max())
        
        if overlap_max > overlap_min:
            overlap_pct = (overlap_max - overlap_min) / (union_max - union_min) * 100
        else:
            overlap_pct = 0
            
        print(f"  Überlappung: {overlap_pct:.1f}%")

# Prüfe Feature-Namen/Ursprung
print("\n" + "="*90)
print("HERKUNFT DER TOP FEATURES")
print("="*90)

print("\nDie 2 super-wichtigen Features sind:")
print(f"  - Feature {top_2_features[0]}")
print(f"  - Feature {top_2_features[1]}")

print("\nHintergrund:")
print("  - Die LEAKAGE_REMOVED CSVs verwenden numerisch kodierte Features (0, 1, 2, ...)")
print("  - Die originalen Namen sind verloren gegangen (One-Hot Encoding)")
print("  - Feature Index können Original-Features oder One-Hot-Variablen sein")

# Test: Correlation der Top 2 mit Target
print("\n" + "="*90)
print("KORRELATION ZUR ZIELVARIABLE")
print("="*90)

for feat_idx in top_2_features:
    corr = abs(X_train_csv.iloc[:, feat_idx].corr(X_train_csv['is_attack']))
    print(f"Feature {feat_idx} - Korrelation mit is_attack: {corr:.6f}")
