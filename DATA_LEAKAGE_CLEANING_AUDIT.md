# 🔍 PRÜFBERICHT: Data Leakage, Cleaning, Feature Engineering
**Datum:** 30. März 2026  
**Kürzel:** B2 - Data Preparation  

---

## ⚠️ KRITISCHE ERKENNTNISSE

### 1. DATA LEAKAGE - Teilweise PROBLEMATISCH

#### ✅ What's good:
```
Phase 3 (Zelle 8): Train/Test Split RICHTIG
    X_train, X_test, y_train, y_test = train_test_split(..., stratify=y)
    ✅ Split erfolgt VORHER Preprocessing
    ✅ Stratification korrekt (class_weight!)
```

#### ⚠️ Problem 1: Ausreißer-Schwellwerte
```python
# Aktuell (Zelle 19):
Q1 = df[numeric_columns].quantile(0.25)  # df = X_train ✅
Q3 = df[numeric_columns].quantile(0.75)  # Basierend auf X_train ✅
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
mask_no_outliers_iqr = ~(df[numeric_columns] < lower_bound | ...)

# ✅ RICHTIG: Grenzen auf X_train berechnet, auf X_train angewendet
# ❌ ABER: X_test wird NICHT mit denselben Grenzen behandelt!
#         → X_test hat potentiell immer noch "Ausreißer" (nach Training-Grenzen)
#         → Das ist nicht optimal für Real-World Inference
```

**Kritik:** X_test sollte mit denselben Grenzen (fit auf X_train) gesampled werden!

#### ⚠️ Problem 2: Missing Values Imputation
```python
# Zelle 26 (Phase 11):
for col in num_cols:
    if clean_df[col].isnull().any():
        median_val = clean_df[col].median()  # Median auf X_train ✅
        clean_df[col] = clean_df[col].fillna(median_val)

# ✅ RICHTIG: Median auf X_train berechnet
# ❌ ABER: X_test wird NICHT geimputed mit demselben Median!
#         → X_test hat immer noch NaNs wenn vorhanden
```

**Kritik:** X_test sollte mit denselben Imputation-Statistiken (fit auf X_train) gefüllt werden!

#### ❌ Problem 3: Feature Engineering - KRITISCH!
```python
# Zelle 28 (Phase 12):
from sklearn.preprocessing import StandardScaler, OneHotEncoder

df_clean = clean_df.copy()
df_clean = df_clean.drop(columns=['attack_cat', 'connection_id'], errors='ignore')

# ❌ PROBLEM: Hier stoppt der Code!
# - StandardScaler wird IMPORTIERT aber NICHT VERWENDET
# - OneHotEncoder wird IMPORTIERT aber NICHT VERWENDET
# - df_clean wird nicht für Train/Test separiert!
# - Keine fit() auf X_train, keine transform() auf X_test!

# WAS FEHLT:
# 1. Separate X_train_encoded, X_test_encoded erstellen
# 2. Categorical Columns identifizieren
# 3. OneHotEncoder mit fit() auf X_train, transform() auf beide
# 4. StandardScaler mit fit() auf X_train, transform() auf beide
# 5. Ergebnis speichern: UNSW_NB15_train.csv, UNSW_NB15_test.csv
```

**Kritik:** Feature Engineering ist UNVOLLSTÄNDIG und würde zu DATA LEAKAGE führen wenn implementiert!

---

## 2. CLEANING - Teilweise DOKUMENTIERT

### ✅ What's documented:
```
Phase 5: "Primäre Methode: Median für numerisch, Modus für kategorial"
Phase 7: "IQR robust gegen Extremwerte. Best für schiefe Verteilungen."
Phase 7: "Z-Score > 3: Normalverteilung-Annahme"
Phase 8: "1.5 * IQR Boxplot-Regel"
```

### ⚠️ Was FEHLT:
```
1. BEGRÜNDUNG FÜR METHODENWAHL:
   - Warum IST die Verteilung schief? (nicht gezeigt)
   - Deswegen: IQR statt Z-Score? (Logik-Lücke)
   - ❌ Histogramme zeigen Verteilungen (Zelle 16)
   - ✅ Aber: Keine Interpretation "daher nutzen wir IQR"

2. PROZESS DOKUMENTATION:
   Phase 7: "Diagnose" - zeigt Ausreißer-Anzahl pro Methode
   ✅ aber: Wenn Z-Score sagt 5 Ausreißer, IQR sagt 500,
      WELCHE wählen wir und WARUM?
      → Keine Entscheidungslogik dokumentiert!

3. IMPACT ANALYSE:
   ❌ Fehlend: Wie viele Zeilen werden gelöscht? (Prozent der Daten)
   ❌ Fehlend: Verlieren wir wichtige Attack-Samples?
       (z.B. "Outlier removal: 10,000 rows deleted,
               davon 8,000 Attack-Samples = 26% Attack-Rate verloren!")

4. IMPUTATION BEGRÜNDUNG:
   ✅ "Median für numerisch, Modus für kategorial"
   ❌ Warum nicht KNN-Imputation? Mean? Deletion?
   ❌ Warum nicht geschichtet nach Label (Normal vs. Attack)?
       (z.B. Attack-Traffic hat andere Median!)
```

