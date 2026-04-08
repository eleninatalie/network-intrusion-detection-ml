# Cybersecurity Intrusion Detection – ML Classification

> Automatische Erkennung von Netzwerkangriffen mittels Machine Learning auf dem UNSW-NB15-Datensatz

---

## Beschreibung

Dieses Projekt wurde im Rahmen des Kurses **DAN01 – Data Analyst** erstellt und untersucht, wie gut Machine-Learning-Modelle Cyberangriffe im Netzwerkverkehr erkennen können. Auf Basis des öffentlichen **UNSW-NB15**-Datensatzes (Australian Centre for Cyber Security) werden drei Modelle trainiert und miteinander verglichen:

| Modell | Rolle |
|---|---|
| Dummy Classifier | Baseline – untere Performanz-Schranke |
| Logistic Regression | lineares Vergleichsmodell |
| Decision Tree | Hauptmodell mit GridSearchCV-Tuning |

Die gesamte Pipeline umfasst explorative Datenanalyse (EDA), Datenbereinigung, Feature Engineering und Modelltraining – vollständig reproduzierbar und frei von Data Leakage.

---

## Forschungsfrage

> **Wie gut kann ein Machine-Learning-Modell im UNSW-NB15 Datensatz Angriffe bzw. auffällige Netzwerkverbindungen von normalem Netzwerkverkehr unterscheiden?**

---

## Projektübersicht

Dieses Projekt analysiert den **UNSW-NB15**-Datensatz (Australian Centre for Cyber Security) und trainiert mehrere Machine-Learning-Modelle zur binären Klassifikation von Netzwerkverkehr:

- **Normal (0):** regulärer Netzwerkverkehr
- **Angriff (1):** auffällige / bösartige Verbindungen

Die Klassenverteilung ist unbalanciert: ~81 % Normal, ~19 % Angriff.

---

## Datensatz

| Eigenschaft | Wert |
|---|---|
| Name | UNSW-NB15 |
| Quelle | Australian Centre for Cyber Security (ACCS) |
| Gesamtgröße | ~175.000 Netzwerkverbindungen |
| Features | 49 (reduziert auf 25 Raw-Network-Features, leakage-frei) |
| Zielvariable | `is_attack` (binär: 0 / 1) |

Die verwendeten CSV-Dateien sind **Leakage-bereinigte** Varianten:
- `UNSW_NB15_train_LEAKAGE_REMOVED.csv`
- `UNSW_NB15_test_LEAKAGE_REMOVED.csv`

---

## Projektstruktur

```
.
├── README.md
├── requirements.txt
├── data/
│   ├── UNSW_NB15_train_LEAKAGE_REMOVED.csv   # Rohdaten: Trainingsdaten (leakage-frei)
│   ├── UNSW_NB15_test_LEAKAGE_REMOVED.csv    # Rohdaten: Testdaten (leakage-frei)
│   ├── UNSW_NB15_training-set.csv            # Originaldatensatz für EDA
│   ├── cybersecurity_cleaned.csv             # Output: bereinigter Datensatz
│   ├── UNSW_NB15_train.csv                   # Output: ML-ready Trainingsdaten
│   └── UNSW_NB15_test.csv                    # Output: ML-ready Testdaten
├── notebooks/
│   ├── Cybersecurity.ipynb                   # Phase 1: EDA & Datenaufbereitung
│   ├── Dummy_Classifier_Training.ipynb       # Baseline-Modell (Stratified Random)
│   ├── Decision_Tree_Training_CORRECTED.ipynb
│   └── Logistic_Regression_Training_CORRECTED.ipynb
├── src/
│   └── utils.py                              # Gemeinsame Hilfsfunktionen
└── images/
    └── unsw_nb15_profiling_report.html       # Output: automatisierter EDA-Report
```

---

## Notebooks

