# Verschattungsgrad-Steuerung - Neue Funktion

## Problem (vorher)

**❌ Verwirrend**: "Betriebspunkt % von I_sc bei aktueller Einstrahlung"
- Warum sollte ein Benutzer einen Betriebspunkt in % von I_sc wählen?
- Nicht intuitiv, was dieser Wert bewirkt
- Szenarien definierten WO verschattet wird, aber nicht WIE STARK

## Lösung (jetzt)

**✅ Intuitiv**: "Verschattungsgrad (%)"
- Definiert, wie stark die im Szenario ausgewählten Zellen verschattet sind
- 0% = keine Verschattung (volle Sonne)
- 50% = halbe Verschattung (z.B. Blatt bedeckt Hälfte der Zelle)
- 100% = vollständige Verschattung (komplette Bedeckung)

---

## Konzept

### Zwei-Stufen-Steuerung:

```
1. SZENARIO wählen    →  Definiert WO verschattet wird (welche Zellen)
2. VERSCHATTUNGSGRAD  →  Definiert WIE STARK verschattet wird (0-100%)
```

### Beispiel: "Einzelne verschattete Zelle"

| Verschattungsgrad | Physikalische Bedeutung | Beispiel |
|-------------------|-------------------------|----------|
| **0%** | Keine Verschattung | Zelle voll belichtet, 1000 W/m² |
| **25%** | Leichte Verschattung | Kleiner Schatten, 750 W/m² |
| **50%** | Halbe Verschattung | Hälfte bedeckt, 500 W/m² |
| **75%** | Starke Verschattung | Großer Schatten, 250 W/m² |
| **100%** | Vollständige Verschattung | Komplett bedeckt, ~0 W/m² |

---

## Implementierung

### 1. Szenarien definieren WO

**`data/scenarios.json`**:
```json
{
  "id": "single_cell",
  "name": "Einzelne verschattete Zelle",
  "shading_pattern": {
    "string_0": [18],  ← Diese Zelle wird verschattet
    "string_1": [],
    "string_2": []
  },
  "shading_intensity": 1.0  ← Standard (wird durch Slider überschrieben)
}
```

### 2. Slider definiert WIE STARK

**UI-Element** (`app_components/layouts/voltage_distribution.py`):
```python
html.Label("Verschattungsgrad (%):"),
html.Small([
    "Wie stark sind die im Szenario definierten Zellen verschattet?",
    html.Br(),
    "0% = volle Sonne | 50% = halbe Bedeckung | 100% = vollständig verschattet"
]),
dcc.Slider(
    id='operating-current-slider',
    min=0,
    max=100,
    step=5,
    value=100,  # Default: vollständige Verschattung
    marks={0: '0%', 25: '25%', 50: '50%', 75: '75%', 100: '100%'}
)
```

### 3. Dynamische Anwendung

**`utils.py`** - Erweiterte Funktion:
```python
def convert_scenario_to_shading_config(scenario, intensity_override=None):
    """
    Convert scenario to shading configuration
    
    Parameters:
    -----------
    scenario : dict
        Defines WHICH cells are shaded
    intensity_override : float or None
        If provided, overrides scenario's intensity (0.0-1.0)
        Allows dynamic control of HOW MUCH cells are shaded
    """
    shading_pattern = scenario['shading_pattern']
    
    # Use override if provided (from slider)
    if intensity_override is not None:
        shading_intensity = intensity_override
    else:
        shading_intensity = scenario.get('shading_intensity', 1.0)
    
    # Apply intensity to all specified cells
    config = {}
    for string_key, cell_list in shading_pattern.items():
        cell_dict = {cell_idx: shading_intensity for cell_idx in cell_list}
        config[string_key] = cell_dict
    
    return config
```

### 4. Callback-Integration

**`app.py`** - Callback:
```python
@app.callback(...)
def update_voltage_distribution(scenario_id, irradiance, temperature, 
                                shading_percent, display_options):
    # Convert slider % to intensity factor
    shading_intensity = shading_percent / 100.0  # 0-100% → 0.0-1.0
    
    # Apply to scenario
    scenario = get_scenario_by_id(scenario_id)
    shading_config = convert_scenario_to_shading_config(
        scenario, 
        intensity_override=shading_intensity  # Override!
    )
    
    # Create module with dynamic shading
    module = PVModule(
        irradiance=irradiance,
        temperature=temperature,
        shading_config=shading_config
    )
    
    # Calculate operating point automatically from MPP
    mpp = module.find_mpp()
    current = mpp['current']  # Realistic operating point!
    
    ...
```

