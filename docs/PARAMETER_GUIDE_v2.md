# Parameter-Guide v2: Steuerung und Einstellungen

Dieses Dokument erklärt die wichtigsten Parameter und Steuerungselemente in der aktualisierten Anwendung.

---

## 1️⃣ "Max. Strom für I-V-Kurve" (I-V Kennlinien-Seite)

### Location
- **Seite**: I-V Kennlinien
- **Panel**: Parameter
- **ID**: `current-slider` (technisch)

### Zweck
**Automatisch gekoppelt an Einstrahlung!**

Dieser Parameter wird **nicht mehr manuell gesetzt**, sondern berechnet sich automatisch aus der Einstrahlung:

```python
I_max = (G / 1000) × I_sc_STC

wobei:
- G = Aktuelle Einstrahlung [W/m²]
- I_sc_STC = 13,98 A (bei 1000 W/m²)
```

### Beispiele

| Einstrahlung | I_max berechnet | Bedeutung |
|--------------|-----------------|-----------|
| 200 W/m² | 2,80 A | Schwachlicht (Winter, bewölkt) |
| 500 W/m² | 6,99 A | Teillast |
| 800 W/m² | 11,18 A | NOCT-Bedingungen |
| 1000 W/m² | 13,98 A | STC (Standard) |

### Hinweis
⚠️ **Der "Max. Strom"-Slider wurde entfernt**, da Strom physikalisch von der Einstrahlung abhängt!

---

## 2️⃣ "Verschattungsgrad (%)" - **NEUE HAUPTFUNKTION!**

### Location
- **Seite**: Spannungsverteilung
- **Panel**: Betriebspunkt
- **ID**: `operating-current-slider` (behält alte ID für Kompatibilität)

### Zweck
Definiert, **WIE STARK** die im gewählten Szenario definierten Zellen verschattet sind.

### Konzept: Zwei-Stufen-Steuerung

```
Schritt 1: SZENARIO wählen     →  WO wird verschattet? (welche Zellen)
Schritt 2: VERSCHATTUNGSGRAD   →  WIE STARK? (0-100%)
```

### Funktionsweise

```python
# Verschattungsgrad (Slider): 0-100%
shading_intensity = slider_value / 100.0  # → 0.0 bis 1.0

# Auf Zelle anwenden:
Iph_effective = Iph_base × (1 - shading_intensity)

# Beispiel:
# - shading_intensity = 0.0 (0%):   Iph = Iph_base (volle Sonne)
# - shading_intensity = 0.5 (50%):  Iph = 0.5 × Iph_base (halbe Einstrahlung)
# - shading_intensity = 1.0 (100%): Iph ≈ 0 (keine Einstrahlung)
```

### Bedeutung der Werte

| Verschattungsgrad | Effektive Einstrahlung | Physikalisches Beispiel |
|-------------------|------------------------|-------------------------|
| **0%** | 100% (1000 W/m²) | Keine Verschattung, volle Sonne |
| **25%** | 75% (750 W/m²) | Leichter Schatten, kleines Objekt |
| **50%** | 50% (500 W/m²) | Halbe Verschattung, größeres Blatt |
| **75%** | 25% (250 W/m²) | Starke Verschattung, großer Schatten |
| **100%** | ~0% (~0 W/m²) | Vollständige Verschattung, komplette Bedeckung |

### Beispiel-Szenarien

#### Beispiel 1: Blatt auf einzelner Zelle

```
Szenario wählen: "Einzelne verschattete Zelle"
→ Definiert: String 0, Zelle 18 ist betroffen

Verschattungsgrad variieren:
┌─────────────────────┬─────────────┬───────────────────┐
│ Verschattungsgrad   │ Effekt      │ Bypass aktiv?     │
├─────────────────────┼─────────────┼───────────────────┤
│ 0%                  │ Keine       │ Nein              │
│ 25%                 │ Minimal     │ Nein              │
│ 50%                 │ Merklich    │ Wahrscheinlich nein│
│ 75%                 │ Stark       │ Möglich           │
│ 100%                │ Vollständig │ Ja (sehr wahrscheinlich)│
└─────────────────────┴─────────────┴───────────────────┘
```

#### Beispiel 2: Kaminschatten im Tagesverlauf

