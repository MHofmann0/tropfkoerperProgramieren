# tropfkoerperProgrammieren 
# Tropfkörper – CSB-Abbau & Nitrifikation (Projektarbeit)

Dieses Projekt ist eine **Python/PyQt6-Anwendung** zu der Bemessung von Tropfkörperanlagen 
und beinhaltet die Berechnungen und grafischen Darstellungen des   
**CSB-Abbaus** und der **Nitrifikation** in einem Tropfkörper.

Die Anwendung bietet:
- eine grafische Benutzeroberfläche (GUI),
- frei editierbare Eingabeparameter,
- Annahmewerte mit Default-Werten,
- zwei Liniendiagramme (CSB-Abbau & Nitrifikation),
- optionale PDF-Ausgabe.

---

## 📌 Funktionsübersicht

### Eingabefelder (GUI)
Die Eingabefelder werden im Code zentral definiert (`INPUT_FIELDS`) und im GUI vom Nutzer ausgefüllt:

- Tagesfracht des CSB (homogenisiert) [kg/d]
- Trockenwetterabfluss [m³/d]
- Tagesfracht des CSB (filtriert) [kg/d]
- Abwassertemperatur [°C]
- NH₄-N-Zulauffracht [kg/d]

👉 Diese Werte werden **erst zur Laufzeit** eingegeben und anschließend im Backend für Berechnungen verwendet.

---

### Annahmewerte
Die Annahmewerte sind im Code vordefiniert (`ASSUMPTIONS`) und können bei Bedarf im GUI angepasst werden:

- inerte CSB-Fraktionen
- hydraulische Parameter
- Tropfkörpergeometrie
- Temperatur- und Reaktionskoeffizienten
- Nitrifikationsparameter

---

### Diagramme
- **Diagramm 1:** CSB-Abbau
- **Diagramm 2:** Nitrifikation

Die Diagramme werden durch Klick auf **„Diagramme aktualisieren“** neu berechnet und geplottet.

---

## 🧮 Berechnungslogik (Backend)

Die mathematischen Grundlagen basieren auf:
- modifizierter **Velz-Gleichung** für den CSB-Abbau
- **Gujer-und-Boller-Gleichung** für die Nitrifikation
- segmentierter Höhenberechnung über den Tropfkörper

Die Berechnungen sind als Python-Funktionen umgesetzt und werden über die GUI-Eingaben gesteuert.

---

## 🖥️ Voraussetzungen

- **Python 3.10 oder neuer**

Benötigte Python-Pakete:
- PyQt6
- matplotlib
- reportlab

---

## ⚙️ Installation

### 1. Repository klonen
```bash
git clone https://github.com/DEIN_USERNAME/tropfkoerperProgramieren.git
cd tropfkoerperProgramieren