---

## Physikalische Bedeutung

### Verschattungsfaktor (shading_factor)

```python
# In SolarCell class:
Iph = Iph_base × (1 - shading_factor)

wobei:
- Iph_base: Photostrom bei voller Einstrahlung
- shading_factor: 0.0 (keine Verschattung) bis 1.0 (volle Verschattung)
```

### Effekt auf Zellstrom:

| shading_factor | Iph | Effekt |
|----------------|-----|--------|
| 0.0 | 100% | Volle Einstrahlung |
| 0.25 | 75% | Leichte Verschattung |
| 0.50 | 50% | Halbe Einstrahlung |
| 0.75 | 25% | Starke Verschattung |
| 1.0 | ~0% | Keine Einstrahlung |

### String-Verhalten:

```
Bei 1 verschatteter Zelle im String:
- Verschattungsgrad 100%:
  → Zelle erzeugt keinen Strom
  → String-Strom wird begrenzt
  → Zelle geht in Reverse-Bias
  → Bypass-Diode kann aktivieren

- Verschattungsgrad 50%:
  → Zelle erzeugt halben Strom
  → String-Strom leicht reduziert
  → Zelle bleibt evtl. in Forward-Bias
  → Bypass-Diode bleibt aus
```

---

## Anwendungsfälle

### 1. Blatt auf Zelle

```
Szenario: "Einzelne verschattete Zelle"

Verschattungsgrad variieren:
- 0%:   Blatt weggeblasen → volle Leistung
- 25%:  Kleines Blatt → leichte Reduktion
- 50%:  Größeres Blatt → merkliche Reduktion
- 75%:  Großes Blatt → starke Reduktion
- 100%: Komplett bedeckt → Bypass aktiviert?
```

### 2. Kaminschatten

```
Szenario: "Kaminschatten"

Tageszeit simulieren:
- 0%:   Mittags, Schatten minimal
- 30%:  Nachmittag, Schatten wächst
- 60%:  Spätnachmittag, deutlicher Schatten
- 90%:  Abend, fast voller Schatten
```

### 3. Baumzweig

```
Szenario: "Baumzweig"

Jahreszeit simulieren:
- 0%:   Winter, Baum kahl → keine Verschattung
- 25%:  Frühling, erste Blätter
- 50%:  Frühjahr, teilweise belaubt
- 75%:  Sommer, dichtes Laub
- 90%:  Hochsommer, maximales Laub
```

### 4. Schneeschicht

```
Szenario: "Teilweise Zellreihe"

Schneehöhe simulieren:
- 0%:   Kein Schnee
- 20%:  Leichter Schneestaub
- 50%:  Halbe Zellen bedeckt
- 80%:  Fast vollständig bedeckt
- 100%: Komplett verschneit
```

---

## Automatischer Betriebspunkt (MPP)

**Alte Lösung** ❌:
- Benutzer musste Betriebsstrom manuell wählen
- % von I_sc - was bedeutet das?
- Unrealistisch, nicht intuitiv

**Neue Lösung** ✅:
```python
# Betriebspunkt wird AUTOMATISCH am MPP berechnet
mpp = module.find_mpp()
current = mpp['current']  # Realistischer Betriebspunkt!
```

### Warum MPP?

1. **Realistisch**: Module werden mit MPPT betrieben
2. **Automatisch**: Keine Benutzereingabe nötig
3. **Konsistent**: Immer der optimale Punkt für den Zustand
4. **Verständlich**: "Maximum Power Point" ist bekannt

### Info-Anzeige:

```
Verschattungsgrad: 75%
Verschattungsfaktor: 0.75 (0 = keine, 1 = volle Verschattung)
Anzahl verschatteter Zellen: 3 von 108
────────────────────────────────────
Betriebspunkt (automatisch am MPP): 
12.34 A, 35.67 V, 440.12 W
```

---

## Vergleich: Alt vs. Neu

