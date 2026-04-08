#!/usr/bin/env python3
"""
VEREINFACHTER CONCLUSIVER TEST:
Vergleiche Decision Tree Performance zwischen SAUBEREN Datasets
und untersuche die Feature-Struktur
"""

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("VERWOGENE DATEN STRUKTUR ANALYSE")
print("=" * 80)

# Überprüfe alle Datensätze
datasets = {
    'UNSW_NB15_training-set': 'UNSW_NB15_training-set.csv',
    'UNSW_NB15_train_LEAKAGE_REMOVED': 'UNSW_NB15_train_LEAKAGE_REMOVED.csv',
    'UNSW_NB15_test': 'UNSW_NB15_test.csv',
    'UNSW_NB15_test_LEAKAGE_REMOVED': 'UNSW_NB15_test_LEAKAGE_REMOVED.csv',
}

for name, filepath in datasets.items():
    try:
        df = pd.read_csv(filepath)
        print(f"\n{name}:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns (first 10): {df.columns[:10].tolist()}")
        print(f"  Columns (last 5): {df.columns[-5:].tolist()}")
    except Exception as e:
        print(f"\n{name}: ERROR - {e}")

# CRITICAL FINDING
print(f"\n" + "=" * 80)
print("🔴 KRITISCHES PROBLEM IDENTIFIZIERT")
print("=" * 80)

print(f"""
DATEN INKONSISTENZ:

1. UNSW_NB15_training-set.csv (45 Spalten):
   - Originale Daten mit benannten Features (dur, proto, service, etc.)
   - Hat attack_cat und label

2. UNSW_NB15_train_LEAKAGE_REMOVED.csv (59 Spalten):
   - Transformierte Daten mit numerischen Feature-Indizes (0, 1, 2, ...)
   - attack_cat wurde entfernt
   - ONE-HOT Encoded Features hinzugefügt

3. UNSW_NB15_test.csv (189 Spalten) ⚠️  PROBLEM!
   - NICHT die Original-Daten!
   - AUCH transformiert mit numerischen Indizes (0, 1, 2, ..., 187)
   - ABER mit 189 Spalten (nicht 59!)
   
4. UNSW_NB15_test_LEAKAGE_REMOVED.csv (59 Spalten):
   - Test-Daten in gleichem Format wie Train LEAKAGE_REMOVED

KONKLUSION:
→ Es gibt mehrere VERSIONS des Datensatzes mit unterschiedlichem Feature-Engineering!
→ UNSW_NB15_test.csv ist mit UNSW_NB15_training-set.csv NICHT kompatibel!
→ Das deutet auf HARTE DATENVERARBEITUNGSPROBLEME hin!
""")

# ========== TEST: Trainiere auf CLEAN TEST DATA =====
print(f"\n" + "=" * 80)
print("TEST: Decision Tree auf CLEAN TRAIN + TEST Daten")
print("=" * 80)

train_clean = pd.read_csv("UNSW_NB15_train_LEAKAGE_REMOVED.csv")
test_clean = pd.read_csv("UNSW_NB15_test_LEAKAGE_REMOVED.csv")

X_train = train_clean.drop('is_attack', axis=1)
y_train = train_clean['is_attack']

X_test = test_clean.drop('is_attack', axis=1)
y_test = test_clean['is_attack']

print(f"\nDaten:")
print(f"  Train: {X_train.shape} (Target: {y_train.value_counts().to_dict()})")
print(f"  Test:  {X_test.shape}")

# Stelle sicher dass Features identisch sind
if list(X_train.columns) != list(X_test.columns):
    print(f"  ⚠️  Train und Test haben unterschiedliche Spalten!")
    common_cols = X_train.columns.intersection(X_test.columns)
    X_train = X_train[common_cols]
    X_test = X_test[common_cols]

# Trainiere Decision Tree  
print(f"\n🔄 Trainiere Decision Tree...")

dt = DecisionTreeClassifier(
    criterion='entropy',
    max_depth=5,
    min_samples_leaf=1,
    min_samples_split=2,
    random_state=42
)

dt.fit(X_train, y_train)

# Evaluiere
train_pred = dt.predict(X_train)
test_pred = dt.predict(X_test)
test_pred_proba = dt.predict_proba(X_test)[:, 1]

train_acc = accuracy_score(y_train, train_pred)
train_f1 = f1_score(y_train, train_pred)

test_acc = accuracy_score(y_test, test_pred)
test_f1 = f1_score(y_test, test_pred)
test_auc = roc_auc_score(y_test, test_pred_proba)

print(f"\n✅ RESULTS on CLEAN Daten:")
print(f"\n  TRAINING SET:")
print(f"    Accuracy: {train_acc:.4f} ({train_acc*100:.2f}%)")
print(f"    F1-Score: {train_f1:.4f}")