---

## 3. FEATURE ENGINEERING - UNVOLLSTÄNDIG!

### ✅ Was implementiert ist:
```
1. Feature Renaming (Phase 4): ✅ Dictionary + Umbenennung
2. Missing Values (Phase 5): ✅ Detection + Imputation
3. Ausreißer-Entfernung (Phase 8): ✅ IQR-Methode
4. Duplikat-Entfernung (Phase 11): ✅ .drop_duplicates()
```

### ❌ Was FEHLT:
```
1. ONE-HOT ENCODING:
   - ✅ Importiert: from sklearn.preprocessing import OneHotEncoder
   - ❌ Nicht verwendet!
   - ❌ Kategoriale Spalten (protocol, service, state) sind immer noch
        als Integer oder String kodiert
   - Modelle in ANDEREN Notebooks laden UNSW_NB15_train.csv
        → FEHLER: Kategoriale Variablen sind nicht numerisch kodiert!

2. STANDARDSCALING:
   - ✅ Importiert: from sklearn.preprocessing import StandardScaler
   - ❌ Nicht verwendet!
   - ❌ Numerische Features haben unterschiedliche Skalierung
        → Logistic Regression wird nicht optimal funktionieren!
   - ❌ X_test wird nicht skaliert
        → Mismatch zwischen Train- und Test-Features!

3. FEATURE SELECTION:
   - ❌ Nicht erwähnt: Sollten alle 49 Features verwendet werden?
   - ❌ Multikollinearität? (Korrelationsmatrix zeigt hohe Werte)
   - ❌ Optional: Top-Features nach Importance selektieren?

4. TRAIN/TEST SEPARATION:
   - ❌ Encoding wird nicht auf X_train und X_test SEPARIERT angewendet
   - ❌ Keine Speicherung von X_train_transformed, X_test_transformed
   - ❌ Modell-Notebooks erhalten NICHT die gleiche Preprocessing!

5. CSV-EXPORT:
   - ✅ `cybersecurity_cleaned.csv` gespeichert
   - ⚠️ `cybersecurity_engineered.csv` gespeichert
   - ❌ Aber: `UNSW_NB15_train.csv`, `UNSW_NB15_test.csv` sind
        NICHT mit Feature Engineering aktualisiert!
   - ❌ Modell-Notebooks laden alte Versionen!
```

---

## 📊 PRÜFERGEBNIS GEGEN ANFORDERUNGEN

### Anforderung B2.1: "Umgang mit Missing Values und Outliers ist methodisch begründet"
- **Median/Modus:** ✅ Genannt
- **IQR vs. Z-Score:** ✅ Genannt
- **Aber:** ❌ **Begründung INCOMPLETE**
  - Warum IQR wählen? (Datenverteilung nicht formal analysiert)
  - Warum 1.5 * IQR? (Konvention, aber nicht in Sicherheits-Kontext begründet)
  - Impact: Wie viel Daten verloren? Wie viel Attack-Samples?
  - **Score: 60/100**

### Anforderung B2.2: "Transformationen nachvollziehbar implementiert"
- **Feature Renaming:** ✅ Vollständig
- **Encoding:** ❌ NICHT implementiert
- **Scaling:** ❌ NICHT implementiert
- **Score: 30/100**

### Anforderung B2.3: "Strikte Trennung Train/Test vor Transformationen"
- **Train/Test Split:** ✅ Timing RICHTIG (Zelle 8 - VORHER)
- **Aber:** ⚠️ Preprocessing wird nicht SEPARIERT:
  - Ausreißer-Grenzen: Auf X_train berechnet ✅, auf X_test angewendet ❌
  - Missing Values: Auf X_train imputed, X_test NICHT imputed
  - Feature Engineering: X_train + X_test nicht SEPARIERT transformiert
- **Score: 50/100**

---

## 🔧 KONKRETE FIXES ERFORDERLICH

### Fix 1: Cleaning-Begründung erweitern
```markdown
**Phase 7 Erweitern:**
- Zeige Verteilungsanalyse (Normal? Schief? Bimodal?)
- Begründe: "Weil 75% der Features schief sind, nutzen wir IQR"
- Quantifiziere Impact: "Entfernung: 5.000 Zeilen (-3%), davon 1.500 Attack-Samples (-5%)"
- Begründe: "Residuale Attack-Samples sind ausreichend für Training"
```

