Tropfkörperberechnung – Python GUI
Kurzbeschreibung

Dieses Projekt ist eine Python-Anwendung mit grafischer Benutzeroberfläche (GUI) zur Berechnung des CSB-Abbaus und der Nitrifikation in einem Tropfkörper.
Die Berechnungen erfolgen auf Basis ingenieurtechnischer Ansätze, die Ergebnisse werden grafisch dargestellt.

Die Anwendung wurde im Rahmen eines Übungsprojekts im Modul Programmieren erstellt.

Voraussetzungen

    Python 3.11 oder höher
    Windows (aufgrund der Aktivierung der virtuellen Umgebung)
    Empfohlen: Visual Studio Code

Installation
1. Virtuelle Umgebung erstellen
python -m venv venv

2. Virtuelle Umgebung aktivieren
.\venv\Scripts\activate

3. Abhängigkeiten installieren
pip install -r requirements.txt

Start der Anwendung
python GUI.py


Nach dem Start öffnet sich die grafische Benutzeroberfläche zur Eingabe der Parameter und zur Anzeige der Diagramme.

Projektstruktur
├── GUI.py              # Startpunkt der GUI
├── berechnung.py       # Berechnungsfunktionen (CSB & Nitrifikation)
├── requirements.txt    # Benötigte Python-Bibliotheken
├── README.md           # Projektdokumentation
└── venv/               # Virtuelle Umgebung (lokal)

Verwendete Bibliotheken / Module

    PyQt6
    matplotlib
    reportlab
    math (Standardbibliothek)
    sys, datetime (Standardbibliothek)
    Kritische Reflexion zum Einsatz von KI

Der Einsatz von KI war insbesondere hilfreich bei:
    der Strukturierung des Codes,
    der Erstellung der GUI mit PyQt,
    der Umsetzung mathematischer Formeln in Python.

Korrekturen waren notwendig bei:

    logischen Fehlern in Berechnungsschritten,
    auswerten der vorhandenen Unterlagen
    Einheitenumrechnungen,
    der Anpassuverknüpfung der GUI-Logik an die berechnungen.

Manuelle Verbesserungen:

    Optimierung der Benutzerführung,
    Plausibilitätsprüfungen der Eingaben,
    Kommentierung und Strukturierung des Codes.

Kritische Reflexion der Ergebnisse

    Aufgrund der oberflächlichen und kurzen Einarbeitung in das Thema der Bemessung von Tropfkörpern zur biologischen Abwasserreinigung sind die berechneten Ergebnisse ohne Gewähr zu verwenden und es wird keine Garantie für deren Richtigkeit übernommen.