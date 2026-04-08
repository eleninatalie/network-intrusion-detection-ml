#!/usr/bin/env python3
"""
CONCLUSIVER TEST: Trainiere Decision Tree auf ORIGINAL Daten  
und vergleiche mit CLEAN Daten Ergebnissen
"""

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

print("=" * 80)
print("CONCLUSIVER LEAKAGE TEST: ORIGINAL vs. CLEAN")
print("=" * 80)

# ========== ORIGINAL DATEN ==========
print("\n" + "=" * 80)
print("TEST 1: DECISION TREE AUF ORIGINAL DATEN")
print("=" * 80)

original_train = pd.read_csv("UNSW_NB15_training-set.csv")
original_test = pd.read_csv("UNSW_NB15_test.csv")

# Bereinige Original Daten
# Entferne: attack_cat (leakage), label (nicht brauchbar), id (irrelevant)
cols_to_remove = ['id', 'attack_cat', 'label']

X_train_orig = original_train.drop(cols_to_remove, axis=1)
y_train_orig = original_train['label']  # 0 = Normal, 1 = Attack

X_test_orig = original_test.drop(cols_to_remove, axis=1)
y_test_orig = original_test['label']

print(f"\nOriginal Train: {X_train_orig.shape}")
print(f"Original Test:  {X_test_orig.shape}")

# One-Hot Encode kategorische Features
categorical_cols = X_train_orig.select_dtypes(include=['object']).columns.tolist()
print(f"\nKategorische Spalten zum One-Hot Encode: {categorical_cols}")

X_train_orig_encoded = pd.get_dummies(X_train_orig, columns=categorical_cols, drop_first=False)
X_test_orig_encoded = pd.get_dummies(X_test_orig, columns=categorical_cols, drop_first=False)

print(f"Nach One-Hot Encoding:")
print(f"  Train Shape: {X_train_orig_encoded.shape}")
print(f"  Test Shape:  {X_test_orig_encoded.shape}")

# Stelle sicher dass Train und Test gleich viele Spalten haben
common_cols = X_train_orig_encoded.columns.intersection(X_test_orig_encoded.columns)
X_train_orig_encoded = X_train_orig_encoded[common_cols]
X_test_orig_encoded = X_test_orig_encoded[common_cols]

print(f"Nach alignment:")
print(f"  Train Shape: {X_train_orig_encoded.shape}")
print(f"  Test Shape:  {X_test_orig_encoded.shape}")

# Standardisiere
scaler = StandardScaler()
X_train_orig_scaled = scaler.fit_transform(X_train_orig_encoded)
X_test_orig_scaled = scaler.transform(X_test_orig_encoded)

print(f"\nGrößen nach Standardisierung:")
print(f"  Train: {X_train_orig_scaled.shape}")
print(f"  Test:  {X_test_orig_scaled.shape}")

# Trainiere Decision Tree auf ORIGINAL Daten
print(f"\n🔄 Trainiere Decision Tree auf ORIGINAL Daten...")

dt_orig = DecisionTreeClassifier(
    criterion='entropy',
    max_depth=5,
    min_samples_leaf=1,
    min_samples_split=2,
    random_state=42
)

dt_orig.fit(X_train_orig_scaled, y_train_orig)

# Evaluiere
train_pred = dt_orig.predict(X_train_orig_scaled)
test_pred = dt_orig.predict(X_test_orig_scaled)

train_acc = accuracy_score(y_train_orig, train_pred)
test_acc = accuracy_score(y_test_orig, test_pred)

print(f"\n✅ RESULTS - Original Daten:")
print(f"  Training Accuracy: {train_acc:.4f} ({train_acc*100:.1f}%)")
print(f"  Test Accuracy:     {test_acc:.4f} ({test_acc*100:.1f}%)")

# ========== CLEAN DATEN ==========
print(f"\n" + "=" * 80)
print("TEST 2: DECISION TREE AUF CLEAN DATEN")
print("=" * 80)

clean_train = pd.read_csv("UNSW_NB15_train_LEAKAGE_REMOVED.csv")
clean_test = pd.read_csv("UNSW_NB15_test_LEAKAGE_REMOVED.csv")

X_train_clean = clean_train.drop('is_attack', axis=1)
y_train_clean = clean_train['is_attack']

X_test_clean = clean_test.drop('is_attack', axis=1)
y_test_clean = clean_test['is_attack']

print(f"\nClean Train: {X_train_clean.shape}")
print(f"Clean Test:  {X_test_clean.shape}")

# Trainiere Decision Tree auf CLEAN Daten
print(f"\n🔄 Trainiere Decision Tree auf CLEAN Daten...")

dt_clean = DecisionTreeClassifier(
    criterion='entropy',
    max_depth=5,
    min_samples_leaf=1,
    min_samples_split=2,
    random_state=42
)

dt_clean.fit(X_train_clean, y_train_clean)

# Evaluiere
train_pred_clean = dt_clean.predict(X_train_clean)
test_pred_clean = dt_clean.predict(X_test_clean)

train_acc_clean = accuracy_score(y_train_clean, train_pred_clean)
test_acc_clean = accuracy_score(y_test_clean, test_pred_clean)

print(f"\n✅ RESULTS - Clean Daten:")
print(f"  Training Accuracy: {train_acc_clean:.4f} ({train_acc_clean*100:.1f}%)")
print(f"  Test Accuracy:     {test_acc_clean:.4f} ({test_acc_clean*100:.1f}%)")

# ========== VERGLEICH ==========
print(f"\n" + "=" * 80)
print("VERGLEICH: ORIGINAL vs. CLEAN")
print("=" * 80)

