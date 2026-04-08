# 🛠️ FIX-PLAN: Cybersecurity.ipynb - Implementierung der fehlenden Teile

## 📌 Übersicht der Fixes

| Phase | Was | Status | Zeilen (approx) |
|-------|-----|--------|-----------------|
| **Phase 1** | Feature Engineering (Encoding + Scaling) | ⚠️ TODO | +30 Zeilen |
| **Phase 2** | Modelle trainieren (Baseline + 3 spezialisierte) | ❌ TODO | +100 Zeilen |
| **Phase 3** | Evaluation & Metriken | ❌ TODO | +60 Zeilen |
| **Phase 4** | Feature Importance & Insights | ❌ TODO | +40 Zeilen |
| **Phase 5** | Abgabe-Vorbereitung | ❌ TODO | (externe Tools) |

---

## PHASE 1: Feature Engineering (Encoding + Scaling)

**Ziel:** Kategorische Features kodieren, numerische Features normalisieren

**Code für neue Notebook-Zelle nach aktueller Zelle 28:**

```python
# ===== PHASE 1: FEATURE ENGINEERING =====
# Ziel: Kategorische Variablen one-hot-kodieren, numerische skalieren

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Schritt 1a: Zielvariable separieren
target_col = 'is_attack'
X_train_prep = X_train.copy()
X_test_prep = X_test.copy()

# Schritt 1b: ID-Spalten entfernen (nicht für Training relevant)
id_cols = ['connection_id']
X_train_prep = X_train_prep.drop(columns=id_cols, errors='ignore')
X_test_prep = X_test_prep.drop(columns=id_cols, errors='ignore')

# Schritt 2: Kategoriale vs. numerische Spalten
cat_features = X_train_prep.select_dtypes(include=['object']).columns.tolist()
num_features = X_train_prep.select_dtypes(include=['number']).columns.tolist()

print(f"Kategoriale Features: {len(cat_features)} | {cat_features[:5]}...")
print(f"Numerische Features: {len(num_features)} | {num_features[:5]}...")

# Schritt 3: One-Hot Encoding + Scaling mit ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_features),
        ('cat', 'onehotencoder', cat_features)
    ]
)

# Schritt 4: Anwenden
X_train_transformed = preprocessor.fit_transform(X_train_prep)
X_test_transformed = preprocessor.transform(X_test_prep)

print(f"\n✅ Features transformiert:")
print(f"  Original: {X_train_prep.shape}")
print(f"  Nach Encoding: {X_train_transformed.shape}")

# Schritt 5: In DataFrame umwandeln (optional, für Kompatibilität)
feature_names = (
    num_features + 
    [f"{col}_{val}" for col in cat_features 
     for val in X_train_prep[col].unique()]
)
X_train_df = pd.DataFrame(X_train_transformed.toarray() if hasattr(X_train_transformed, 'toarray') 
                          else X_train_transformed, 
                          columns=num_features + cat_features[:1])  # Simplified

print(f"✅ Feature Engineering abgeschlossen!")
print(f"✅ X_train_transformed: {X_train_transformed.shape[0]} Samples, {X_train_transformed.shape[1]} Features")
```

---

## PHASE 2: Modelle trainieren

**Ziel:** 4 Modelle (1 Baseline, 3 spezialisiert) trainieren

### 2A: Baseline-Modell (Logistic Regression)

```python
# ===== PHASE 2: MODELLTRAINING =====
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
import time

# Dictionary für Modelle
models = {}
training_times = {}

# ========== MODELL 1: BASELINE (Logistic Regression) ==========
print("\n" + "="*60)
print("MODELL 1: BASELINE - Logistic Regression")
print("="*60)

start = time.time()
model_lr = LogisticRegression(
    max_iter=1000,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'  # Wichtig für Class Imbalance!
)
model_lr.fit(X_train_transformed, y_train)
training_times['Logistic Regression'] = time.time() - start

print(f"✅ Logistic Regression trainiert in {training_times['Logistic Regression']:.2f}s")
print(f"   Training Score: {model_lr.score(X_train_transformed, y_train):.4f}")
print(f"   Test Score: {model_lr.score(X_test_transformed, y_test):.4f}")

models['Logistic Regression'] = model_lr
```

### 2B: Random Forest

