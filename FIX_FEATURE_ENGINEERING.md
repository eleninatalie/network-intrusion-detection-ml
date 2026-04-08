# 🛠️ FIX-ANLEITUNG: Feature Engineering (Zelle 28)

## Problem
Feature Engineering ist unvollständig!
- StandardScaler + OneHotEncoder sind importiert aber nicht verwendet
- Kategoriale Variablen sind nicht encodiert
- Numerische Variablen sind nicht skaliert
- X_test wird nicht berücksichtigt

## Lösung: Python-Code für Zelle 28 (Muss ersetzen):

```python
# ===== FEATURE ENGINEERING: Encoding + Scaling =====
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import pandas as pd
import numpy as np

print("=" * 80)
print("PHASE 12: Feature Engineering für ML-ready Datensätze")
print("=" * 80)

# Feature-Typen identifizieren
cat_features = clean_df.select_dtypes(include=['object', 'category']).columns.tolist()
num_features = clean_df.select_dtypes(include=['number']).columns.tolist()

print(f"\n✅ Kategoriale Features ({len(cat_features)}): {cat_features}")
print(f"✅ Numerische Features ({len(num_features)}): {num_features[:5]}... ({len(num_features)} total)")

# ColumnTransformer für Feature Engineering
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_features),
        ('cat', OneHotEncoder(sparse=False, handle_unknown='ignore', drop='first'), cat_features)
    ],
    remainder='drop'
)

# FIT auf Training-Daten, TRANSFORM auf beide
print("\n⏳ Applying Feature Normalization to Training & Test Set...")
X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)

print(f"✅ X_train transformiert: {X_train.shape} → {X_train_transformed.shape}")
print(f"✅ X_test transformiert: {X_test.shape} → {X_test_transformed.shape}")

# Zu DataFrame konvertieren + Target hinzufügen
X_train_df = pd.DataFrame(X_train_transformed)
X_train_df['is_attack'] = y_train.values

X_test_df = pd.DataFrame(X_test_transformed)
X_test_df['is_attack'] = y_test.values

# Speichern für Modell-Notebooks
X_train_df.to_csv('UNSW_NB15_train.csv', index=False)
X_test_df.to_csv('UNSW_NB15_test.csv', index=False)

print(f"\n✅ ML-ready CSVs gespeichert:")
print(f"   - UNSW_NB15_train.csv: {X_train_df.shape}")
print(f"   - UNSW_NB15_test.csv: {X_test_df.shape}")
print(f"\n💾 Diese werden von Modell-Notebooks geladen!")
```

---

## FIX 2: Cleaning-Begründung dokumentieren

### Wo? Zelle 19 (Phase 8) - nach IQR-Berechnung

Füge hinzu:

```python
# ===== IMPACT ANALYSE =====
print(f"\n📊 AUSREISSER-ENTFERNUNG IMPACT:")
print(f"Vor IQR-Bereinigung: {df.shape[0]} Zeilen")
print(f"Nach IQR-Bereinigung: {df_no_outliers_iqr.shape[0]} Zeilen")
deleted_rows = df.shape[0] - df_no_outliers_iqr.shape[0]
deleted_pct = (deleted_rows / df.shape[0]) * 100
print(f"Gelöschte Zeilen: {deleted_rows} ({deleted_pct:.1f}%)")

# Nach Label analysieren
print(f"\n🎯 Impact nach Attack-Label:")
attack_before = (df['is_attack'] == 1).sum()
attack_after = (df_no_outliers_iqr['is_attack'] == 1).sum()
attack_lost = attack_before - attack_after
attack_lost_pct = (attack_lost / attack_before) * 100 if attack_before > 0 else 0
print(f"Normal-Samples vor: {(df['is_attack']==0).sum()}, nach: {(df_no_outliers_iqr['is_attack']==0).sum()}")
print(f"Attack-Samples vor: {attack_before}, nach: {attack_after}")
print(f"→ Verlorene Attack-Samples: {attack_lost} ({attack_lost_pct:.1f}%)")

print(f"\n✅ Bewertung: {'✅ Akzeptabel' if attack_lost_pct < 10 else '⚠️ Kritisch - zu viel verloren!'}")
```

---

## FIX 3: IQR-Methodenwahl begründen

### Wo? Phase 7 Markdown-Zelle - Erweitern

Füge nach "Z-Score vs. IQR" hinzu:

```markdown
### Entscheidungslogik
1. **Analyse der Verteilungen (Zelle 16):**
   - 75%+ der numerischen Features sind rechtsgschief (nicht normal)
   - Multimodale Verteilungen vorhanden
   - **→ Z-Score Assumption (Normalverteilung) verletzt**

2. **Daher: IQR-Methode gewählt**
   - ✅ Robust gegen schiefe Verteilungen
   - ✅ Keine Normalverteilungs-Annahme nötig
   - ✅ Boxplot-Standard (1.5 * IQR) bewährt in Praxis
   - ❌ Z-Score würde zu viele Anomalien übersehen

3. **Impact (siehe Zelle 19):**
   - Z-Score hätte X Ausreißer gefunden
   - IQR findet Y Ausreißer (robuster)
   - Gelöschte Zeilen: Z% (davon W% Attack-Samples)
```

---

## FIX 4: Missing Values Begründung erweitern

### Wo? Phase 5 nach Code-Zelle

Füge hinzu:

```python
# ===== IMPUTATION STRATEGIE BEGRÜNDUNG =====
print("📊 MISSING VALUES HANDLING LOGIC:")
print("\nBegründung für Median/Modus:")
print("1. Median ist robust gegen Extremwerte (besser als Mean)")
print("2. Modus für kategoriale Features (häufigster Wert)")
print("3. Warum nicht KNN/MICE? → Zu komplex für diesen Kontext")
print("4. Warum nicht nach Label? → Missing-Rate zu niedrig (..) für Label-Schichtung")

print(f"\nFehlende Werte nach Kategoriecal:")
for col in categorical_columns:
    missing_pct = (df[col].isnull().sum() / len(df)) * 100
    print(f"  {col}: {missing_pct:.2f}%")
    
print(f"\nFehlende Werte nach Numerisch:")
for col in numeric_columns[:5]:  # Top 5
    missing_pct = (df[col].isnull().sum() / len(df)) * 100
    if missing_pct > 0:
        print(f"  {col}: {missing_pct:.2f}%")
```

---

## 📋 Implementation-Checkliste

- [ ] Zelle 28 komplett überwrite mit obigem Code
- [ ] Zelle 19 um Impact-Analyse erweitern
- [ ] Zelle 12 um Missing-Value-Begründung erweitern
- [ ] Phase 7 Markdown um Entscheidungslogik erweitern
- [ ] **Kernel → Run All** durchführen
- [ ] `UNSW_NB15_train.csv`, `UNSW_NB15_test.csv` überprüfen (sollten größer sein)
- [ ] Modell-Notebooks mit neuem Kernel durchführen

---

## ⏱️ Zeit estimate
- **Feature Engineering Code:** 10 Min (Copy-Paste + Run)
- **Cleaning-Dokumentation:** 15 Min (Schnelle Additions)
- **Gesamt:** ~25 Min bis alles fertig
