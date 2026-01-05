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


class LineChartWidget(QWidget):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        self._title = title
        if title:
            self.ax.set_title(title, fontsize=14, fontweight="bold")

        # Initiale Beispiel-Daten
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 1, 0, 2, 1, 3]
        self.ax.plot(x, y)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def set_data(self, x, y, title: str | None = None):
        """Diagramm aktualisieren."""
        self.ax.clear()
        used_title = title if title is not None else self._title
        if used_title:
            self.ax.set_title(used_title, fontsize=14, fontweight="bold")
        self.ax.plot(x, y)
        self.canvas.draw()

    def save_png(self, path: str):
        """Speichert das Diagramm als PNG (für PDF-Einbettung)."""
        self.figure.savefig(path, dpi=150, bbox_inches="tight")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt GUI mit Eingabefeldern, Diagrammen & PDF Export")
        self.resize(1200, 780)

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(10)
        central.setLayout(root_layout)

        # ---- Überschrift
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
        root_layout.addWidget(header)

        # ---- Mittelbereich
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(14)
        root_layout.addLayout(middle_layout, stretch=1)

        # ===== Links: Container (Inputs + Annahmen + Meldungen) =====
        left_container = QWidget()
        left_container.setMinimumWidth(420)
        left_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)
        left_container.setLayout(left_layout)

        groupbox_style = """
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

        # ===== Box 1: 5 Eingabefelder =====
        inputs_box = QGroupBox("Eingabefelder")
        inputs_box.setStyleSheet(groupbox_style)

        grid_inputs = QGridLayout()
        grid_inputs.setHorizontalSpacing(10)
        grid_inputs.setVerticalSpacing(8)
        grid_inputs.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.input_1 = QLineEdit(); self.input_1.setPlaceholderText("Input 1")
        self.input_2 = QLineEdit(); self.input_2.setPlaceholderText("Input 2")
        self.input_3 = QLineEdit(); self.input_3.setPlaceholderText("Input 3")
        self.input_4 = QLineEdit(); self.input_4.setPlaceholderText("Input 4")
        self.input_5 = QLineEdit(); self.input_5.setPlaceholderText("Input 5")

        grid_inputs.addWidget(QLabel("Feld 1:"), 0, 0); grid_inputs.addWidget(self.input_1, 0, 1)
        grid_inputs.addWidget(QLabel("Feld 2:"), 1, 0); grid_inputs.addWidget(self.input_2, 1, 1)
        grid_inputs.addWidget(QLabel("Feld 3:"), 2, 0); grid_inputs.addWidget(self.input_3, 2, 1)
        grid_inputs.addWidget(QLabel("Feld 4:"), 3, 0); grid_inputs.addWidget(self.input_4, 3, 1)
        grid_inputs.addWidget(QLabel("Feld 5:"), 4, 0); grid_inputs.addWidget(self.input_5, 4, 1)

        for field in [self.input_1, self.input_2, self.input_3, self.input_4, self.input_5]:
            field.setFixedWidth(220)

        inputs_box.setLayout(grid_inputs)
        left_layout.addWidget(inputs_box)

        # ===== Box 2: 14 Annahmewerte =====
        assumptions_box = QGroupBox("Annahmewerte")
        assumptions_box.setStyleSheet(groupbox_style)

        grid_assumptions = QGridLayout()
        grid_assumptions.setHorizontalSpacing(10)
        grid_assumptions.setVerticalSpacing(8)
        grid_assumptions.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.assumption_fields = []
        for i in range(14):
            label = QLabel(f"Annahme {i+1}:")
            edit = QLineEdit()
            edit.setPlaceholderText(f"Wert {i+1}")
            edit.setFixedWidth(220)

            self.assumption_fields.append(edit)
            grid_assumptions.addWidget(label, i, 0)
            grid_assumptions.addWidget(edit, i, 1)

        assumptions_box.setLayout(grid_assumptions)
        left_layout.addWidget(assumptions_box)

        # ===== Unter den Eingabewerten: Textausgabefeld für Fehlermeldungen =====
        messages_box = QGroupBox("Meldungen")
        messages_box.setStyleSheet(groupbox_style)

        msg_layout = QVBoxLayout()
        msg_layout.setContentsMargins(6, 6, 6, 6)

        self.messages = QTextEdit()
        self.messages.setReadOnly(True)
        self.messages.setPlaceholderText("Hier erscheinen Hinweise/Fehlermeldungen ...")
        self.messages.setMinimumHeight(120)

        msg_layout.addWidget(self.messages)
        messages_box.setLayout(msg_layout)
        left_layout.addWidget(messages_box)

        middle_layout.addWidget(left_container)

        # ===== Rechts: Diagramme + Buttons unten rechts =====
        right_container = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(14)
        right_container.setLayout(right_layout)

        self.chart_top = LineChartWidget("Liniendiagramm 1")
        self.chart_bottom = LineChartWidget("Liniendiagramm 2")

        right_layout.addWidget(self.chart_top, stretch=1)
        right_layout.addWidget(self.chart_bottom, stretch=1)

        # Button-Zeile unten rechts
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        self.update_button = QPushButton("Diagramme aktualisieren")
        self.update_button.setFixedHeight(38)
        self.update_button.setMinimumWidth(220)
        self.update_button.clicked.connect(self.update_charts)

        self.pdf_button = QPushButton("PDF exportieren")
        self.pdf_button.setFixedHeight(38)
        self.pdf_button.setMinimumWidth(180)
        self.pdf_button.clicked.connect(self.export_pdf)

        btn_row.addWidget(self.update_button)
        btn_row.addWidget(self.pdf_button)
        right_layout.addLayout(btn_row)

        middle_layout.addWidget(right_container, stretch=1)

        # ---- Fußzeile
        status = QStatusBar()
        status.showMessage("Bereit")
        self.setStatusBar(status)

    def add_message(self, text: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append(f"[{timestamp}] {text}")

    def _parse_float(self, raw: str, name: str):
        """Parst float (deutsche Komma-Eingaben erlaubt)."""
        raw = raw.strip()
        if raw == "":
            return None, f"{name} ist leer."
        raw = raw.replace(",", ".")
        try:
            return float(raw), None
        except ValueError:
            return None, f"{name} ist keine Zahl: '{raw}'"

    def collect_values(self):
        """Sammelt Werte und schreibt Meldungen."""
        self.messages.clear()

        input_edits = [
            ("Feld 1", self.input_1),
            ("Feld 2", self.input_2),
            ("Feld 3", self.input_3),
            ("Feld 4", self.input_4),
            ("Feld 5", self.input_5),
        ]

        inputs = []
        errors = 0
        for name, edit in input_edits:
            val, err = self._parse_float(edit.text(), name)
            if err:
                self.add_message("Fehler: " + err)
                errors += 1
            inputs.append((name, val))

        assumptions = []
        for i, edit in enumerate(self.assumption_fields, start=1):
            name = f"Annahme {i}"
            val, err = self._parse_float(edit.text(), name)
            if err:
                self.add_message("Fehler: " + err)
                errors += 1
            assumptions.append((name, val))

        if errors == 0:
            self.add_message("OK: Alle Werte sind gültige Zahlen.")
        else:
            self.add_message(f"Achtung: {errors} Problem(e) gefunden. Diagramme werden mit vorhandenen Zahlen aktualisiert.")

        return inputs, assumptions

    def update_charts(self):
        """Button-Funktion: Diagramme anhand der Eingabefelder aktualisieren."""
        inputs, assumptions = self.collect_values()

        # --- Diagramm 1: nutzt 5 Eingabefelder als y-Werte
        y1 = [v for _, v in inputs if v is not None]
        x1 = list(range(1, len(y1) + 1))

        if len(y1) >= 2:
            self.chart_top.set_data(x1, y1, title="Liniendiagramm 1 (aus Eingaben)")
            self.add_message("Diagramm 1 aktualisiert.")
        else:
            self.add_message("Hinweis: Für Diagramm 1 bitte mindestens 2 gültige Zahlen in Feld 1-5 eingeben.")

        # --- Diagramm 2: nutzt 14 Annahmen als y-Werte
        y2 = [v for _, v in assumptions if v is not None]
        x2 = list(range(1, len(y2) + 1))

        if len(y2) >= 2:
            self.chart_bottom.set_data(x2, y2, title="Liniendiagramm 2 (aus Annahmen)")
            self.add_message("Diagramm 2 aktualisiert.")
        else:
            self.add_message("Hinweis: Für Diagramm 2 bitte mindestens 2 gültige Zahlen bei den Annahmen eingeben.")

        self.statusBar().showMessage("Diagramme aktualisiert")

    def export_pdf(self):
        """Erstellt eine PDF-Ausgabe (mit Werten + Diagramm-Bildern)."""
        # Optional: vor PDF nochmal rechnen/aktualisieren
        # self.update_charts()
        inputs, assumptions = self.collect_values()

        file_path, _ = QFileDialog.getSaveFileName(
            self, "PDF speichern", "ausgabe.pdf", "PDF Dateien (*.pdf)"
        )
        if not file_path:
            self.add_message("PDF-Export abgebrochen.")
            return

        try:
            tmp1 = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp2 = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp1.close()
            tmp2.close()

            self.chart_top.save_png(tmp1.name)
            self.chart_bottom.save_png(tmp2.name)

            c = pdf_canvas.Canvas(file_path, pagesize=A4)
            width, height = A4

            y = height - 20 * mm
            c.setFont("Helvetica-Bold", 16)
            c.drawString(20 * mm, y, "PDF Ausgabe")
            y -= 10 * mm

            c.setFont("Helvetica", 10)
            c.drawString(20 * mm, y, f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
            y -= 10 * mm

            c.setFont("Helvetica-Bold", 12)
            c.drawString(20 * mm, y, "Eingabefelder")
            y -= 7 * mm
            c.setFont("Helvetica", 10)

            for name, val in inputs:
                c.drawString(22 * mm, y, f"{name}: {val if val is not None else '-'}")
                y -= 5.5 * mm
                if y < 30 * mm:
                    c.showPage()
                    y = height - 20 * mm

            y -= 4 * mm

            c.setFont("Helvetica-Bold", 12)
            c.drawString(20 * mm, y, "Annahmewerte")
            y -= 7 * mm
            c.setFont("Helvetica", 10)

            for name, val in assumptions:
                c.drawString(22 * mm, y, f"{name}: {val if val is not None else '-'}")
                y -= 5.5 * mm
                if y < 30 * mm:
                    c.showPage()
                    y = height - 20 * mm

            c.showPage()
            y = height - 20 * mm
            c.setFont("Helvetica-Bold", 12)
            c.drawString(20 * mm, y, "Diagramme")
            y -= 10 * mm

            c.setFont("Helvetica", 10)
            c.drawString(20 * mm, y, "Diagramm 1")
            y -= 5 * mm
            c.drawImage(tmp1.name, 20 * mm, y - 80 * mm, width=170 * mm, height=80 * mm,
                        preserveAspectRatio=True, anchor='n')
            y -= 90 * mm

            c.drawString(20 * mm, y, "Diagramm 2")
            y -= 5 * mm
            c.drawImage(tmp2.name, 20 * mm, y - 80 * mm, width=170 * mm, height=80 * mm,
                        preserveAspectRatio=True, anchor='n')

            c.save()

            self.statusBar().showMessage(f"PDF gespeichert: {file_path}")
            self.add_message(f"PDF erfolgreich gespeichert: {file_path}")

        except Exception as e:
            self.add_message(f"Fehler beim PDF-Export: {e}")
            QMessageBox.critical(self, "PDF-Export Fehler", f"Fehler beim Erstellen der PDF:\n\n{e}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