```
Szenario: "Kaminschatten" (3 Zellen pro String)

Tageszeit simulieren:
┌──────────┬─────────────────┬────────────────┐
│ Zeit     │ Verschattung    │ Effekt         │
├──────────┼─────────────────┼────────────────┤
│ 12:00    │ 0% (Mittag)     │ Minimal        │
│ 14:00    │ 30%             │ Leicht         │
│ 16:00    │ 60%             │ Merklich       │
│ 18:00    │ 90%             │ Stark, Bypass  │
│ 20:00    │ 100% (fast dunkel)│ Kritisch     │
└──────────┴─────────────────┴────────────────┘
```

#### Beispiel 3: Schneelast

```
Szenario: "Teilweise Zellreihe" (6 Zellen)

Schneehöhe simulieren:
┌──────────────┬─────────────┬──────────────────┐
│ Schnee       │ Verschattung│ Erwartung        │
├──────────────┼─────────────┼──────────────────┤
│ Kein Schnee  │ 0%          │ Normale Leistung │
│ Staubschicht │ 20%         │ Leichte Reduktion│
│ Halb bedeckt │ 50%         │ 50% Reduktion    │
│ Fast bedeckt │ 80%         │ Starke Reduktion │
│ Vollschnee   │ 100%        │ Bypass aktiviert │
└──────────────┴─────────────┴──────────────────┘
```

### Automatischer Betriebspunkt (MPP)

**Wichtig**: Der Betriebsstrom wird **automatisch** aus dem Maximum Power Point (MPP) berechnet!

```python
# Automatisch berechnet:
mpp = module.find_mpp()
operating_current = mpp['current']  # Realistischer Betriebspunkt
operating_voltage = mpp['voltage']
operating_power = mpp['power']
```

**Warum MPP?**
- ✅ Realistisch: Module werden mit MPPT (Maximum Power Point Tracking) betrieben
- ✅ Automatisch: Keine manuelle Eingabe nötig
- ✅ Konsistent: Immer der optimale Punkt für den aktuellen Zustand
- ✅ Verständlich: "MPP" ist ein bekanntes Konzept in der PV

### Info-Anzeige

Die Anwendung zeigt automatisch:

```
┌─────────────────────────────────────────────┐
│ Verschattungsgrad: 75%                      │
│ Verschattungsfaktor: 0.75                   │
│ Anzahl verschatteter Zellen: 3 von 108     │
│─────────────────────────────────────────────│
│ Betriebspunkt (automatisch am MPP):        │
│ 12.34 A, 35.67 V, 440.12 W                 │
└─────────────────────────────────────────────┘
```

---

## 3️⃣ Temperatur (-20°C bis +90°C)

### Location
- **Alle Seiten**: Parameter-Panel
- **ID**: `temperature-slider`

### Zweck
Simuliert Temperatureinfluss auf Modulleistung.

### Temperaturbereich (erweitert!)

| Temperatur | Szenario | V_oc Änderung | P_mpp Änderung |
|------------|----------|---------------|----------------|
| **-20°C** | Winter (Alpen, Schnee) | +11% | +19% |
| **0°C** | Winter (Mitteleuropa) | +6% | +14% |
| **25°C** | STC (Standard) | Referenz | Referenz |
| **45°C** | NOCT (Normal) | -5% | -9% |
| **70°C** | Sommer (Flachdach) | -11% | -17% |
| **90°C** | Extrem (Wüste) | -15% | -21% |

### Temperaturkoeffizienten (HJT)

```
β_Voc = -0,926 mV/°C pro Zelle
γ_Pmpp = -0,26 %/K

→ HJT hat 35% besseren Temperaturkoeffizienten als Standard p-Type!
```

---

## 4️⃣ Einstrahlung (200-1200 W/m²)

### Location
- **Alle Seiten**: Parameter-Panel
- **ID**: `irradiance-slider`

### Zweck
Simuliert verschiedene Lichtbedingungen.

### Typische Werte