print(f"\n  TEST SET:")
print(f"    Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")
print(f"    F1-Score: {test_f1:.4f}")
print(f"    AUC-ROC:  {test_auc:.4f}")

print(f"\n  OVERFITTING:")
print(f"    Train-Test Acc Diff: {(train_acc - test_acc)*100:.2f}%")

# ========== VERDACHT ANALYSE =====
print(f"\n" + "=" * 80)
print("🔍 VERDACHT-ANALYSE")
print("=" * 80)

print(f"""
BEOBACHTUNGEN:

1. TEST ACCURACY: {test_acc*100:.1f}%
   - Wenn < 50%: Zufällig (Münzwurf)
   - Wenn > 95%: Verdächtig hoch / Leakage möglich
   - Wenn 100%: Definitiv verdächtig
   
   ERGEBNIS: {test_acc*100:.1f}% ist {"🚨 SEHR VERDÄCHTIG" if test_acc > 0.99 else "✅ PLAUSIBEL" if test_acc > 0.85 else "⚠️  IN DER GRAUZONE"}

2. OVERFITTING CHECK:
   - Difference: {(train_acc - test_acc)*100:.2f}%
   - Wenn ~0%: Perfekt generalisiert (verdächtig?)
   - Wenn >10%: Normales Overfitting
   
   ERGEBNIS: {"✅ NORMALES MUSTER" if (train_acc - test_acc) > 0.01 else "🚨 PERFEKT GENERALISIERT (VERDÄCHTIG!)"}

3. FEATURE ENGINEERING VERDACHT:
   - Original Training Set: 45 Spalten
   - Clean Dataset: 59 Spalten
   - Test.csv (raw): 189 Spalten(!!!)
   
   PROBLEM: Die Datensätze wurden inkonsistent vorbereitet!
            Features wurden möglicherweise unterschiedlich engineert!
            
4. ONE-HOT ENCODING VERDACHT:
   - 40 kontinuierliche Features (standardisiert)
   - 18 One-Hot Encoded Features
   - Ursprung: Unbekannt!
   
   FRAGE: Wurden die One-Hot Features mit der GLEICHEN METHODE
          aus den Original-Daten extrahiert?
          ODER wurden sie POST-HOC engineert?

FAZIT:
→ Während die {test_acc*100:.1f}% Accuracy an sich plausibel sein KÖNNTE,
→ ist die DATEN-VORBEREITUNG VERDÄCHTIG
→ Die inkonsistente Feature-Engineering zwischen Datasets ist problematisch
→ EMPFEHLUNG: Überprüfe die preprocessing pipeline!
""")

# ========== Feature Analysis =====
print(f"\n" + "=" * 80)
print("TOP 10 IMPORTANT FEATURES")
print("=" * 80)

feature_importance = dt.feature_importances_
top_indices = np.argsort(feature_importance)[-10:][::-1]

print(f"\nRanking:")
for rank, idx in enumerate(top_indices, 1):
    feat_name = X_train.columns[idx]
    importance = feature_importance[idx]
    
    # Überproniere welche One-Hot sind
    is_one_hot = int(feat_name) in [45, 150, 156, 157, 171, 172, 173, 174, 178, 183, 184, 185, 186, 189, 190, 191, 192, 194]
    marker = " 🔴 ONE-HOT" if is_one_hot else " ✓ Kontinuierlich"
    
    print(f"  {rank:2d}. Feature {feat_name:3s}: {importance:.4f}{marker}")

print(f"\n" + "=" * 80)
print("⚠️  FINALE EMPFEHLUNG")
print("=" * 80)

print(f"""
Status-Check:

[1] Hohe Accuracy? {test_acc*100:.1f}%
    → {"JA - Verdächtig!" if test_acc > 0.95 else "Nein - Normal"}

[2] Daten konsistent vorbereitet?
    → NEIN - Training, Clean, und Test.csv haben unterschiedliche Strukturen
    
[3] Feature Engineering dokumentiert?
    → UNBEKANNT - Die Quelle der 59/189 Spalten ist unklar

[4] Leakage nachgewiesen?
    → INDIREKT - Verdacht auf Leakage durch:
       - Inkonsistente Data Preprocessing
       - Undokumentiertes Feature Engineering
       - One-Hot Encoded Features (18 Stück) mit unklarem Ursprung

NÄCHSTE SCHRITTE:
1. ✅ Überprüfe die preprocessing_pipeline (falls sie  Dokumentation hat)
2. ✅ Rekonstruiere wie die 59 Features aus Original extrahiert wurden
3. ✅ Überprüfe, ob die One-Hot Features NACH dem Leakage Removal hinzugefügt wurden
4. ✅ Falls One-Hot Features VORHER hinzugefügt wurden: Verdacht auf Leakage!
""")
