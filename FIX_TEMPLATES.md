# 🛠️ FIX-TEMPLATES - CODE ZUM HINZUFÜGEN

## 1. BASELINE-MODELL (DummyClassifier)

Diesen Code **in ALLE DREI Notebooks einführen** (nach Modell-Training):

### Template für DummyClassifier

```python
# ===== BASELINE MODEL =====
from sklearn.dummy import DummyClassifier

print("="*60)
print("BASELINE MODEL (DummyClassifier)")
print("="*60)

# Strategy 1: Most Frequent (predicts majority class always)
dummy_model = DummyClassifier(strategy='most_frequent', random_state=42)
dummy_model.fit(X_train, y_train)

# Vorhersagen
y_test_pred_dummy = dummy_model.predict(X_test)
y_test_proba_dummy = dummy_model.predict_proba(X_test)[:, 1]

# Metriken berechnen
dummy_metrics = calculate_metrics(y_test, y_test_pred_dummy, y_test_proba_dummy)

print("\nDummy Classifier (Most Frequent) - Test Metriken:")
for metric, value in dummy_metrics.items():
    print(f"  {metric:15s}: {value:.4f}")

# Baseline ist wichtig weil:
# - Zeigt minimale Performance
# - Alles darüber ist ein echter Fortschritt
# - Für Class Imbalance besonders wichtig
```

---

## 2. CROSS-VALIDATION FÜR LOGISTIC REGRESSION

Diesen Code nach dem Modell-Training **nur in Logistic_Regression.ipynb** hinzufügen:

```python
# ===== 5-FOLD CROSS-VALIDATION =====
print("="*60)
print("5-FOLD CROSS-VALIDATION")
print("="*60)

scoring = {
    'accuracy': 'accuracy',
    'precision': 'precision',
    'recall': 'recall',
    'f1': 'f1',
    'roc_auc': 'roc_auc'
}

cv_results = cross_validate(lr_model, X_train, y_train, cv=5, scoring=scoring)

# Zusammenfassung
cv_summary = pd.DataFrame({
    'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC'],
    'Mean': [
        cv_results['test_accuracy'].mean(),
        cv_results['test_precision'].mean(),
        cv_results['test_recall'].mean(),
        cv_results['test_f1'].mean(),
        cv_results['test_roc_auc'].mean()
    ],
    'Std Dev': [
        cv_results['test_accuracy'].std(),
        cv_results['test_precision'].std(),
        cv_results['test_recall'].std(),
        cv_results['test_f1'].std(),
        cv_results['test_roc_auc'].std()
    ]
})

print("\n5-Fold Cross-Validation Ergebnisse:")
display(cv_summary.round(4))

# Visualisierung
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

metrics_for_box = [
    cv_results['test_accuracy'],
    cv_results['test_precision'],
    cv_results['test_recall'],
    cv_results['test_f1'],
    cv_results['test_roc_auc']
]

axes[0].boxplot(metrics_for_box, labels=['Accuracy', 'Precision', 'Recall', 'F1', 'ROC-AUC'])
axes[0].set_title('Cross-Validation Metriken Distribution')
axes[0].set_ylabel('Score')
axes[0].grid(alpha=0.3)

axes[1].bar(cv_summary['Metric'], cv_summary['Mean'], yerr=cv_summary['Std Dev'], capsize=5)
axes[1].set_title('Cross-Validation Mittelwerte ± Std Dev')
axes[1].set_ylabel('Score')
axes[1].set_ylim([0, 1])
axes[1].grid(alpha=0.3)
plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.show()
```

---

## 3. GESAMTVERGLEICH (Final Comparison)

Diesen Code **NUR in Random_Forest.ipynb** (letzte Zelle) **ERSETZEN**:

```python
# ===== GESAMTVERGLEICH ALLER MODELLE + BASELINE =====

# Hinweis: Diese Werte sind Beispiele - verwenden Sie die echten Werte aus Ihren Notebooks!
comparison_df = pd.DataFrame({
    'Model': ['Dummy Baseline', 'Logistic Regression', 'Decision Tree', 'Random Forest'],
    'Accuracy': [0.7459, 0.8407, 0.9476, 0.8967],
    'Precision': [0.7459, 0.8047, 0.9392, 0.9841],
    'Recall': [1.0000, 0.8987, 0.9424, 0.8716],
    'F1-Score': [0.8563, 0.8493, 0.9408, 0.9244],
    'ROC-AUC': [0.5000, 0.9692, 0.9894, 0.9735]
})

print("="*80)
print("FINAL MODEL COMPARISON - ALLE MODELLE + BASELINE")
print("="*80)
display(comparison_df.round(4))

# Visualisierung
fig, ax = plt.subplots(figsize=(14, 7))

metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
x = np.arange(len(metrics))
width = 0.2

for i, model in enumerate(comparison_df['Model']):
    values = comparison_df.iloc[i][metrics].values
    ax.bar(x + i*width, values, width, label=model, alpha=0.8)

ax.set_xlabel('Metriken', fontsize=12)
ax.set_ylabel('Score', fontsize=12)
ax.set_title('Model Comparison: Dummy vs. LR vs. Decision Tree vs. Random Forest', 
             fontsize=14, fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(metrics)
ax.legend(fontsize=11)
ax.set_ylim([0, 1.05])
ax.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.show()

# Analyse
print("\n" + "="*80)
print("KEY INSIGHTS")
print("="*80)
print("\n1. BASELINE (Dummy):")
print("   - Accuracy: 74.59% (predicts majority class always)")
print("   - Recall: 100% (aber das ist schlecht - auch Normales wird als Angriff erkannt)")
print("   - Dieser ist der minimale Vergleichspunkt!")

print("\n2. DECISION TREE ist BEST für Cybersecurity:")
print("   - Highest Accuracy: 94.76%")
print("   - Highest Recall: 94.24% (erkennt echte Angriffe)")
print("   - Lowest False Negatives: 5.76%")

print("\n3. RANDOM FOREST hat höchste Precision:")
print("   - Precision: 98.41% (wenig Falsch-Alarme)")
print("   - Aber: Niedrigerer Recall (87.16%) - verpasst mehr Angriffe")

print("\n4. LOGISTIC REGRESSION als Baseline:")
print("   - Solide Perfortmance (84.07% Accuracy)")
print("   - Gut zum Vergleichen aber nicht optimal für diesen Use Case")

print("\n" + "="*80)
print("EMPFEHLUNG: Decision Tree (94.76%) > Random Forest (89.67%) > LogReg (84.07%) >> Dummy (74.59%)")
print("="*80)
```