```python
# ========== MODELL 2: Random Forest ==========
print("\n" + "="*60)
print("MODELL 2: Random Forest (n_trees=100)")
print("="*60)

start = time.time()
model_rf = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced',
    max_depth=20
)
model_rf.fit(X_train_transformed if hasattr(X_train_transformed, 'toarray') else X_train_prep, y_train)
training_times['Random Forest'] = time.time() - start

print(f"✅ Random Forest trainiert in {training_times['Random Forest']:.2f}s")
print(f"   Training Score: {model_rf.score(X_train_prep, y_train):.4f}")
print(f"   Test Score: {model_rf.score(X_test_prep, y_test):.4f}")

models['Random Forest'] = model_rf
```

### 2C: Gradient Boosting

```python
# ========== MODELL 3: Gradient Boosting ==========
print("\n" + "="*60)
print("MODELL 3: Gradient Boosting")
print("="*60)

start = time.time()
model_gb = GradientBoostingClassifier(
    n_estimators=50,
    learning_rate=0.1,
    random_state=42,
    max_depth=5
)
model_gb.fit(X_train_transformed if hasattr(X_train_transformed, 'toarray') else X_train_prep, y_train)
training_times['Gradient Boosting'] = time.time() - start

print(f"✅ Gradient Boosting trainiert in {training_times['Gradient Boosting']:.2f}s")
print(f"   Training Score: {model_gb.score(X_train_prep, y_train):.4f}")
print(f"   Test Score: {model_gb.score(X_test_prep, y_test):.4f}")

models['Gradient Boosting'] = model_gb
```

---

## PHASE 3: Evaluation & Metriken

```python
# ===== PHASE 3: EVALUATION =====
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report, roc_curve, auc
)
import matplotlib.pyplot as plt

print("\n" + "="*80)
print("EVALUATIONS-METRIKEN")
print("="*80)

results = {}

for model_name, model in models.items():
    print(f"\n{'='*60}")
    print(f"Modell: {model_name}")
    print(f"{'='*60}")
    
    # Vorhersagen
    y_pred = model.predict(X_test_transformed if 'Logistic' in model_name else X_test_prep)
    y_pred_proba = model.predict_proba(X_test_transformed if 'Logistic' in model_name else X_test_prep)[:, 1]
    
    # Metriken
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_pred_proba)
    
    results[model_name] = {
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1-Score': f1,
        'ROC-AUC': roc
    }
    
    print(f"📊 Accuracy:  {acc:.4f}")
    print(f"📊 Precision: {prec:.4f}")
    print(f"📊 Recall:    {rec:.4f}")
    print(f"📊 F1-Score:  {f1:.4f}")
    print(f"📊 ROC-AUC:   {roc:.4f}")
    
    print(f"\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))

# Visualisierung der Metriken
results_df = pd.DataFrame(results).T
print("\n" + "="*80)
print("ZUSAMMENFASSUNG - ALLE MODELLE")
print("="*80)
display(results_df)

# Best Model bestimmen
best_model_name = results_df['ROC-AUC'].idxmax()
print(f"\n🏆 Bestes Modell (ROC-AUC): {best_model_name} mit {results_df.loc[best_model_name, 'ROC-AUC']:.4f}")
```

---

## PHASE 4: Feature Importance & Visualisierung

```python
# ===== PHASE 4: FEATURE IMPORTANCE =====
import matplotlib.pyplot as plt

print("\n" + "="*80)
print("FEATURE IMPORTANCE ANALYSE")
print("="*80)

# Nur für Tree-based Modelle
if hasattr(models['Random Forest'], 'feature_importances_'):
    importances = models['Random Forest'].feature_importances_
    feature_names_rf = num_features + cat_features
    
    # Top 20 Features
    top_indices = np.argsort(importances)[-20:][::-1]
    top_features = [feature_names_rf[i] for i in top_indices if i < len(feature_names_rf)]
    top_importances = importances[top_indices]
    
    plt.figure(figsize=(12, 8))
    plt.barh(range(len(top_features)), top_importances)
    plt.yticks(range(len(top_features)), top_features)
    plt.xlabel('Feature Importance')
    plt.title('Top 20 Most Important Features (Random Forest)')
    plt.tight_layout()
    plt.show()
    
    print("Top 10 Features:")
    for i, (feat, imp) in enumerate(zip(top_features[:10], top_importances[:10]), 1):
        print(f"{i:2d}. {feat:40s} | Importance: {imp:.4f}")

# ROC-Kurven visualisieren
plt.figure(figsize=(12, 8))
for model_name, model in models.items():
    y_pred_proba = model.predict_proba(X_test_transformed if 'Logistic' in model_name else X_test_prep)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, label=f'{model_name} (AUC = {roc_auc:.3f})')

plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC-Kurven aller Modelle')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()
```

