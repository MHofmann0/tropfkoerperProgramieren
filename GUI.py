import sys
import tempfile
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QStatusBar, QGroupBox,
    QPushButton, QTextEdit, QFileDialog
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import mm


# =========================================================
# ANNAHMEN: NAME + DEFAULT-WERT (HIER BEARBEITEN!)
# =========================================================
ASSUMPTIONS = [
    ("inerte Fraktion im Zulauf", 0.05),
    ("inerte Fraktion im partikulären CSB", 0.3),
    ("hydraulischer Koeffizient", 0.5),
    ("Reaktionskonstante", 0.0024),
    ("höhe Tropfkörper", 5.2),
    ("spezifische Oberfläche des Tropfkörpers in [m²/m³]", 125),
    ("Temperaturkoeffizient", 1.03),
    ("Segmenthöhe in [m]", 0.1),
    ("Hydraulische Beschickung in [m³/m²*h]", 0.39),
    ("Reaktionsrate bei 10°C in [g NH4-N/m²*d]", 1.8),
    ("Sättigungskonstante in [g NH4-N/m³] #liegt zwischen 1 und 2", 2.0),
    ("Faktor K", 0.11),
    ("Temperaturkorrekturfaktor", 1.02),
    ("Startpunkt Höhe", 0.0),
]

# =========================================================
# EINGABEFELDER: NAME + DEFAULT-WERT (HIER BEARBEITEN!)
# =========================================================
INPUT_FIELDS = [
    ("Tagesfracht des CSB homogenisiert in [kg/d]:", 7800),
    ("Trockenwetterabfluss im Jahresmittel in [m³/d]:", 20000),
    ("Tagesfracht des CSB filtriert in [kg/d]:", 4480),
    ("Abwassertemperatur in [°C]:", 5),
    ("NH4-N-Konzentration im Zulauf zum Tropfkörper in [kg/d]:", 5.2),
]


# =========================================================
# DIAGRAMM-WIDGET
# =========================================================
class LineChartWidget(QWidget):
    def __init__(self, title: str):
        super().__init__()

        self.title = title
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        self.ax.set_title(title, fontsize=14, fontweight="bold")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def set_data(self, x, y):
        self.ax.clear()
        self.ax.set_title(self.title, fontsize=14, fontweight="bold")
        self.ax.plot(x, y, marker="o")
        self.ax.grid(True)
        self.canvas.draw()

    def save_png(self, path: str):
        self.figure.savefig(path, dpi=150, bbox_inches="tight")