| Aspekt | Vorher ❌ | Nachher ✅ |
|--------|----------|-----------|
| **Slider-Name** | "Betriebspunkt % von I_sc" | "Verschattungsgrad %" |
| **Bedeutung** | Unklar, technisch | Klar, intuitiv |
| **Funktion** | Wählt Analysestrom | Definiert Verschattungsstärke |
| **Betriebspunkt** | Manuell gewählt | Automatisch (MPP) |
| **Anwendung** | Verwirrend | Natürlich |
| **Beispiel** | "94% von I_sc" - Was? | "50% verschattet" - Klar! |

---

## Benutzer-Workflow

### Alt ❌:

```
1. Szenario wählen
2. Betriebsstrom in % von I_sc wählen (???)
3. Verwirrung
```

### Neu ✅:

```
1. Szenario wählen     → "Einzelne verschattete Zelle"
2. Verschattungsgrad   → 50% (halbes Blatt auf Zelle)
3. Ergebnis verstehen  → Sehen, wie sich partielle Verschattung auswirkt!
```

---

## Test-Szenarien

### Test 1: Progressive Verschattung

```
Szenario: "Einzelne verschattete Zelle"
Einstrahlung: 1000 W/m²
Temperatur: 25°C

Verschattungsgrad durchfahren:
0%   → Beobachten: Alle Zellen grün, volle Leistung
25%  → Beobachten: Eine Zelle leicht dunkler, minimale Reduktion
50%  → Beobachten: Eine Zelle deutlich dunkler, merkliche Reduktion
75%  → Beobachten: Eine Zelle sehr dunkel, String-Spannung sinkt
100% → Beobachten: Eine Zelle schwarz, Bypass-Diode aktiviert?
```

### Test 2: Kamin-Schatten im Tagesverlauf

```
Szenario: "Kaminschatten"
Einstrahlung: 1000 W/m²

Tageszeit simulieren:
0% (Mittag)    → Minimaler Effekt
30% (14:00)    → Leichte Reduktion
60% (16:00)    → Merkliche Reduktion
90% (18:00)    → Starke Reduktion, Bypass-Effekte
```

### Test 3: Schneelast

```
Szenario: "Teilweise Zellreihe"

Schneehöhe simulieren:
0%   → Kein Schnee
20%  → Leichter Schneestaub → minimaler Effekt
50%  → Halbe Zellen bedeckt → deutliche Reduktion
80%  → Fast bedeckt → starke Reduktion
100% → Vollständig verschneit → Bypass aktiviert
```

---

## Code-Änderungen - Zusammenfassung

### Geänderte Dateien:

1. **`utils.py`**
   - `convert_scenario_to_shading_config()` erweitert um `intensity_override`

2. **`app_components/layouts/voltage_distribution.py`**
   - Slider umbenannt: "Verschattungsgrad (%)"
   - Neue Beschreibung und Hinweise
   - Output-ID: `shading-intensity-info` (statt `current-info`)

3. **`app.py`**
   - Callback `update_voltage_distribution` angepasst
   - Slider-Wert als `shading_percent` interpretiert
   - Automatische MPP-Berechnung für Betriebspunkt
   - Neue Info-Anzeige für Verschattungsgrad und MPP

---

## Zusammenfassung

### Was wurde erreicht?

✅ **Intuitive Bedienung**: "Verschattungsgrad" ist sofort verständlich
✅ **Realistische Szenarien**: Blatt, Schatten, Schnee simulierbar
✅ **Automatischer Betriebspunkt**: MPP wird automatisch berechnet
✅ **Flexible Steuerung**: Von 0% (keine) bis 100% (volle) Verschattung
✅ **Physikalisch korrekt**: shading_factor wird auf Zell-Photostrom angewendet

### Warum ist das besser?

| Kriterium | Verbesserung |
|-----------|--------------|
| **Verständlichkeit** | +++ (von "% von I_sc" zu "Verschattungsgrad") |
| **Realismus** | +++ (MPP statt manueller Strompunkt) |
| **Flexibilität** | +++ (variable Verschattung statt fest) |
| **Nutzererfahrung** | +++ (intuitiv statt verwirrend) |

---

**Die Steuerung ist jetzt benutzerfreundlich und physikalisch sinnvoll!** 🎯

---

*Implementiert: November 2025*  
*PV-Modul Verschattungs-Visualisierung v0.2*

