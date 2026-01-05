import sys
import tempfile
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QStatusBar, QSizePolicy, QGroupBox,
    QPushButton, QTextEdit, QFileDialog, QMessageBox
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
    ("inerte Fraktion im Zulauf", berechnung.fs),
    ("Länge [m]", 0.5),
    ("Breite [m]", 0.2),
    ("Höhe [m]", 0.3),
    ("Temperatur [°C]", 20),
    ("Druck [bar]", 1.0),
    ("Wärmeleitfähigkeit [W/mK]", 0.6),
    ("Elastizitätsmodul [GPa]", 210),
    ("Poisson-Zahl [-]", 0.3),
    ("Reibungskoeffizient [-]", 0.25),
    ("Volumenstrom [m³/s]", 0.01),
    ("Massenstrom [kg/s]", 5),
    ("Wirkungsgrad [-]", 0.9),
    ("Sicherheitsfaktor [-]", 1.5),
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
        header = QLabel("Überschrift")
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

        self.input_fields = []
        for i in range(5):
            label = QLabel(f"Feld {i+1}:")
            edit = QLineEdit()
            edit.setFixedWidth(220)
            self.input_fields.append(edit)
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
            edit = QLineEdit(str(default))   # <<< DEFAULT-WERT
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

        self.chart_1 = LineChartWidget("Diagramm aus Eingabefeldern")
        self.chart_2 = LineChartWidget("Diagramm aus Annahmen")

        right_layout.addWidget(self.chart_1, stretch=1)
        right_layout.addWidget(self.chart_2, stretch=1)

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

    def update_charts(self):
        self.messages.clear()

        y1 = []
        for i, edit in enumerate(self.input_fields, start=1):
            val, err = self.parse_float(edit.text(), f"Feld {i}")
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

    def export_pdf(self):
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