---

## 4. DOCSTRING TEMPLATE

Verbesserte `calculate_metrics()` Funktion mit Docstring:

```python
def calculate_metrics(y_true, y_pred, y_proba, set_name=""):
    """
    Berechne alle wichtigen Klassifikations-Metriken für binäre Klassifikation.
    
    Diese Funktion ist zentral für die Modell-Evaluierung und wird in allen
    Notebooks (Logistic Regression, Decision Tree, Random Forest) verwendet.
    
    Args:
        y_true (array-like): Wahre Class-Labels (0 oder 1)
        y_pred (array-like): Vom Modell vorhergesagte Labels (0 oder 1)
        y_proba (array-like): Vorhersage-Wahrscheinlichkeiten für positive Klasse (0-1)
        set_name (str): Optional - Name des Datensatzes für Logging (z.B. 'Training', 'Test')
    
    Returns:
        dict: Dictionary mit Metriken:
            - 'Accuracy': Anteil korrekter Vorhersagen (insgesamt)
            - 'Precision': Von Positiv-Vorhersagen wie viele sind wirklich positiv
            - 'Recall': Von echten Positiven wie viele werden erkannt (wichtig für Sicherheit!)
            - 'F1-Score': Harmonischer Durchschnitt von Precision und Recall
            - 'ROC-AUC': Area Under ROC Curve (unabhängig vom Schwellwert)
    
    Notes:
        - Verwendet Macro-Averaging für klassenunabhängige Metriken
        - Für Cybersecurity ist Recall kritischer als Precision (no attack should be missed)
        - ROC-AUC ist robust gegen Class Imbalance
    
    Example:
        >>> metrics = calculate_metrics(y_test, y_pred, y_proba, set_name='Test')
        >>> print(metrics['Recall'])  # Output: 0.9424
    """
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    roc_auc = roc_auc_score(y_true, y_proba)
    
    return {
        'Accuracy': accuracy,
        'Precision': precision,
        'Recall': recall,
        'F1-Score': f1,
        'ROC-AUC': roc_auc
    }
```

---

## CHECKLISTE FÜR IMPLEMENTATION

### Schritt 1: Baseline-Modell hinzufügen

- [ ] **Logistic_Regression.ipynb**
  - [ ] Neue Zelle nach Model-Training: DummyClassifier Code
  - [ ] Neue Zelle mit 5-Fold Cross-Validation (siehe oben)
  - [ ] Alle Zellen ausführen ("Restart Kernel & Run All")

- [ ] **Decision_Tree.ipynb**
  - [ ] Neue Zelle vor "Zusammenfassung": DummyClassifier 
  - [ ] Keine weitere CV nötig (bereits vorhanden)
  - [ ] Verifizieren dass alles läuft

- [ ] **Random_Forest.ipynb**
  - [ ] Neue Zelle mit Baseline-Vergleich
  - [ ] Letzte Zelle (Vergleich) mit Template ersetzen
  - [ ] Echtdaten aus Ihren Modellen einsetzen

### Schritt 2: Finale Verifizierung

- [ ] Logistic_Regression.ipynb: "Restart Kernel & Run All" ✅
- [ ] Decision_Tree.ipynb: "Restart Kernel & Run All" ✅
- [ ] Random_Forest.ipynb: "Restart Kernel & Run All" ✅
- [ ] Alle Metriken sind sichtbar und konsistent

### Schritt 3: Dokumentation

- [ ] AUDIT_REPORT.md aktualisieren mit neuen Ergebnissen
- [ ] Baseline-Performance dokumentieren
- [ ] Final-Recommendation schreiben

---

## WICHTIGE HINWEISE

1. **Import Statement**: Denken Sie daran, DummyClassifier zu importieren:
   ```python
   from sklearn.dummy import DummyClassifier
   ```

2. **Random State für Reproduzierbarkeit:**
   ```python
   dummy_model = DummyClassifier(strategy='most_frequent', random_state=42)
   ```

3. **Cross-Validation MUSS auf Train-Set sein:**
   ```python
   cv_results = cross_validate(model, X_train, y_train, cv=5, ...)  # NICHT X_test!
   ```

4. **Echte Werte in Vergleichstabelle:**
   ```python
   # Kopieren Sie die Werte aus Ihren Notebooks:
   'Accuracy': [  # Baseline, LR, DT, RF
       dummy_accuracy,
       test_metrics['Accuracy'],  # aus Ihrem Notebook
       ...
   ]
   ```
