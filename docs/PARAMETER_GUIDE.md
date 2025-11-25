# Parameter-Guide für PV-Modul Visualisierung

## Übersicht der Strom-Parameter

Die App verwendet **zwei verschiedene Strom-Slider** mit unterschiedlichen Zwecken:

---

## 1️⃣ "Max. Strom für I-V-Kurve" (Parameter-Seite)

### Technischer Name
- **ID**: `current-slider`
- **Location**: Parameter-Sektion (alle Seiten mit Parameter-Controls)

### Zweck
Definiert den **maximalen Strombereich** für die Berechnung der I-V-Kennlinien.

### Funktionsweise
```python
# Berechnet I-V Kurve von 0 bis max_current
currents = np.linspace(0, max_current, points=300)
voltages = [module.voltage_at_current(I) for I in currents]
```

### Wann wichtig?
- ✅ **I-V Kennlinien-Seite**: Bestimmt den dargestellten Bereich
- ✅ **Vollständige Kurven**: Sollte ≥ I_sc sein für komplette Darstellung
- ❌ **Nicht direkt** für Spannungsverteilung (dort wird spezifischer Strom gewählt)

### Empfohlene Einstellung
- **Standard**: 14 A (leicht über I_sc = 13,98 A)
- **Bereich**: 0-15 A
- **Faustregel**: Immer ≥ I_sc für vollständige I-V Kurve

### Beispiel
```
Wenn max_current = 10 A:
→ I-V Kurve zeigt nur 0-10 A
→ Fehlende Werte: 10-13,98 A (Kurzschlussbereich)

Wenn max_current = 14 A:
→ Vollständige Kurve von 0 bis I_sc (13,98 A)
→ Alle Betriebspunkte sichtbar ✓
```

---

## 2️⃣ "Analyse-Betriebsstrom" (Betriebspunkt-Seite)

### Technischer Name
- **ID**: `operating-current-slider`
- **Location**: Spannungsverteilungs-Seite, Betriebspunkt-Sektion

### Zweck
Wählt einen **spezifischen Betriebspunkt** zur detaillierten Analyse der Spannungsverteilung im Modul.

### Funktionsweise
```python
# Berechnet Spannungsverteilung bei gewähltem Strom
selected_current = 13.14  # A (z.B. I_mpp)
voltage_map = module.get_cell_voltage_map(selected_current)
# Zeigt: Spannung jeder der 108 Zellen
```

### Wann wichtig?
- ✅ **Spannungsverteilungs-Visualisierung**: Direkt verwendet
- ✅ **Hot-Spot Analyse**: Basis für Leistungsdissipation
- ✅ **Bypass-Dioden Status**: Schaltzustand abhängig von diesem Wert

### Empfohlene Einstellungen

| Strom | Bedeutung | Einsatz |
|-------|-----------|---------|
| **0 A** | Leerlauf (Open Circuit) | V_oc Analyse |
| **5 A** | Teillast | Schwachlicht-Bedingungen |
| **13,14 A** | **I_mpp** (Maximum Power Point) | **Normalbetrieb** ⭐ |
| **13,98 A** | I_sc (Short Circuit) | Kurzschluss-Analyse |

### Beispiel
```
Bei I = 13,14 A (I_mpp):
- String 1: +33,89 V (alle Zellen hell)
- String 2: +33,89 V (alle Zellen hell)
- String 3: +33,89 V (alle Zellen hell)
→ Modul-Spannung: 3 × 33,89 = 101,67 V
→ Leistung: 101,67 V × 13,14 A = 1335 W (aber nur 445W pro String!)

Bei I = 13,14 A mit 1 verschatteter Zelle in String 1:
- String 1: -11,0 V (Bypass aktiviert bei V_br = 22V)
- String 2: +33,89 V (normal)
- String 3: +33,89 V (normal)
→ Modul-Spannung: -11 + 33,89 + 33,89 = 56,78 V
→ Leistungsverlust: -35% !
```

---

## Vergleichstabelle

| Aspekt | Max. Strom (Parameter) | Analyse-Betriebsstrom (Betriebspunkt) |
|--------|------------------------|----------------------------------------|
| **Zweck** | Berechnungsbereich | Analyse-Punkt |
| **Einfluss auf** | I-V Kurven-Darstellung | Spannungsverteilung, Hot-Spots |
| **Typ** | Bereichs-Parameter | Punkt-Parameter |
| **Änderung** | Ändert Kurven-Breite | Ändert analysierten Zustand |
| **Typischer Wert** | 14 A (über I_sc) | 13,14 A (I_mpp) |
| **Anpassung** | Selten | Häufig (für verschiedene Analysen) |

---

## Verwendungs-Szenarien

