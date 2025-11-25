# Installationsanleitung

## Schritt-für-Schritt Installation

### 1. Python-Version überprüfen

Stellen Sie sicher, dass Python 3.8 oder höher installiert ist:

```bash
python --version
```

Falls Python nicht installiert ist, laden Sie es von [python.org](https://www.python.org/downloads/) herunter.

### 2. Projektverzeichnis vorbereiten

Navigieren Sie zum Projektverzeichnis:

```bash
cd PVmodul_Demo
```

### 3. Virtuelle Umgebung erstellen (empfohlen)

Es wird empfohlen, eine virtuelle Umgebung zu verwenden:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Abhängigkeiten installieren

Installieren Sie alle erforderlichen Pakete:

```bash
pip install -r requirements.txt
```

Dies installiert:
- dash (2.14.2)
- plotly (5.18.0)
- numpy (1.24.3)
- scipy (1.11.4)
- pandas (2.1.4)
- dash-bootstrap-components (1.5.0)

### 5. Installation testen

Führen Sie das Test-Skript aus:

```bash
python test_installation.py
```

Alle Tests sollten mit ✓ bestanden werden.

### 6. Anwendung starten

```bash
python app.py
```

Die Anwendung läuft nun unter: **http://127.0.0.1:8050**

Öffnen Sie diese URL in Ihrem Browser (Chrome, Firefox, oder Edge empfohlen).

## Fehlerbehebung

### Problem: "pip" wird nicht erkannt

**Lösung:**
- Stellen Sie sicher, dass Python korrekt installiert ist
- Fügen Sie Python zum PATH hinzu
- Versuchen Sie `python -m pip install -r requirements.txt` statt `pip install`

### Problem: Installation schlägt bei NumPy/SciPy fehl (Windows)

**Lösung:**
- Installieren Sie [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Oder verwenden Sie vorcompilierte Wheels von [Christoph Gohlke](https://www.lfd.uci.edu/~gohlke/pythonlibs/)

### Problem: Port 8050 bereits belegt

**Lösung:**
Ändern Sie den Port in `config.py`:
```python
APP_CONFIG = {
    'port': 8051,  # Oder einen anderen freien Port
    ...
}
```

### Problem: ModuleNotFoundError nach Installation

**Lösung:**
- Stellen Sie sicher, dass die virtuelle Umgebung aktiviert ist
- Installieren Sie die Pakete erneut: `pip install --upgrade -r requirements.txt`

## Systemanforderungen

**Minimal:**
- Python 3.8+
- 4 GB RAM
- Moderner Browser (Chrome 90+, Firefox 88+, Edge 90+)

**Empfohlen:**
- Python 3.10+
- 8 GB RAM
- Chrome Browser für beste Performance
- Bildschirmauflösung: 1920x1080 oder höher

## Performance-Optimierung

Für bessere Performance bei älteren Computern:

1. Reduzieren Sie die Anzahl der Berechnungspunkte in `config.py`:
```python
VIZ_PARAMS = {
    'voltage_points': 200,  # Standard: 500
    ...
}
```

2. Deaktivieren Sie Debug-Modus in `config.py`:
```python
APP_CONFIG = {
    'debug': False,
    ...
}
```

## Update-Anleitung

Bei neuen Versionen:

```bash
# Virtuelle Umgebung aktivieren
source venv/bin/activate  # oder venv\Scripts\activate (Windows)

# Abhängigkeiten aktualisieren
pip install --upgrade -r requirements.txt

# Testen
python test_installation.py

# Starten
python app.py
```

## Deinstallation

```bash
# Virtuelle Umgebung deaktivieren
deactivate

# Projektverzeichnis löschen
cd ..
rm -rf PVmodul_Demo  # oder manuell löschen
```

## Support

Bei Problemen:
1. Überprüfen Sie die Python-Version: `python --version`
2. Überprüfen Sie installierte Pakete: `pip list`
3. Führen Sie Test-Skript aus: `python test_installation.py`
4. Dokumentieren Sie Fehlermeldungen für Support-Anfragen

---

**Viel Erfolg mit der PV Modul Verschattungs-Visualisierung!** 🌞⚡

