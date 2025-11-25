# PV Modul Verschattungs-Visualisierung

Eine umfassende, interaktive Web-Applikation zur Visualisierung des elektrischen Verhaltens von Photovoltaikmodulen unter Verschattungsbedingungen mit detaillierter Halbleiterphysik-Analyse.

## 🌟 Hauptfunktionen

### 1. **I-V Kennlinien Analyse**
- Interaktive I-V und P-V Kurven
- Dynamische Parameter-Anpassung (Einstrahlung, Temperatur)
- MPP-Tracking und Verlustanalyse
- Vergleich mit unverschattetem Referenzmodul

### 2. **Spannungsverteilung & Hot-Spot Analyse**
- Detaillierter Modulschaltplan mit Echtzeit-Spannungswerten
- Farbcodierte Voltage-Heatmaps
- Leistungsdissipations-Visualisierung
- Hot-Spot Identifikation und Warnsystem

### 3. **Bypass-Dioden Verhalten**
- Analyse der Bypass-Aktivierungsschwellen
- String-Spannungs-Monitoring
- Kritische Zellanzahl-Bestimmung
- Szenario-Vergleiche für Bypass-Optimierung

### 4. **Halbleiterphysik Deep-Dive**
- **2D Visualisierungen:**
  - Elektrisches Feldprofil im pn-Übergang
  - Bänderdiagramm unter Reverse-Bias
  - Sperrschichtweite vs. Spannung
  - Temperaturabhängigkeit der Breakdown-Spannung

- **3D Visualisierungen:**
  - Interaktives 3D pn-Übergangs-Modell
  - Avalanche-Durchbruch Animation
  - Ladungsträger-Multiplikation (Lawineneffekt)

### 5. **Szenario-Bibliothek**
- 8+ vordefinierte Verschattungsszenarien
- Side-by-Side Vergleiche
- Detaillierte Verlustanalyse
- Exportierbare Ergebnisse

## 📋 Voraussetzungen

- Python 3.8 oder höher
- pip (Python Package Manager)

## 🚀 Installation

1. **Repository klonen oder Dateien herunterladen**

2. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Anwendung starten

```bash
python app.py
```

Die Anwendung wird unter `http://127.0.0.1:8050` verfügbar sein.

Öffnen Sie Ihren Browser und navigieren Sie zu dieser Adresse.

## 🏗️ Projektstruktur

```
PVmodul_Demo/
├── app.py                          # Haupt-Dash-Anwendung mit Callbacks
├── config.py                       # Konfiguration und physikalische Parameter
├── requirements.txt                # Python-Abhängigkeiten
├── utils.py                        # Hilfsfunktionen
│
├── physics/                        # Physik-Engine
│   ├── __init__.py
│   ├── cell_model.py              # Einzelzellen-Modell mit Breakdown
│   ├── string_model.py            # Zellstring mit Bypass-Logik
│   ├── module_model.py            # Komplettes 108-Zellen-Modul
│   └── semiconductor_physics.py    # Halbleiterphysik (Avalanche, etc.)
│
├── visualizations/                 # Visualisierungsmodule
│   ├── __init__.py
│   ├── iv_plotter.py              # I-V und P-V Kurven
│   ├── circuit_visualizer.py      # Schaltplan-Darstellung
│   ├── heatmap_generator.py       # Heatmaps (Spannung, Leistung, Temp.)
│   └── semiconductor_3d.py        # 3D Halbleiter-Visualisierungen
│
├── app_components/                 # Dash UI-Komponenten
│   ├── layouts/                   # Seiten-Layouts
│   │   ├── overview.py
│   │   ├── iv_curves.py
│   │   ├── voltage_distribution.py
│   │   ├── bypass_diode.py
│   │   ├── breakdown_physics.py
│   │   └── scenarios.py
│   ├── components/                # Wiederverwendbare Komponenten
│   │   └── controls.py
│   └── callbacks/                 # (in app.py integriert)
│
├── data/
│   └── scenarios.json             # Vordefinierte Verschattungsszenarien
│
└── assets/
    └── style.css                  # Custom CSS Styling
```

## 📊 Verwendete Modelle

### Elektrisches Zellmodell
- **Single-Diode Model** mit Temperaturabhängigkeit
- Reverse-Bias Charakteristik mit Shunt-Widerstand
- **Avalanche-Breakdown-Modell** (10-20V Bereich)
- Hot-Spot Leistungsberechnung

### Modulkonfiguration
- **108 Halbzellen** (typisches Modul-Design)
- **3 Substrings** à 36 Zellen
- **3 Schottky-Bypass-Dioden** (V_f ≈ 0.4V)
- Realistische Parameter bei STC (1000 W/m², 25°C)

