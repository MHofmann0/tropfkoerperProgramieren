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
# ZENTRALE NAMEN DER ANNAHMEFELDER (HIER ANPASSEN!)
# =========================================================
ASSUMPTION_NAMES = [
    ("Dichte [kg/m³]", 1000),
    ("Länge [m]", 1.0),
    ("Breite [m]", 1.0),
    ("Höhe [m]", 1.0),
    ("Temperatur [°C]", 25.0),
    ("Druck [bar]", 1.0),
    ("Wärmeleitfähigkeit [W/mK]", 0.5),
    ("Elastizitätsmodul [GPa]", 100.0),
    ("Poisson-Zahl [-]", 0.3),
    ("Reibungskoeffizient [-]", 0.1),
    ("Volumenstrom [m³/s]", 1.0),
    ("Massenstrom [kg/s]", 1.0),
    ("Wirkungsgrad [-]", 1.0),
    ("Sicherheitsfaktor [-]", 1.0),
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

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

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
        self.resize(1250, 800)

        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        # ---------------- Header ----------------
        header = QLabel("Überschrift")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                padding: 10px;
                border: 1px solid #aaa;
            }
        """)
        root.addWidget(header)

        # ---------------- Mittelbereich ----------------
        middle = QHBoxLayout()
        middle.setSpacing(14)
        root.addLayout(middle, stretch=1)

        # =================================================
        # LINKER BEREICH
        # =================================================
        left_container = QWidget()
        left_container.setMinimumWidth(440)
        left_layout = QVBoxLayout(left_container)
        left_layout.setSpacing(12)

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

        # -------- Annahmen --------
        assumption_box = QGroupBox("Annahmewerte")
        assumption_box.setStyleSheet(box_style)
        grid_as = QGridLayout(assumption_box)

        self.assumption_fields = []
        for i, name in enumerate(ASSUMPTION_NAMES):
            label = QLabel(f"{name}:")
            edit = QLineEdit()
            edit.setPlaceholderText(name)
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

        # ==============================================
        # RECHTER BEREICH
        # =================================================
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setSpacing(14)

        self.chart_1 = LineChartWidget("Diagramm aus Eingabefeldern")
        self.chart_2 = LineChartWidget("Diagramm aus Annahmen")

        right_layout.addWidget(self.chart_1, stretch=1)
        right_layout.addWidget(self.chart_2, stretch=1)

        # -------- Buttons --------
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_update = QPushButton("Diagramme aktualisieren")
        btn_update.setMinimumWidth(220)
        btn_update.clicked.connect(self.update_charts)

        btn_pdf = QPushButton("PDF exportieren")
        btn_pdf.setMinimumWidth(180)
        btn_pdf.clicked.connect(self.export_pdf)

        btn_row.addWidget(btn_update)
        btn_row.addWidget(btn_pdf)

        right_layout.addLayout(btn_row)

        middle.addWidget(right_container, stretch=1)

        # ---------------- Statusbar ----------------
        self.setStatusBar(QStatusBar())

    # =================================================
    # HILFSFUNKTIONEN
    # =================================================
    def log(self, text: str):
        time = datetime.now().strftime("%H:%M:%S")
        self.messages.append(f"[{time}] {text}")

    def parse_float(self, text, name):
        text = text.strip().replace(",", ".")
        if not text:
            return None, f"{name} ist leer"
        try:
            return float(text), None
        except ValueError:
            return None, f"{name} ist keine Zahl"

    # =================================================
    # BUTTON-FUNKTIONEN
    # =================================================
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
        for name, edit in zip(ASSUMPTION_NAMES, self.assumption_fields):
            val, err = self.parse_float(edit.text(), name)
            if err:
                self.log("Fehler: " + err)
            else:
                y2.append(val)

        if len(y1) >= 2:
            self.chart_1.set_data(range(1, len(y1) + 1), y1)
            self.log("Diagramm 1 aktualisiert")

        if len(y2) >= 2:
            self.chart_2.set_data(range(1, len(y2) + 1), y2)
            self.log("Diagramm 2 aktualisiert")

    def export_pdf(self):
        file, _ = QFileDialog.getSaveFileName(self, "PDF speichern", "ausgabe.pdf", "PDF (*.pdf)")
        if not file:
            return

        try:
            tmp1 = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp2 = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp1.close()
            tmp2.close()

            self.chart_1.save_png(tmp1.name)
            self.chart_2.save_png(tmp2.name)

            c = pdf_canvas.Canvas(file, pagesize=A4)
            w, h = A4

            y = h - 20 * mm
            c.setFont("Helvetica-Bold", 16)
            c.drawString(20 * mm, y, "PDF Ausgabe")

            y -= 15 * mm
            c.setFont("Helvetica", 10)
            for i, edit in enumerate(self.input_fields, start=1):
                c.drawString(20 * mm, y, f"Feld {i}: {edit.text()}")
                y -= 6 * mm

            c.showPage()
            c.drawImage(tmp1.name, 20 * mm, h - 120 * mm, width=170 * mm)
            c.showPage()
            c.drawImage(tmp2.name, 20 * mm, h - 120 * mm, width=170 * mm)

            c.save()
            self.log("PDF erfolgreich erstellt")

        except Exception as e:
            QMessageBox.critical(self, "PDF Fehler", str(e))


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

