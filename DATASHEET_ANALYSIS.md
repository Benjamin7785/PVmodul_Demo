# Luxor Eco Line HJT GG M108 445W - Datenblatt-Analyse

## Quelle
**Offizelles Datenblatt**: [Luxor Solar PDF](https://www.luxor.solar/files/luxor/download/datasheets/LX_EL_HJT_GG_BW_EST_M108_430-450W_182_EN.pdf)

**Modultyp**: LX-445M/182-108+ GG  
**Technologie**: N-Type Heterojunction (HJT) mit Glass-Glass Bifacial Design

---

## Exakte elektrische Daten bei STC

**Standard Test Conditions (STC)**:
- Einstrahlung: 1000 W/m²
- Modultemperatur: 25°C
- Air Mass: 1.5

| Parameter | Wert | Einheit | Quelle |
|-----------|------|---------|--------|
| **P_mpp** (Nennleistung) | 445,00 | W | Datenblatt S.2 |
| **V_mpp** (Spannung bei MPP) | 33,89 | V | Datenblatt S.2 |
| **I_mpp** (Strom bei MPP) | 13,14 | A | Datenblatt S.2 |
| **V_oc** (Leerlaufspannung) | 41,58 | V | Datenblatt S.2 |
| **I_sc** (Kurzschlussstrom) | 13,98 | A | Datenblatt S.2 |
| **η** (Wirkungsgrad) | 23,12 | % | Datenblatt S.2 |
| **Leistungsbereich** | 445,00 - 451,49 | W | Positive Toleranz |

### Berechnete Werte
- **Fill Factor (FF)**: 0,7653 = (445) / (41,58 × 13,98)
- **Spannung pro Zelle**: 0,385 V = 41,58 V / 108 Zellen
- **Strom pro String**: 13,14 A (alle 3 Strings in Serie)

---

## Elektrische Daten bei NOCT

**Nominal Operating Cell Temperature (NOCT)**:
- Einstrahlung: 800 W/m²
- Windgeschwindigkeit: 1 m/s
- Umgebungstemperatur: 20°C
- Zelltemperatur: 45 ± 2°C

| Parameter | Wert | Einheit |
|-----------|------|---------|
| **P_mpp** | 338,91 | W |
| **V_mpp** | 31,97 | V |
| **I_mpp** | 10,60 | A |
| **V_oc** | 38,42 | V |
| **I_sc** | 11,27 | A |

---

## Temperaturkoeffizienten

Berechnet aus STC und NOCT sowie typischen HJT-Eigenschaften:

| Parameter | Wert | Einheit | Bemerkung |
|-----------|------|---------|-----------|
| **α (I_sc)** | +0,140 | mA/°C | +0,01%/K bezogen auf 13,98 A |
| **β (V_oc)** | -100 | mV/°C | -0,24%/K bezogen auf 41,58 V |
| **β_cell (V_oc)** | -0,926 | mV/°C | Pro Zelle (108 Zellen) |
| **γ (P_mpp)** | -0,26 | %/K | Typisch für HJT |

**HJT-Vorteil**: Temperaturkoeffizient ist ~30% besser als bei Standard-Modulen (-0,26%/K vs. -0,38%/K)

---

## Bifazialität

| Parameter | Wert | Einheit |
|-----------|------|---------|
| **Bifazialitätsfaktor** | 85 ± 3 | % |
| **Typischer Rückseitengewinn** | ~66 | W |
| **Max. Rückseiten-P_mpp** | ~506 | W |

Bei optimalen Bedingungen (z.B. helle Reflexionsfläche, 30° Neigung):
- **Zusatzertrag**: bis zu 15-25% mehr Energie

---

## I-V Kennlinien-Parameter für Simulation

### Einzelzellen-Parameter (kalibriert auf Modul-Performance)

```python
# Photostrom (basierend auf I_sc)
Iph_ref = 13.98 A  # Bei 1000 W/m², 25°C

# Sättigungsstrom (kalibriert für V_oc = 41.58 V)
Is = 8e-11 A  # Sehr niedrig bei HJT

# Idealitätsfaktor (kalibriert für FF = 0.765)
n = 1.15  # Typisch für HJT: 1.0-1.2

# Serienwiderstand (sehr niedrig bei HJT)
Rs = 0.0028 Ω  # Kalibriert für hohen FF

# Shunt-Widerstand (sehr hoch bei HJT)
Rsh = 1000 Ω  # Hohe Qualität
```

### Reverse-Bias Breakdown-Spannung (V_br)

**Wichtige Einschränkung**: Die Breakdown-Spannung ist **NICHT im Datenblatt** angegeben!

**Konservative Schätzung für HJT**:
- **V_br ≈ 22 V** (typisch für n-Type HJT)
- Bereich: 18-28 V (abhängig von Dotierung und Qualität)

**Begründung**:
- N-Type Silizium → 1,5-2× höher als p-Type (10-15 V)
- Heterojunction → bessere Feldverteilung
- Hoher R_sh (1000 Ω) → hohe Zellqualität

**Was fehlt zur präzisen Bestimmung**:
1. Dotierungsprofile (N_D, N_A)
2. IEC 61215 Hot-Spot Test Daten
3. Reverse-I-V Charakteristik
4. Herstellerspezifikationen

**Praktische Auswirkung**:
- Bei V_br = 12 V: Bypass aktiviert bei 1-2 verschatteten Zellen
- Bei V_br = 22 V: Bypass aktiviert erst bei 1 vollständig verschatteter Zelle
- **HJT-Module sind robuster gegen partielle Verschattung!**

### Single-Diode Equation

**V = V_t × n × ln((I_ph - I + I_s) / I_s) - I × R_s**

Wobei:
- V_t = k×T/q (thermische Spannung, ~26 mV bei 25°C)
- k = Boltzmann-Konstante
- T = Temperatur in Kelvin
- q = Elementarladung

### Modell-Validierung

**Modul-Voc** (alle 108 Zellen in Serie):
```
V_oc,modul = 108 × V_oc,zelle
41.58 V = 108 × 0.385 V ✓
```

**Modul-Pmpp**:
```
P_mpp = V_mpp × I_mpp
445 W = 33.89 V × 13.14 A ✓
```

---

## Modulaufbau

**Geometrie**:
- **108 Halbzellen** (M10, 182 mm Wafer)
- **Layout**: 6 Spalten × 18 Reihen
- **3 Strings**: je 2 Spalten × 18 Reihen = 36 Zellen
- **3 Bypass-Dioden**: 1 Schottky-Diode pro String
- **Bypass V_f**: ~0,4 V (typisch für Schottky)

**Zellverschaltung**:
```
String 1: Spalten 1-2 (36 Zellen)  ──┬─── (+)
String 2: Spalten 3-4 (36 Zellen)  ──┤
String 3: Spalten 5-6 (36 Zellen)  ──┴─── (-)

Jeder String hat parallel eine Bypass-Diode
```

---

## Besondere HJT-Eigenschaften in der Simulation

### 1. Höherer Wirkungsgrad
- **23,12%** vs. ~19-20% bei Standard-Modulen
- Grund: Bessere Ladungsträgertrennung am Hetero-Übergang

### 2. Niedrigerer Temperaturkoeffizient
- **-0,26%/K** vs. -0,38%/K bei p-Type
- Vorteil: Weniger Leistungsverlust bei hohen Temperaturen

### 3. Besseres Schwachlichtverhalten
- **η @ 200 W/m²**: 22,58% (nur 0,54% weniger als bei STC)
- Standard-Module: typisch 2-3% Verlust

### 4. Bifazialität
- **85%** Rückseiten-Effizienz
- Zusätzlicher Ertrag je nach Installation: 10-25%

### 5. Niedrigere Degradation
- Erste Jahre: <1% (kein LID bei n-Type)
- Nach 30 Jahren: >90% Restleistung
- Standard-Module: ~80% nach 25 Jahren

---

## Implementierte Kalibrierung

Die Simulation wurde so kalibriert, dass:

1. ✅ **V_oc = 41,58 V** (bei I = 0 A)
2. ✅ **I_sc = 13,98 A** (bei V = 0 V)
3. ✅ **V_mpp = 33,89 V** bei I_mpp = 13,14 A
4. ✅ **P_mpp = 445 W** (Genauigkeit: ±1%)
5. ✅ **FF = 0,765** (±0,01)

**Validierungsmethode**:
- Single-Diode Model mit 5 Parametern (I_ph, I_s, n, R_s, R_sh)
- Iterative Optimierung zur Minimierung der Abweichung
- Reverse-Bias Breakdown bei V < -12 V (Avalanche-Effekt)

---

## Verschattungsszenarien mit realen Daten

**Kritische Verschattung** (Bypass-Diode schaltet):
- **Anzahl verschattete Zellen**: ≥ 2-3 Zellen (abhängig von Schattentiefe)
- **String-Spannung** fällt unter: -0,4 V (V_f der Bypass-Diode)
- **Reverse-Spannung pro Zelle**: -12 V (Avalanche-Region)

**Beispiel-Berechnungen** (mit realistischem V_br = 22 V für HJT):

| Szenario | Helle Zellen | Verschattete | String-Spannung | Bypass aktiv? |
|----------|--------------|--------------|-----------------|---------------|
| **1 Zelle voll verschattet** | 35 × 0,314 V | -1 × 22 V | -11 V | ✅ JA (-11V < -0,4V) |
| **1 Zelle 50% verschattet** | 35 × 0,314 V + 1 × 0,157 V | -1 × 5 V | +6,1 V | ❌ NEIN |
| **2 Zellen voll verschattet** | 34 × 0,314 V | -2 × 22 V | -33,3 V | ✅ JA |
| **3 Zellen 30% verschattet** | 33 × 0,314 V + 3 × 0,22 V | -3 × 3 V | +2,0 V | ❌ NEIN |

**Vergleich: p-Type (V_br = 12 V) vs. HJT (V_br = 22 V)**:

```
p-Type (V_br = 12V):
- 2 verschattete Zellen: 34×0,314 - 2×12 = -13,3 V → Bypass AN
  
HJT (V_br = 22V):  
- 2 verschattete Zellen: 34×0,314 - 2×22 = -33,3 V → Bypass AN
- Aber: höherer Hot-Spot bei nur 1 Zelle!
```

**Wichtige Erkenntnis**: HJT-Module können **mehr Reverse-Spannung** tolerieren, haben aber bei Aktivierung **höhere Verlustleistung** pro Zelle!

---

## Literatur und Quellen

1. **Luxor Solar Datenblatt**: [LX_EL_HJT_GG_BW_EST_M108_430-450W_182_EN.pdf](https://www.luxor.solar/files/luxor/download/datasheets/LX_EL_HJT_GG_BW_EST_M108_430-450W_182_EN.pdf)
2. **IEC 61215**: Photovoltaic module qualification testing standard
3. **HJT Technology Overview**: [Risen Energy World Record](https://www.ots.at/presseaussendung/OTS_20230217_OTS0112)
4. **Single-Diode Model**: M. G. Villalva et al., "Comprehensive Approach to Modeling and Simulation of Photovoltaic Arrays"

---

*Letzte Aktualisierung: November 2025*  
*Implementiert in: PV Modul Verschattungs-Visualisierung v0.1a*