### Halbleiterphysik
- **pn-Übergang** mit Dotierungskonzentrationen
- **Sperrschichtweite** berechnet aus Poisson-Gleichung
- **Elektrisches Feld** mit Maximalfeldstärke
- **Impact-Ionization** (Chynoweth's Law)
- **Avalanche-Multiplikation** mit exponentieller Verstärkung

## 🎓 Physikalische Hintergründe

### Reverse-Bias Breakdown

Wenn eine verschattete Solarzelle in einem Serienstring betrieben wird:

1. **Stromzwang:** Die verschattete Zelle kann keinen Photostrom generieren, muss aber den String-Strom führen
2. **Reverse-Bias:** Die Zelle wird in Sperrrichtung betrieben (negative Spannung)
3. **Leistungsdissipation:** P = |V_reverse| × I_string → Hot-Spot
4. **Avalanche-Durchbruch:** Bei V < -V_br (~12V) tritt Stoßionisation auf

### Bypass-Dioden-Schutz

- Leiten bei V_substring < -V_f (≈ -0.4V für Schottky)
- Ermöglichen Stromumleitung um verschattete Bereiche
- Verhindern übermäßige Hot-Spots
- Reduzieren Leistungsverluste

## 🔧 Anpassung

### Parameter ändern

Bearbeiten Sie `config.py` um physikalische Parameter anzupassen:

```python
CELL_PARAMS = {
    'Iph_ref': 10.0,      # Photostrom bei 1000 W/m²
    'Vbr_typical': 12,    # Typische Breakdown-Spannung
    # ... weitere Parameter
}
```

### Eigene Szenarien hinzufügen

Bearbeiten Sie `data/scenarios.json`:

```json
{
  "id": "mein_szenario",
  "name": "Mein Verschattungsszenario",
  "description": "Beschreibung des Szenarios",
  "shading_pattern": {
    "string_0": [0, 1, 2],
    "string_1": [],
    "string_2": []
  },
  "shading_intensity": 1.0
}
```

## 📝 Technische Details

### Technologie-Stack
- **Backend:** Python 3.8+
- **Web-Framework:** Dash 2.14+
- **Visualisierung:** Plotly 5.18+
- **Wissenschaftlich:** NumPy, SciPy
- **UI-Framework:** Dash Bootstrap Components

### Performance
- Echtzeit-Updates (<100ms)
- Bis zu 500 Punkte pro I-V-Kurve
- Parallele String-Berechnungen
- Optimierte numerische Solver (SciPy)

## 🐛 Fehlerbehebung

**Problem:** Modul startet nicht
- Lösung: Überprüfen Sie, ob alle Abhängigkeiten installiert sind
- Lösung: Stellen Sie sicher, dass Port 8050 nicht belegt ist

**Problem:** Grafiken werden nicht angezeigt
- Lösung: Browser-Cache leeren und Seite neu laden
- Lösung: JavaScript im Browser aktivieren

**Problem:** Langsame Performance
- Lösung: Reduzieren Sie die Anzahl der Punkte in I-V-Kurven (config.py)
- Lösung: Schließen Sie andere Browser-Tabs

## 📚 Referenzen

Die Implementierung basiert auf etablierten Modellen aus der PV-Forschung:

1. Single-Diode Solarzellen-Modell
2. Avalanche-Breakdown in Silizium (Chynoweth's Law)
3. Bypass-Dioden in PV-Modulen (Schottky-Charakteristik)
4. Hot-Spot Formation bei Teilverschattung

## 🤝 Beiträge

Dieses Projekt wurde entwickelt als interaktives Lern- und Analysewerkzeug für technisches Personal im PV-Bereich.

## 📄 Lizenz

Dieses Projekt ist für Bildungs- und Forschungszwecke verfügbar.

## ⚡ Schnellstart-Beispiel

```python
# Beispiel: Eigenes Modul erstellen und analysieren
from physics import PVModule

# Modul mit Verschattung erstellen
shading_config = {
    'string_0': {5: 1.0, 6: 1.0},  # Zwei Zellen voll verschattet
    'string_1': {},
    'string_2': {}
}

module = PVModule(
    irradiance=1000,
    temperature=25,
    shading_config=shading_config
)

# I-V Kurve generieren
iv_data = module.iv_curve()
print(f"Voc: {iv_data['voltages'][-1]:.2f} V")
print(f"Isc: {iv_data['currents'][0]:.2f} A")

# MPP finden
mpp = module.find_mpp()
print(f"MPP: {mpp['power']:.2f} W at {mpp['voltage']:.2f} V")

# Hot-Spots analysieren
hotspot_analysis = module.analyze_hotspots(mpp['current'])
print(f"Hot-Spots: {hotspot_analysis['num_hotspots']}")
print(f"Gesamt-Dissipation: {hotspot_analysis['total_hotspot_power']:.2f} W")
```

## 📞 Support

Bei Fragen oder Problemen, bitte dokumentieren Sie:
- Python-Version
- Betriebssystem
- Fehlermeldung (falls vorhanden)
- Schritte zur Reproduktion

---

**Entwickelt für die interaktive Visualisierung von PV-Modul-Verschattungseffekten** 🌞⚡