### Szenario 1: Normale MPP-Analyse
```yaml
Parameter:
  Max. Strom: 14 A  # Vollständige I-V Kurve
  Einstrahlung: 1000 W/m²
  Temperatur: 25°C

Betriebspunkt:
  Analyse-Betriebsstrom: 13,14 A  # I_mpp für Normalzustand

→ Zeigt: Spannungsverteilung bei optimaler Leistung
```

### Szenario 2: Verschattungs-Analyse
```yaml
Parameter:
  Max. Strom: 14 A
  Einstrahlung: 1000 W/m²
  Verschattung: 3 Zellen in String 1

Betriebspunkt:
  Analyse-Betriebsstrom: 10 A  # Reduzierter Strom durch Verschattung

→ Zeigt: Wie Bypass-Dioden bei reduziertem Strom schalten
```

### Szenario 3: Schwachlicht
```yaml
Parameter:
  Max. Strom: 14 A  # Bereich bleibt gleich
  Einstrahlung: 200 W/m²
  Temperatur: 25°C

Betriebspunkt:
  Analyse-Betriebsstrom: 2,8 A  # ~20% von I_sc

→ Zeigt: Verhalten bei geringer Einstrahlung
```

### Szenario 4: Hot-Spot Untersuchung
```yaml
Parameter:
  Max. Strom: 14 A
  Verschattung: 1 Zelle vollständig

Betriebspunkt:
  Analyse-Betriebsstrom: 13,14 A  # I_mpp erzwingen

→ Zeigt: Maximale Hot-Spot Leistung (bis zu 289 W bei V_br=22V!)
```

---

## Technische Details

### Max. Strom für I-V-Kurve

**Code-Verwendung**:
```python
def calculate_iv_curve(module, max_current=14.0):
    currents = np.linspace(0, max_current, 300)
    voltages = []
    powers = []
    
    for I in currents:
        V = module.module_voltage_at_current(I)
        P = V * I
        voltages.append(V)
        powers.append(P)
    
    return currents, voltages, powers
```

**Auswirkung**:
- Zu niedrig (< I_sc): Unvollständige Kurve
- Optimal (≈ I_sc + 10%): Vollständige Darstellung
- Zu hoch (>> I_sc): Verschwendete Rechenzeit

---

### Analyse-Betriebsstrom

**Code-Verwendung**:
```python
def analyze_operating_point(module, current):
    # Berechne Zustand bei diesem Strom
    voltage_map = module.get_cell_voltage_map(current)
    
    # Für jede Zelle:
    for string_idx, string in enumerate(module.strings):
        for cell_idx, cell_voltage in enumerate(voltage_map[string_idx]):
            if cell_voltage < 0:
                # Zelle in Reverse-Bias
                hotspot_power = abs(cell_voltage) * current
                # Zeige Warnung wenn > 10 W
```

**Auswirkung**:
- Direkte Anzeige in Heatmaps
- Basis für Hot-Spot Warnungen
- Bypass-Dioden Status-Anzeige

---

## Best Practices

### ✅ DO:
1. **Max. Strom**: Immer ≥ I_sc (13,98 A) setzen
2. **Analyse-Strom**: Bei I_mpp (13,14 A) starten
3. **Experimente**: Analyse-Strom variieren, Parameter konstant lassen
4. **Szenarien**: Verschiedene Analyse-Ströme für verschiedene Lastfälle testen

### ❌ DON'T:
1. Nicht Max. Strom < I_sc (unvollständige I-V Kurven)
2. Nicht Analyse-Strom > I_sc (physikalisch nicht möglich bei Normal-Betrieb)
3. Nicht beide Parameter verwechseln
4. Nicht Max. Strom für Punkt-Analysen verwenden

---

## Fehlerbehebung

### Problem: "I-V Kurve endet bei 10 A"
**Ursache**: Max. Strom zu niedrig  
**Lösung**: Max. Strom auf 14 A erhöhen

### Problem: "Keine Hot-Spots sichtbar trotz Verschattung"
**Ursache**: Analyse-Betriebsstrom zu niedrig  
**Lösung**: Auf I_mpp (13,14 A) erhöhen

### Problem: "Bypass-Dioden immer aktiv"
**Ursache**: Analyse-Betriebsstrom zu hoch oder Verschattung zu stark  
**Lösung**: Verschattung reduzieren oder Strom senken

---

## Zusammenfassung

| Parameter | Zweck | Empfohlener Wert | Anpassung |
|-----------|-------|------------------|-----------|
| **Max. Strom für I-V-Kurve** | Berechnungsbereich | 14 A | Selten |
| **Analyse-Betriebsstrom** | Untersuchungspunkt | 13,14 A (I_mpp) | Häufig |

**Merksatz**: 
- "Max. Strom" = Wie weit sehe ich auf der I-V Kurve?
- "Analyse-Strom" = Wo schaue ich genau hin?

---

*Letzte Aktualisierung: November 2025*  
*Version: 0.1b mit verbesserter Parameterbenennung*