# =========================================================
# HAUPTFENSTER
# =========================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt GUI – Eingaben, Annahmen & Diagramme")
        self.resize(1250, 820)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # ---------------- Header ----------------
        header = QLabel("Tropfkörperberechnung")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size:22px; font-weight:bold; padding:10px; border:1px solid #aaa;")
        root.addWidget(header)

        # ---------------- Mittelbereich ----------------
        middle = QHBoxLayout()
        root.addLayout(middle, stretch=1)

        # =================================================
        # LINKER BEREICH
        # =================================================
        left_container = QWidget()
        left_container.setMinimumWidth(460)
        left_layout = QVBoxLayout(left_container)

        box_style = """
            QGroupBox {
                border: 2px solid #444;
                border-radius: 0px;
                margin-top: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                top: -5px;
            }
        """

        # -------- Eingabefelder --------
        input_box = QGroupBox("Eingabefelder")
        input_box.setStyleSheet(box_style)
        grid_in = QGridLayout(input_box)

        self.input_fields = []  # Liste aus (name, QLineEdit)
        for i, (name, default) in enumerate(INPUT_FIELDS):
            label = QLabel(f"{name}:")
            edit = QLineEdit(str(default))
            edit.setFixedWidth(220)
            self.input_fields.append((name, edit))
            grid_in.addWidget(label, i, 0)
            grid_in.addWidget(edit, i, 1)

        left_layout.addWidget(input_box)

        # -------- Annahmen (MIT DEFAULT-WERTEN) --------
        assumption_box = QGroupBox("Annahmewerte")
        assumption_box.setStyleSheet(box_style)
        grid_as = QGridLayout(assumption_box)

        self.assumption_fields = []
        for i, (name, default) in enumerate(ASSUMPTIONS):
            label = QLabel(f"{name}:")
            edit = QLineEdit(str(default))  # DEFAULT-WERT
            edit.setFixedWidth(220)
            self.assumption_fields.append(edit)
            grid_as.addWidget(label, i, 0)
            grid_as.addWidget(edit, i, 1)

        left_layout.addWidget(assumption_box)

        # -------- Meldungen --------
        msg_box = QGroupBox("Meldungen")
        msg_box.setStyleSheet(box_style)
        msg_layout = QVBoxLayout(msg_box)

        self.messages = QTextEdit()
        self.messages.setReadOnly(True)
        self.messages.setMinimumHeight(120)
        msg_layout.addWidget(self.messages)

        left_layout.addWidget(msg_box)

        middle.addWidget(left_container)

        # =================================================
        # RECHTER BEREICH
        # =================================================
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)

        self.chart_1 = LineChartWidget("CSB-Abbau")
        self.chart_2 = LineChartWidget("Nitrifikation")

        right_layout.addWidget(self.chart_1, stretch=1)
        right_layout.addWidget(self.chart_2, stretch=1)

        # =================================================
        # ✅ NEUES OUTPUT-FELD UNTER DEN 2 GRAPHEN
        # =================================================
        output_box = QGroupBox("Ergebnis")
        output_box.setStyleSheet(box_style)
        output_layout = QHBoxLayout(output_box)

        label_rl = QLabel("Reinigungsleistung [in %]:")
        self.output_rl = QLineEdit()
        self.output_rl.setReadOnly(True)
        self.output_rl.setFixedWidth(120)
        self.output_rl.setAlignment(Qt.AlignmentFlag.AlignRight)

        output_layout.addWidget(label_rl)
        output_layout.addWidget(self.output_rl)
        output_layout.addStretch()

        right_layout.addWidget(output_box)

        # -------- Buttons --------
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_update = QPushButton("Diagramme aktualisieren")
        btn_update.clicked.connect(self.update_charts)

        btn_pdf = QPushButton("PDF exportieren")
        btn_pdf.clicked.connect(self.export_pdf)

        btn_row.addWidget(btn_update)
        btn_row.addWidget(btn_pdf)
        right_layout.addLayout(btn_row)

        middle.addWidget(right_container, stretch=1)

        self.setStatusBar(QStatusBar())

    # =================================================
    # LOGIK
    # =================================================
    def log(self, text: str):
        self.messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] {text}")

    def parse_float(self, text, name):
        text = text.strip().replace(",", ".")
        try:
            return float(text), None
        except ValueError:
            return None, f"{name} ist keine Zahl"

    def all_inputs_are_numbers(self):
        # prüft Eingabefelder
        for name, edit in self.input_fields:
            _, err = self.parse_float(edit.text(), name)
            if err:
                return False

        # prüft Annahmenfelder
        for (name, _), edit in zip(ASSUMPTIONS, self.assumption_fields):
            _, err = self.parse_float(edit.text(), name)
            if err:
                return False

        return True

    def update_charts(self):
        self.messages.clear()

        # ZUERST prüfen, ob alle Eingaben Zahlen sind
        if not self.all_inputs_are_numbers():
            self.output_rl.setText("")  # Output leeren
            self.log("Falsche Werte, bitte nur Zahlen eingeben")
            return

        y1 = []
        for name, edit in self.input_fields:
            val, err = self.parse_float(edit.text(), name)
            if err:
                self.log("Fehler: " + err)
            else:
                y1.append(val)

        y2 = []
        for (name, _), edit in zip(ASSUMPTIONS, self.assumption_fields):
            val, err = self.parse_float(edit.text(), name)
            if err:
                self.log("Fehler: " + err)
            else:
                y2.append(val)

        if len(y1) >= 2:
            self.chart_1.set_data(range(1, len(y1) + 1), y1)

        if len(y2) >= 2:
            self.chart_2.set_data(range(1, len(y2) + 1), y2)

        # =================================================
        # ✅ Reinigungsleistung berechnen (Beispiel)
        # - hier als Demo: aus erstem und letztem CSB-Wert
        # =================================================
        if len(y1) >= 2 and y1[0] != 0:
            reinigungsleistung = (1 - y1[-1] / y1[0]) * 100
            self.output_rl.setText(f"{reinigungsleistung:.1f}")
        else:
            self.output_rl.setText("")

    def export_pdf(self):
        # (Dein bisheriger Code war hier noch nicht fertig – ich lasse das Verhalten wie bei dir:
        QFileDialog.getSaveFileName(self, "PDF speichern", "ausgabe.pdf", "PDF (*.pdf)")


# =========================================================
# START
# =========================================================
def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