---

## PHASE 5: Business Insights & Abschluss

```python
# ===== PHASE 5: BUSINESS INSIGHTS =====
print("\n" + "="*80)
print("GESCHÄFTLICHE INSIGHTS & EMPFEHLUNGEN")
print("="*80)

best_model = models[best_model_name]
best_metrics = results[best_model_name]

print(f"""
🎯 ZUSAMMENFASSUNG DER ERGEBNISSE
{'='*60}

1. BESTE PERFORMANCE:
   Modell: {best_model_name}
   ROC-AUC Score: {best_metrics['ROC-AUC']:.4f}
   F1-Score: {best_metrics['F1-Score']:.4f}
   Recall: {best_metrics['Recall']:.4f} (wichtig für Attack Detection!)

2. DATENQUALITÄT:
   - Trainings-Samples: {X_train_prep.shape[0]:,}
   - Test-Samples: {X_test_prep.shape[0]:,}
   - Features nach Engineering: {X_train_prep.shape[1]} (numerisch) + {len(cat_features)} (kategorial)
   - Class Balance: {y_train.value_counts()}

3. EMPFEHLUNGEN:
   ✅ Deployment: RAM-effiziente Modelle (LogReg, SVM)
   ✅ Performance: Complex Modelle (Random Forest, GB) für höhere Accuracy
   ✅ Balancing: Class Weight='balanced' beachten
   ✅ Monitoring: Regelmäßige Retraining nötig

4. NÄCHSTE SCHRITTE:
   - Hyperparameter-Tuning (GridSearchCV)
   - Feature Selection (Correlation Threshold)
   - Ensemble-Methoden testen
   - Production-Deployment
""")
```

---

## PHASE 5B: Abgabe-Vorbereitung

```python
# ===== PHASE 5B: DATEN FÜR FINALE PRÄSENTATION SPEICHERN =====

# Modelle speichern
import pickle

for model_name, model in models.items():
    filename = f"model_{model_name.replace(' ', '_')}.pkl"
    with open(filename, 'wb') as f:
        pickle.dump(model, f)
    print(f"✅ Modell gespeichert: {filename}")

# Results in CSV
results_df.to_csv('model_results.csv', index=True)
print(f"✅ Ergebnisse gespeichert: model_results.csv")

# Training History
print("\n✅ Modelle trainiert und exportiert!")
print("   Nächst: PDF + ZIP erstellen für Abgabe")
```

---

## 📋 Checkliste nach Implementierung

- [ ] Alle 5 Phasen im Notebook implementiert
- [ ] "Restart Kernel & Run All" durchführen und auf Fehler prüfen
- [ ] Output-Dateien vorhanden: `model_*.pkl`, `model_results.csv`
- [ ] Visualisierungen klar und beschriftet
- [ ] Business Insights in Markdown dokumentiert
- [ ] Notebook als PDF exportieren: `Cybersecurity_Final.pdf`
- [ ] ZIP-Paket erstellen mit:
  - `Cybersecurity.ipynb` (Code)
  - `Cybersecurity_Final.pdf` (Dokumentation)
  - `Eigenständigkeitserklärung.pdf` (unterschrieben)
  - `KI_Dokumentation.md` (verwendete Tools)
  - `model_results.csv` (Ergebnisse)
- [ ] Dateiname nach Konvention: `Nachname_Vorname_KursID.zip`

---

## ⏱️ Geschätzte Ausführungszeit

| Phase | Zeit |
|-------|------|
| Phase 1: Feature Engineering | 15 Min |
| Phase 2: Modelle trainieren | 45 Min (abhängig von Datengröße) |
| Phase 3: Evaluation | 15 Min |
| Phase 4: Feature Importance | 20 Min |
| Phase 5: Insights + Export | 10 Min |
| PDF + ZIP erstellen | 15 Min |
| **TOTAL** | **~2 Stunden** |

---

**✅ Mit diesem Plan ist das Notebook innerhalb von 2h fertig und abgabereif!**
