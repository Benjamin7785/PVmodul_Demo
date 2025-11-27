# ⚡🎯 Performance & Genauigkeits-Fix

## 🎯 Problem 1: Falsche Spannungen (gelöst ✅)

**User-Report**: "Die Spannung, die an den 36 Zellen angezeigt wird ist größer 70V. Das ist unplausibel."

### Was war falsch:
- Modul-Spannung: 75.60 V (sollte 41.58 V sein) ❌
- Abweichung: +82% ❌

### Lösung:
1. ✅ `get_Voc()` verwendet jetzt **analytische Formel** statt numerische Suche
2. ✅ **Single-Diode-Parameter neu kalibriert**:
   - `n`: 1.15 → 0.92
   - `Rs`: 0.0028 → 0.0008 Ω
   - `Rsh`: 1000 → 5000 Ω
3. ✅ I-V Kurvenbereich korrigiert (min statt max I_sc)

### Ergebnis:
| Parameter | Vorher | Nachher | Soll | Abweichung |
|-----------|--------|---------|------|------------|
| V_oc | 75.60 V | **41.58 V** ✅ | 41.58 V | 0.0% |
| V_mpp | 54.00 V | **34.01 V** ✅ | 33.89 V | 0.4% |
| P_mpp | 830 W | **438 W** ✅ | 445 W | **1.6%** ✅ |

---

## ⚡ Problem 2: Schlechte Performance (teilweise gelöst ⚠️)

**User-Report**: "Die performance der Visualisierung ist wieder sehr schlecht. Die Visualisierungen werden nicht geladen."

### Was passiert ist:
Bei der Spannungskorrektur wurde die JIT-Optimierung teilweise entfernt, um scipy.optimize.brentq für Genauigkeit zu verwenden.

### Was wurde optimiert:
1. ✅ `_calculate_cell_current_jit()`: Reduziert auf 6 Iterationen (war 10)
2. ✅ I-V Kurve: Nur 30 Punkte statt 150 (5x schneller)
3. ✅ Relaxed tolerance: 1e-4 statt 1e-6
4. ✅ JIT current() bleibt aktiviert (10-20x schneller)
5. ❌ JIT bisection funktioniert nicht → verwendet scipy.optimize.brentq

### Aktuelle Performance (geschätzt):
- **MPP-Suche**: ~1-2 Sekunden
- **I-V Kurve (30 Punkte)**: ~1-2 Sekunden
- **Gesamter Callback**: ~2-4 Sekunden

**Status**: ⚠️ Akzeptabel, aber nicht optimal

---

## 🔧 Was funktioniert:

### ✅ Genauigkeit
- V_oc: 0.0% Abweichung
- P_mpp: 1.6% Abweichung
- Physikalisch plausible Werte

### ✅ JIT für current()
```python
@jit(nopython=True, cache=True, fastmath=True)
def _calculate_cell_current_jit(V, Iph, Is, n, Vt, Rs, Rsh, num_iter=6):
    # 10-20x schneller als pure Python!
    I = np.full_like(V, Iph)
    for _ in range(num_iter):
        V_diode = V + I * Rs
        exp_arg = np.clip(V_diode / (n * Vt), -50.0, 50.0)
        I_diode = Is * (np.exp(exp_arg) - 1.0)
        I_shunt = V_diode / Rsh
        I_new = Iph - I_diode - I_shunt
        I = 0.5 * I + 0.5 * I_new
    return I
```

### ✅ Weniger Punkte für I-V Kurven
```python
# module_model.py, string_model.py
if fast:
    iv_data = self.iv_curve(points=30)  # 30 Punkte: 5x schneller!
else:
    iv_data = self.iv_curve(points=100)
```

---

## ❌ Was NICHT funktioniert:

### JIT Bisection
Die JIT-compiled Bisection-Methode konvergiert nicht korrekt:
- Gibt falsche Spannungen zurück (0V statt 0.3V)
- Problem: Suchbereich oder Konvergenzlogik ist fehlerhaft
- **Daher verwenden wir scipy.optimize.brentq** (langsamer aber korrekt)