print(f"""
┌─────────────────────────────────┬──────────────┬──────────────┐
│ Metrik                          │ Original     │ Clean        │
├─────────────────────────────────┼──────────────┼──────────────┤
│ Train Accuracy                  │ {train_acc:>7.2%}         │ {train_acc_clean:>7.2%}         │
│ Test Accuracy                   │ {test_acc:>7.2%}         │ {test_acc_clean:>7.2%}         │
├─────────────────────────────────┼──────────────┼──────────────┤
│ Overfitting (Train - Test)      │ {train_acc - test_acc:>7.2%}         │ {train_acc_clean - test_acc_clean:>7.2%}         │
└─────────────────────────────────┴──────────────┴──────────────┘
""")

# ANALYSE
print("\n" + "=" * 80)
print("🔍 LEAKAGE ANALYSE")
print("=" * 80)

print(f"""
BEFUNDE:

1. ORIGINAL DATEN (mit attack_cat entfernt, aber ONE-HOT encoded):
   - Train Accuracy: {train_acc*100:.1f}%
   - Test Accuracy:  {test_acc*100:.1f}%
   
2. CLEAN DATEN (Full Leakage Removed + Feature Engineered):
   - Train Accuracy: {train_acc_clean*100:.1f}%
   - Test Accuracy:  {test_acc_clean*100:.1f}%

INTERPRETATION:
""")

if abs(test_acc - test_acc_clean) > 0.1:
    print(f"""   ⚠️  UNTERSCHIED VON {abs(test_acc - test_acc_clean)*100:.1f}% - VERDÄCHTIG!
   
   Das deutet darauf hin dass:
   a) CLEAN Daten zusätzliche Information enthalten (Feature Engineering)
   b) Diese Features könnten indirekt attack_cat Information kodieren
   c) Leakage könnte in den engineerten Features vorhanden sein
""")
else:
    print(f"""   ✅ ÄHNLICHE PERFORMANCE ({abs(test_acc - test_acc_clean)*100:.1f}% Unterschied)
   
   Das deutet darauf hin dass:
   a) CLEAN Daten legitim vorbereitet wurden
   b) Die höhere CLEAN-Performance könnte aus besserer Normalisierung kommen
""")

# Feature Importance
print(f"\n" + "=" * 80)
print("TOP FEATURES - ORIGINAL Daten")
print("=" * 80)

feature_importance_orig = dt_orig.feature_importances_
top_indices_orig = np.argsort(feature_importance_orig)[-5:][::-1]

print(f"\nTop 5 Features:")
for i, idx in enumerate(top_indices_orig, 1):
    feat_name = X_train_orig_encoded.columns[idx]
    importance = feature_importance_orig[idx]
    print(f"  {i}. Feature {idx} ({feat_name}): {importance:.4f}")

print(f"\n" + "=" * 80)
print("TOP FEATURES - CLEAN Daten")
print("=" * 80)

feature_importance_clean = dt_clean.feature_importances_
top_indices_clean = np.argsort(feature_importance_clean)[-5:][::-1]

print(f"\nTop 5 Features:")
for i, idx in enumerate(top_indices_clean, 1):
    feat_name = str(idx)
    importance = feature_importance_clean[idx]
    print(f"  {i}. Feature {feat_name}: {importance:.4f}")

# FINAL VERDICT
print(f"\n" + "=" * 80)
print("⚖️  FINAL VERDICT")
print("=" * 80)

if test_acc_clean > 0.95 and test_acc > 0.95:
    print(f"""
✅ CONCLUSION: Beide Datensätze zeigen hohe Accuracy!

Wahrscheinliche Erklärung:
→ UNSW-NB15 ist ein SEHR GUT STRUKTURIERTER Datensatz mit klarer Separierung
→ Die Hochdosen-Performance ist nicht Folge von offenkundiger Leakage
→ Allerdings: Die CLEAN-Daten zeigen NOCH HÖHERE Performance

Empfehlung:
→ Die Test-Accuracy von {test_acc_clean*100:.1f}% auf CLEAN ist höher als zu erwarten
→ Die engineerten Features könnten dennoch indirekte Leakage enthalten
→ ABER: Das ist nicht absolut nachgewiesen

ENTSCHEIDEND: Die{test_acc_clean*100:.1f}% auf Clean und {test_acc*100:.1f}% auf Original sind beide sehr hoch.
Das deutet auf ECHTE, legitime Separierbarkeit des Datensatzes hin, nicht auf Leakage!
""")
elif test_acc_clean > test_acc + 0.1:
    print(f"""
⚠️  WARNUNG: CLEAN-Daten zeigen SIGNIFIKANT höhere Performance!

   Clean Test Accuracy:    {test_acc_clean*100:.1f}%
   Original Test Accuracy: {test_acc*100:.1f}%
   Unterschied:            {(test_acc_clean - test_acc)*100:.1f}%

Das könnte bedeuten:
→ Feature Engineering in CLEAN-Daten kann indirekt attack_cat Information kodieren
→ Oder: Die LEAKAGE Removal war nicht vollständig
→ Oder: Die CLEAN-Daten sind aus einer ganz anderen Aufbereitung

EMPFEHLUNG: Untersuche die Feature Engineering Pipeline der CLEAN-Daten!
""")
else:
    print(f"""
✅ ÄHNLICHE PERFORMANCE zwischen Original und Clean

Das deutet darauf hin dass die CLEAN-Daten ordnungsgemäß vorbereitet wurden.
Die {test_acc_clean*100:.1f}% Accuracy scheint legitim zu sein!
""")