| Einstrahlung | Bedingung | I_sc | Erwartung |
|--------------|-----------|------|-----------|
| **200 W/m²** | Bewölkt, Winter | 2,80 A | Schwachlicht |
| **500 W/m²** | Teilweise bewölkt | 6,99 A | Teillast |
| **800 W/m²** | NOCT (20°C Ambient) | 11,18 A | Normalzustand |
| **1000 W/m²** | STC (Standard) | 13,98 A | Volllast |
| **1200 W/m²** | Sehr hell, Reflexion | 16,78 A | Überlast |

---

## Zusammenfassung: Was wurde geändert?

### Alte Version ❌

```
Problem 1: "Max. Strom" manuell wählbar
→ Führte zu unrealistischen Kombinationen (z.B. 13 A bei 200 W/m²)

Problem 2: "Betriebsstrom %" unklar
→ Benutzer mussten technischen Wert wählen (% von I_sc?)

Problem 3: Verschattung fix
→ Szenarien hatten feste Verschattungsintensität
```

### Neue Version ✅

```
Lösung 1: Strom automatisch gekoppelt
→ I_max = (G/1000) × I_sc_STC (physikalisch korrekt!)

Lösung 2: "Verschattungsgrad %" intuitiv
→ Benutzer wählt verständlichen Wert (0-100% Verschattung)

Lösung 3: Dynamische Verschattung
→ Szenarien + Verschattungsgrad = flexible Simulation
```

---

## Workflow-Vergleich

### Alt ❌

```
1. Szenario wählen
2. Max. Strom wählen (???)
3. Betriebsstrom % wählen (???)
4. Verwirrung
```

### Neu ✅

```
1. Szenario wählen          → WO verschattet?
2. Verschattungsgrad wählen → WIE STARK verschattet?
3. (Strom automatisch)       → MPP berechnet
4. Ergebnis verstehen!       → Klare Visualisierung
```

---

## Best Practices

### Realistische Simulationen

**Winter-Szenario**:
```yaml
Einstrahlung: 600 W/m²
Temperatur: -10°C
Szenario: "Teilweise Zellreihe" (Schnee)
Verschattungsgrad: 50%
→ Simuliert: Halbe Schneelast bei Wintersonne
```

**Sommer-Szenario**:
```yaml
Einstrahlung: 1000 W/m²
Temperatur: 70°C
Szenario: "Baumzweig"
Verschattungsgrad: 75%
→ Simuliert: Dichtes Laub bei Hochsommer
```

**Extremfall**:
```yaml
Einstrahlung: 1000 W/m²
Temperatur: 25°C
Szenario: "Kompletter String verschattet"
Verschattungsgrad: 100%
→ Simuliert: Worst-Case, 1/3 Modul komplett aus
```

---

## Häufig gestellte Fragen (FAQ)

### Q1: Warum gibt es keinen "Max. Strom"-Slider mehr?

**A**: Der Strom ist physikalisch an die Einstrahlung gekoppelt:
```
I_ph ∝ G (Photostrom proportional zur Einstrahlung)
```
Bei 200 W/m² kann ein Modul physikalisch NICHT 13 A liefern!

### Q2: Was bedeutet "Betriebspunkt am MPP"?

**A**: Der Operating Point wird automatisch am Maximum Power Point berechnet. Das ist der Punkt, an dem das Modul im Realbetrieb (mit MPPT-Regler) arbeitet.

### Q3: Kann ich trotzdem einen anderen Betriebsstrom wählen?

**A**: Nein, nicht direkt. Aber Sie können:
- Einstrahlung ändern → ändert I_sc und damit MPP
- Verschattung ändern → verschiebt MPP
- Temperatur ändern → verschiebt MPP

### Q4: Was ist der Unterschied zwischen Szenario und Verschattungsgrad?

**A**: 
- **Szenario**: Definiert **WO** verschattet wird (geometrisches Muster)
- **Verschattungsgrad**: Definiert **WIE STARK** verschattet wird (Intensität)

### Q5: Wie simuliere ich ein kleines Blatt auf einer Zelle?

**A**:
```
1. Szenario: "Einzelne verschattete Zelle"
2. Verschattungsgrad: 25-50% (je nach Blattgröße)
→ Simuliert partielle Bedeckung
```

---

**Die Steuerung ist jetzt intuitiv, realistisch und physikalisch korrekt!** 🎯

---

*Aktualisiert: November 2025*  
*PV-Modul Verschattungs-Visualisierung v0.2*


