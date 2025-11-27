# Schnellstart-Anleitung

## In 5 Minuten zur laufenden Anwendung

### Schritt 1: Installation (einmalig)
```bash
pip install -r requirements.txt
```

### Schritt 2: Starten
```bash
python app.py
```

### Schritt 3: Browser öffnen
Öffnen Sie: **http://127.0.0.1:8050**

---

## Erste Schritte in der Anwendung

### 1. Übersichtsseite
- Einführung in die Funktionen
- Theoretische Grundlagen
- Navigation zu den Hauptfunktionen

### 2. I-V Kennlinien
**Pfad:** Navigation → "I-V Kennlinien"

**Was tun:**
1. Wählen Sie ein Szenario aus dem Dropdown (z.B. "Einzelne Zelle")
2. Passen Sie Einstrahlung und Temperatur mit den Slidern an
3. Beobachten Sie die I-V und Leistungskurven
4. Vergleichen Sie mit der Referenz (unverschattet)

**Was Sie sehen:**
- I-V Kennlinie mit MPP-Markierung
- Leistungskurve
- Verlustanalyse
- Bypass-Status

### 3. Spannungsverteilung
**Pfad:** Navigation → "Spannungsverteilung"

**Was tun:**
1. Wählen Sie ein Verschattungsszenario
2. Stellen Sie den Betriebsstrom ein
3. Analysieren Sie die Spannungsverteilung

**Was Sie sehen:**
- Farbcodierter Schaltplan (rot = Reverse-Bias)
- Spannungs-Heatmap
- Leistungsdissipation-Heatmap
- Hot-Spot Warnungen

### 4. Bypass-Analyse
**Pfad:** Navigation → "Bypass-Analyse"

**Was tun:**
1. Variieren Sie die Anzahl verschatteter Zellen
2. Ändern Sie die Verschattungsintensität
3. Beobachten Sie, wann der Bypass aktiviert

**Was Sie sehen:**
- String-Spannungen (farbcodiert)
- Aktivierungsschwelle (-0.4V Linie)
- Kritische Zellanzahl
- Bypass-Status-Anzeige

### 5. Halbleiterphysik
**Pfad:** Navigation → "Halbleiterphysik"

**Was tun:**
1. Stellen Sie die Reverse-Spannung ein (-20V bis 0V)
2. Wechseln Sie zwischen den Tabs:
   - **E-Feld Profil:** Feldverteilung im pn-Übergang
   - **Bänderdiagramm:** Energiebänder unter Reverse-Bias
   - **3D pn-Übergang:** Interaktive 3D-Darstellung
   - **Avalanche Animation:** Lawinendurchbruch (bei V < -10V)

**Was Sie sehen:**
- Physikalische Eigenschaften (Sperrschichtweite, E-Feld, etc.)
- 2D und 3D Visualisierungen
- Temperaturabhängigkeit
- Multiplikationsfaktor

### 6. Szenarien-Vergleich
**Pfad:** Navigation → "Szenarien"

**Was tun:**
1. Wählen Sie 2-3 Szenarien zum Vergleich
2. Klicken Sie "Vergleich aktualisieren"
3. Analysieren Sie die Unterschiede

**Was Sie sehen:**
- Überlagerte I-V Kurven
- Leistungsvergleich
- Vergleichstabelle mit MPP-Daten
- Hot-Spot Vergleich

---

## Vordefinierte Szenarien

### Einfache Szenarien (zum Lernen)
1. **Keine Verschattung:** Referenzzustand
2. **Einzelne Zelle:** Eine Zelle verschattet - Bypass AUS
3. **Zwei Zellen:** Zwei Zellen - nahe Bypass-Schwelle

### Kritische Szenarien (Bypass-Analyse)
4. **Drei Zellen:** Kritisch - Bypass wahrscheinlich EIN
5. **Kaminschatten:** Schmaler Schatten über alle Strings
6. **Baumzweig:** Unregelmäßige Verschattung

### Extreme Szenarien (maximale Verluste)
7. **Teilweise Reihe:** 6 Zellen in einem String
8. **Kompletter String:** Alle 36 Zellen eines Strings
9. **Stufenverschattung:** Graduell über Strings