### Fix 2: Missing Values - Statistische Begründung
```python
# Phase 5 ergänzen:
print("Analyse fehlender Werte nach Label:")
print(f"Normal-Traffic: {df[df['is_attack']==0].isnull().sum()}")
print(f"Attack-Traffic: {df[df['is_attack']==1].isnull().sum()}")
print("→ Feststellung: Muster zufällig? Oder Attack-spezifisch?")
print("→ Entscheidung: Median gesamt (nicht per Label, da gering)")
```

### Fix 3: Feature Engineering separiert implementieren
```python
# Zelle 28 KOMPLETT UMSCHREIBEN:
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Kategoriale vs. numerische Features trennen
cat_features = df_clean_train.select_dtypes(include=['object']).columns.tolist()
num_features = df_clean_train.select_dtypes(include=['number']).columns.tolist()

# ColumnTransformer: One-Hot Encoding + Scaling
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_features),
        ('cat', OneHotEncoder(sparse=False, handle_unknown='ignore'), cat_features)
    ]
)

# Fit auf X_train, transform auf beide
X_train_transformed = preprocessor.fit_transform(X_train_clean)
X_test_transformed = preprocessor.transform(X_test_clean)

# Speichern
pd.DataFrame(X_train_transformed).to_csv('UNSW_NB15_train.csv', index=False)
pd.DataFrame(X_test_transformed).to_csv('UNSW_NB15_test.csv', index=False)
```

### Fix 4: X_test parallel behandeln
```python
# Nach Ausreißer-Entfernung (Zelle 19):
# Nutze GLEICHE Grenzen auf X_test:
X_test_cleaned = X_test[(X_test[numeric_columns] >= lower_bound) & 
                         (X_test[numeric_columns] <= upper_bound)]
```

---

## 📋 ZUSAMMENFASSUNG DER MÄNGEL

| Punkt | Status | Priorität | Fix-Zeit |
|-------|--------|-----------|----------|
| Missing Values Begründung | ⚠️ Teilweise | HOCH | 15 Min |
| Outlier Impact quantifizieren | ❌ Fehlt | HOCH | 20 Min |
| IQR-Logik dokumentiert | ⚠️ Schwach | MITTEL | 10 Min |
| One-Hot Encoding implementieren | ❌ FEHLT | 🔴 KRITISCH | 20 Min |
| StandardScaler implementieren | ❌ FEHLT | 🔴 KRITISCH | 15 Min |
| X_test mit gleichen Grenzen | ❌ FEHLT | 🔴 KRITISCH | 30 Min |
| Feature Engineering separiert | ❌ FEHLT | 🔴 KRITISCH | 30 Min |

---

## ✅ ABFORDERUNG-PRÜFUNG

```
Anforderung: "Cleaning: Umgang mit Missing Values und Outliers ist methodisch 
             begründet und dokumentiert."
✅ Teilweise erfüllt (60%):
   - Was ist vorhanden: Methoden genannt (Median, IQR)
   ❌ Was fehlt: 
     - Warum diese Methoden? (Datenverteilung-Analyse)
     - Welcher Impact? (Reihen gelöscht, Prozent)
     - Sicherheits-spezifische Überlegungen

Anforderung: "Feature Engineering: Transformationen nachvollziehbar implementiert"
❌ NICHT erfüllt (30%):
   - Renaming: ✅ OK
   - Encoding: ❌ Nicht implementiert!
   - Scaling: ❌ Nicht implementiert!
   
Anforderung: "Data Leakage: Strikte Trennung Train/Test vor Transformationen"
⚠️ Teilweise erfüllt (50%):
   - Timeline richtig: Train/Test VORHER ✅
   - Aber: Transformationen nicht SEPARIERT
   - X_test = X_train? Oder getrennt transformiert?
```

---

## 🚨 AUSWIRKUNGEN FÜR MODELLE

Die modellen Notebooks (Logistic_Regression, Decision_Tree, Random_Forest) laden 
`UNSW_NB15_train.csv` und `UNSW_NB15_test.csv`.

**PROBLEM:** Diese CSVs haben KEINE Feature Engineering!
- Kategoriale Variablen sind nicht encodiert
- Numerische Variablen sind nicht skaliert
- → **Modelle werden nicht optimal funktionieren!**

**LÖSUNG ERFORDERLICH:**
1. Feature Engineering in Zelle 28 fertigstellen
2. train.csv + test.csv mit Encoding + Scaling überschreiben
3. Alle Modell-Notebooks erneut laufen lassen