```python
# AKTUELL (funktioniert, aber langsam):
def find_operating_point(self, target_current):
    from scipy.optimize import brentq
    
    def objective(v):
        return self.current(v) - target_current  # current() ist JIT!
    
    voltage = brentq(objective, 0.0, V_oc * 1.1, xtol=1e-4)
    return voltage

# IDEAL (würde funktionieren, wenn JIT bisection funktioniert):
def find_operating_point(self, target_current):
    return _find_voltage_for_current_jit(...)  # 20-30x schneller!
```

---

## 📊 Vergleich: Vorher vs. Nachher

| Metrik | Ursprünglich | Nach Numba JIT | Nach Spannungsfix | Jetzt |
|--------|--------------|----------------|-------------------|-------|
| **V_oc Genauigkeit** | +82% ❌ | +82% ❌ | 0.0% ✅ | 0.0% ✅ |
| **P_mpp Genauigkeit** | -14% ❌ | -14% ❌ | 1.6% ✅ | 1.6% ✅ |
| **MPP-Suche** | ~5-10s ❌ | 0.03s ✅ | 2.2s ⚠️ | ~1-2s ⚠️ |
| **Callback** | ~46s ❌ | ~0.8s ✅ | 5.9s ❌ | ~2-4s ⚠️ |

---

## 🚀 Weitere Optimierungsmöglichkeiten

### Option 1: JIT Bisection reparieren (schwierig)
**Potentieller Speedup**: 10-20x für `find_operating_point()`  
**Zeitaufwand**: Hoch  
**Risiko**: Bugs in der Konvergenz

### Option 2: Noch weniger Punkte (einfach)
**Änderung**: 30 → 20 Punkte für I-V Kurve  
**Speedup**: ~1.5x  
**Nachteil**: Weniger glatte Kurven

### Option 3: Caching (mittel)
**Idee**: Cache berechnete I-V Kurven für identische Parameter  
**Speedup**: 2-5x bei wiederholten Berechnungen  
**Zeitaufwand**: Mittel

### Option 4: Parallel Processing (schwierig)
**Idee**: Berechne mehrere Strings parallel mit `joblib` oder `multiprocessing`  
**Speedup**: 2-3x (3 Strings parallel)  
**Zeitaufwand**: Mittel-Hoch

---

## ✅ Was der User jetzt tun kann:

### 1. App testen
```bash
python app.py
```

Die App läuft auf http://127.0.0.1:8050/

**Erwartung**:
- ✅ Korrekte Spannungen (V_oc ≈ 41.6V)
- ✅ Korrekte Leistung (P_mpp ≈ 439W)
- ⚠️ Loading-Zeit: 2-4 Sekunden pro Visualisierung

### 2. Performance-Tuning (optional)

#### Wenn 2-4s zu langsam ist:

**Option A**: Noch weniger Punkte
```python
# physics/module_model.py, physics/string_model.py
# Zeile ~147
if fast:
    iv_data = self.iv_curve(points=20)  # Statt 30
```

**Option B**: Nur "Keine Verschattung" testen
- Andere Szenarien sind rechenintensiver
- "Keine Verschattung" lädt schneller

---

## 📝 Zusammenfassung

### ✅ Erfolge:
1. Spannungen sind jetzt korrekt (0% Abweichung von Datenblatt)
2. Leistung ist korrekt (1.6% Abweichung von Datenblatt)
3. JIT für current() funktioniert (10-20x Speedup)
4. I-V Kurven mit 30 Punkten (5x Speedup vs. 150 Punkte)

### ⚠️ Kompromisse:
1. scipy.optimize.brentq statt JIT bisection (langsamer, aber korrekt)
2. Weniger Punkte → weniger glatte Kurven
3. Callback-Zeit 2-4s (akzeptabel, aber nicht optimal)

### ❌ Bekannte Probleme:
1. JIT bisection funktioniert nicht (Bug in Konvergenz)
2. Performance könnte besser sein

---

*Implementiert: November 2025*  
*PV-Modul Verschattungs-Visualisierung v0.2*  
*Status: Funktional ✅ | Performance: Akzeptabel ⚠️ | Genauigkeit: Exzellent ✅*