### 1. `Cybersecurity.ipynb` – Explorative Datenanalyse (EDA)
- Datenimport & Initialisierung
- Train/Test-Split mit Stratification (80/20)
- Feature Engineering & Spaltenumbenennung
- Fehlende Werte & Ausreißer-Diagnose (Z-Score vs. IQR)
- Ausreißer-Entfernung (IQR-Methode)
- Univariate & bivariate Analyse
- Automatisierter EDA-Report via YData Profiling
- Encoding (One-Hot) & Scaling (StandardScaler)
- Export der ML-ready Datensätze

### 2. `Dummy_Classifier_Training.ipynb` – Baseline
- Stratified Random Classifier (kein echtes Lernen)
- Dient als untere Performanz-Schranke
- Erwartete Accuracy: ~69 %, AUC-ROC: ~0,50

### 3. `Decision_Tree_Training_CORRECTED.ipynb` – Hauptmodell
- Decision Tree Classifier mit GridSearchCV (5-Fold CV)
- Hyperparameter-Tuning: `max_depth`, `criterion`, `min_samples_split`, `min_samples_leaf`
- Feature Importance Analyse
- Erwartete Accuracy: ~93–94 %, AUC-ROC: ~0,96–0,98

### 4. `Logistic_Regression_Training_CORRECTED.ipynb` – Vergleichsmodell
- Logistic Regression mit StandardScaler + GridSearchCV
- Interpretierbares lineares Modell als Vergleich zum Decision Tree
- Erwartete Accuracy: ~88–92 %, AUC-ROC: ~0,93–0,96

---

## Modellvergleich (erwartet)

| Metrik | Dummy Baseline | Logistic Regression | Decision Tree |
|---|---|---|---|
| Accuracy | ~69 % | ~88–92 % | ~93–94 % |
| Precision | ~19 % | ~85–91 % | ~90–95 % |
| Recall | ~19 % | ~80–88 % | ~85–92 % |
| F1-Score | ~19 % | ~82–89 % | ~88–93 % |
| AUC-ROC | ~0,50 | ~0,93–0,96 | ~0,96–0,98 |

---

## Installation & Ausführung

### Voraussetzungen
- Python 3.8+
- Virtuelle Umgebung empfohlen

### Setup

```bash
# Virtuelle Umgebung erstellen und aktivieren
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### Reihenfolge der Notebooks

Notebooks müssen in dieser Reihenfolge ausgeführt werden:

```
1. Cybersecurity.ipynb
2. Dummy_Classifier_Training.ipynb
3. Decision_Tree_Training_CORRECTED.ipynb
4. Logistic_Regression_Training_CORRECTED.ipynb
```

---

## Reproduzierbarkeit

- `random_state=42` in allen Modellen und Splits gesetzt
- Stratified Train/Test Split (80/20) zur Erhaltung der Klassenverteilung
- Preprocessing (`StandardScaler`, `OneHotEncoder`) wird nur auf Trainingsdaten gefittet und auf Testdaten angewendet (kein Data Leakage)
- Alle Pfade sind relativ (keine absoluten Pfade)

---

## Technologien

| Kategorie | Bibliotheken |
|---|---|
| Datenverarbeitung | `pandas`, `numpy`, `scipy` |
| Visualisierung | `matplotlib`, `seaborn` |
| Machine Learning | `scikit-learn` |
| EDA-Report | `ydata-profiling` |
| Fehlende Werte | `missingno` |
| Umgebung | `jupyter`, `ipykernel` |

---

## Credits

| | |
|---|---|
| **Autorin** | Eleni Prangl |
| **Kurs** | DAN01 – Data Analyst |
| **Datensatz** | UNSW-NB15 – [Australian Centre for Cyber Security (ACCS)](https://research.unsw.edu.au/projects/unsw-nb15-dataset) |
| **Referenz** | Moustafa, N. & Slay, J. (2015). *UNSW-NB15: a comprehensive data set for network intrusion detection systems.* MilCIS. |