---

## Wichtige Parameter verstehen

### Einstrahlung (W/m²)
- **1000:** Standardtestbedingungen (STC)
- **800:** Bewölkter Tag
- **400:** Stark bewölkt
- **200:** Sehr schwache Beleuchtung

### Temperatur (°C)
- **25:** STC-Bedingung
- **45:** Typisch im Sommer
- **65:** Heiße Module im Hochsommer
- **85:** Maximum (Extrembedingungen)

### Betriebsstrom (A)
- **0:** Leerlauf (V = Voc)
- **~5-6:** MPP-Bereich (typisch)
- **~10:** Kurzschluss (I = Isc)

---

## Interpretation der Ergebnisse

### I-V Kurve
- **Horizontaler Teil:** Stromquelle-Verhalten (konstanter Strom)
- **Knie:** MPP-Region (optimaler Betriebspunkt)
- **Steiler Abfall:** Spannungsquelle-Verhalten (konstante Spannung)
- **Stufen in Kurve:** Bypass-Dioden schalten

### Farben in Spannungsverteilung
- **🟢 Grün:** Positive Spannung (normal)
- **🟡 Gelb:** Nahe 0V
- **🔴 Rot:** Negative Spannung (Reverse-Bias, Hot-Spot!)

### Bypass-Status
- **🟢 AUS:** String arbeitet normal
- **🔴 EIN:** String wird umgangen (starke Verschattung)

### Hot-Spots
- **< 5W:** Unkritisch
- **5-20W:** Moderat, Temperaturerhöhung
- **> 20W:** Kritisch, Zellschädigung möglich!

---

## Tipps für effiziente Nutzung

1. **Beginnen Sie einfach:** Starten Sie mit "Keine Verschattung", dann "Einzelne Zelle"
2. **Vergleichen Sie immer:** Nutzen Sie die Referenzkurve in I-V Ansicht
3. **Experimentieren Sie:** Variieren Sie Parameter und beobachten Sie Effekte
4. **Bypass-Schwelle:** Testen Sie verschiedene Zellanzahlen in Bypass-Analyse
5. **Physik verstehen:** Nutzen Sie Halbleiterphysik-Seite für Tiefenverständnis

---

## Häufige Fragen (FAQ)

**Q: Warum ist die Leistung bei Verschattung so stark reduziert?**
A: Nicht nur die direkte Reduktion, sondern auch Bypass-Aktivierung und Spannungseinbrüche führen zu überproportionalen Verlusten.

**Q: Ab wann schaltet der Bypass?**
A: Bei etwa 2-3 stark verschatteten Zellen in einem String (abhängig von Intensität und Strom).

**Q: Was ist die Breakdown-Spannung?**
A: ~12V pro Zelle - darüber tritt Avalanche-Durchbruch auf (siehe Halbleiterphysik).

**Q: Sind Hot-Spots gefährlich?**
A: Ja, bei Leistungen > 20W kann es zu dauerhafter Zellschädigung kommen.

**Q: Warum Schottky-Dioden als Bypass?**
A: Niedrige Durchlassspannung (0.4V vs. 0.7V) und schnelles Schaltverhalten.

---

## Tastenkombinationen (in Graphen)

- **Zoom:** Mausrad oder Bereich aufziehen
- **Pan:** Klicken und Ziehen (mit Pan-Tool)
- **Reset:** Doppelklick auf Graph
- **Download:** Kamera-Symbol oben rechts
- **Hover:** Detailwerte beim Überfahren

---

## Nächste Schritte

Nach dem Schnellstart:
1. Lesen Sie die vollständige Dokumentation: `README.md`
2. Erkunden Sie eigene Szenarien: Bearbeiten Sie `data/scenarios.json`
3. Passen Sie Parameter an: `config.py`
4. Experimentieren Sie mit dem Code: `test_installation.py`

---

**Viel Spaß beim Erkunden der PV-Verschattungseffekte!** 🌞⚡

Bei Fragen oder Problemen: Siehe `INSTALL.md` oder `README.md`


