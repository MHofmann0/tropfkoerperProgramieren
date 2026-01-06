import sys
import os
import tempfile
from io import BytesIO
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
from reportlab.lib.utils import ImageReader

from berechnung import CSB_berechnen, nitrifikation_berechnen, reinigungsleistung_berechnen


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
    ("Tagesfracht des CSB homogenisiert in [kg/d]", 7800),
    ("Trockenwetterabfluss im Jahresmittel in [m³/d]", 20000),
    ("Tagesfracht des CSB filtriert in [kg/d]", 4480),
    ("Abwassertemperatur in [°C]", 30),
    ("NH4-N-Konzentration im Zulauf zum Tropfkörper in [kg/d]", 5.2),
]


# =========================================================
# DIAGRAMM-WIDGET
# =========================================================
class LineChartWidget(QWidget):
    def __init__(self, title: str, x_label: str = "", y_label: str = ""):
        super().__init__()

        self.title = title
        self.x_label = x_label
        self.y_label = y_label

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        self.ax.set_title(title, fontsize=14, fontweight="bold")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def set_data(self, data):
        self.ax.clear()
        self.ax.set_title(self.title, fontsize=14, fontweight="bold")
        for d in data:
            # d = [y_values, x_values] (wie in deinem Code)
            self.ax.plot(d[1], d[0], marker="o")
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.ax.grid(True)
        self.canvas.draw()

    def to_png_bytes(self, dpi: int = 150) -> bytes:
        """
        Rendert die aktuelle Matplotlib-Figure als PNG-bytes (ohne Dateispeicherung).
        """
        buf = BytesIO()
        self.figure.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
        buf.seek(0)
        return buf.getvalue()


# =========================================================
# HAUPTFENSTER
# =========================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kläranlagenrechner Tropfkörper")
        self.resize(1250, 820)

        # Speichert die letzten berechneten Ergebnisse für PDF-Ausgabe
        self.last_results = None

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
            edit = QLineEdit(str(default))   # DEFAULT-WERT
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

        self.chart_1 = LineChartWidget("CSB-Abbau", x_label="CSB [mg/L]", y_label="Höhe [m]")
        self.chart_2 = LineChartWidget("Nitrifikation", x_label="NH₄-N [mg/L]", y_label="Höhe [m]")

        right_layout.addWidget(self.chart_1, stretch=1)
        right_layout.addWidget(self.chart_2, stretch=1)

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
            self.log("Falsche Werte, bitte nur Zahlen eingeben")
            return

        inputs = []
        for name, edit in self.input_fields:
            val, err = self.parse_float(edit.text(), name)
            if err:
                self.log("Fehler: " + err)
                return
            inputs.append(val)

        assumptions = []
        for (name, _), edit in zip(ASSUMPTIONS, self.assumption_fields):
            val, err = self.parse_float(edit.text(), name)
            if err:
                self.log("Fehler: " + err)
                return
            assumptions.append(val)

        csb = CSB_berechnen(
            Bd_CSB_hom_ZT=inputs[0],
            Q_d=inputs[1],
            Bd_CSB_filt_ZT=inputs[2],
            T=inputs[3],
            fs=assumptions[0],
            fa=assumptions[1],
            n=assumptions[2],
            k_20=assumptions[3],
            hoehe_TK=assumptions[4],
            A_spez=assumptions[5],
            O_C_20=assumptions[6],
            h_seg=assumptions[7],
            q_A=assumptions[8]
        )

        csb_minus_5 = CSB_berechnen(
            Bd_CSB_hom_ZT=inputs[0],
            Q_d=inputs[1],
            Bd_CSB_filt_ZT=inputs[2],
            T=inputs[3] - 5,
            fs=assumptions[0],
            fa=assumptions[1],
            n=assumptions[2],
            k_20=assumptions[3],
            hoehe_TK=assumptions[4],
            A_spez=assumptions[5],
            O_C_20=assumptions[6],
            h_seg=assumptions[7],
            q_A=assumptions[8]
        )

        csb_plus_5 = CSB_berechnen(
            Bd_CSB_hom_ZT=inputs[0],
            Q_d=inputs[1],
            Bd_CSB_filt_ZT=inputs[2],
            T=inputs[3] + 5,
            fs=assumptions[0],
            fa=assumptions[1],
            n=assumptions[2],
            k_20=assumptions[3],
            hoehe_TK=assumptions[4],
            A_spez=assumptions[5],
            O_C_20=assumptions[6],
            h_seg=assumptions[7],
            q_A=assumptions[8]
        )

        nitrification = nitrifikation_berechnen(
            werte_diagramm_csb=csb,
            B_d_NH4_ZT=inputs[4],
            Q_d=inputs[1],
            T=inputs[3],
            j_n_max_10=assumptions[9],
            N=assumptions[10],
            k=assumptions[11],
            O_N_10=assumptions[12],
            h_v=assumptions[13],
            A_spez=assumptions[5],
            h_seg=assumptions[7],
            q_A=assumptions[8]
        )

        self.chart_1.set_data([csb, csb_minus_5, csb_plus_5])
        self.chart_2.set_data([[nitrification[0], nitrification[2]]])

        reinigungsleistung = reinigungsleistung_berechnen(nitrification)
        self.last_results = reinigungsleistung

        self.log("CSB-Reinigung absolut: " + str(reinigungsleistung["CSB-Reinigung"]["absolut"]))
        self.log("CSB-Reinigung relativ: " + str(reinigungsleistung["CSB-Reinigung"]["relativ"]) + "%")
        self.log("NH4-N-Reinigung absolut: " + str(reinigungsleistung["NH4-N-Reinigung"]["absolut"]))
        self.log("NH4-N-Reinigung relativ: " + str(reinigungsleistung["NH4-N-Reinigung"]["relativ"]) + "%")

    # ---------------- PDF Helpers ----------------
    def _pdf_new_page(self, c: pdf_canvas.Canvas):
        c.showPage()

    def export_pdf(self):
        # ✅ Standard-Dateiname: "Tropfkörperberechnung - Datum.pdf"
        datum = datetime.now().strftime("%Y-%m-%d")
        default_name = f"Tropfkörperberechnung - {datum}.pdf"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "PDF speichern",
            default_name,
            "PDF (*.pdf)"
        )
        if not filename:
            return

        c = pdf_canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        margin_x = 18 * mm
        top_margin = 18 * mm
        bottom_margin = 18 * mm
        y = height - top_margin

        def ensure_space(min_space_points: float):
            nonlocal y
            if y - min_space_points < bottom_margin:
                self._pdf_new_page(c)
                y = height - top_margin

        def draw_line(text, font="Helvetica", size=10, dy=5 * mm):
            nonlocal y
            ensure_space(dy + 2 * mm)
            c.setFont(font, size)
            c.drawString(margin_x, y, text)
            y -= dy

        def draw_image(png_bytes: bytes, title: str, max_w: float, max_h: float, title_gap=5 * mm, after_gap=6 * mm):
            """
            Fügt ein PNG ins PDF ein (skalierend, Seitenumbruch-sicher).
            """
            nonlocal y

            img = ImageReader(BytesIO(png_bytes))
            iw, ih = img.getSize()

            # Skaliere auf max_w/max_h unter Beibehaltung Seitenverhältnis
            scale = min(max_w / iw, max_h / ih)
            w = iw * scale
            h = ih * scale

            # Platz prüfen: Titel + Bild + After gap
            ensure_space(title_gap + h + after_gap + 8)

            c.setFont("Helvetica-Bold", 11)
            c.drawString(margin_x, y, title)
            y -= title_gap

            # Bild platzieren (links bündig)
            c.drawImage(img, margin_x, y - h, width=w, height=h, preserveAspectRatio=True, mask="auto")
            y -= (h + after_gap)

        # ---------------- Seite 1: Werte + Ergebnisse ----------------
        draw_line("Tropfkörperberechnung – PDF-Ausgabe", font="Helvetica-Bold", size=14, dy=8 * mm)
        draw_line(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", font="Helvetica", size=9, dy=8 * mm)

        # Eingaben
        draw_line("Eingabewerte:", font="Helvetica-Bold", size=11, dy=6 * mm)
        for name, edit in self.input_fields:
            draw_line(f"- {name}: {edit.text()}", font="Helvetica", size=10, dy=5 * mm)

        y -= 2 * mm

        # Annahmen
        draw_line("Annahmewerte:", font="Helvetica-Bold", size=11, dy=6 * mm)
        for (name, _), edit in zip(ASSUMPTIONS, self.assumption_fields):
            draw_line(f"- {name}: {edit.text()}", font="Helvetica", size=10, dy=5 * mm)

        y -= 4 * mm

        # Ergebnisse (falls vorhanden)
        draw_line("Ergebnisse:", font="Helvetica-Bold", size=11, dy=6 * mm)
        if self.last_results is None:
            draw_line("Keine Ergebnisse vorhanden. Bitte zuerst 'Diagramme aktualisieren' ausführen.", size=10, dy=5 * mm)
        else:
            rr = self.last_results
            draw_line(f"CSB-Reinigung absolut: {rr['CSB-Reinigung']['absolut']}", size=10, dy=5 * mm)
            draw_line(f"CSB-Reinigung relativ: {rr['CSB-Reinigung']['relativ']} %", size=10, dy=5 * mm)
            draw_line(f"NH4-N-Reinigung absolut: {rr['NH4-N-Reinigung']['absolut']}", size=10, dy=5 * mm)
            draw_line(f"NH4-N-Reinigung relativ: {rr['NH4-N-Reinigung']['relativ']} %", size=10, dy=5 * mm)

        # ---------------- Diagramme (Seite 2, sauber) ----------------
        self._pdf_new_page(c)
        y = height - top_margin

        draw_line("Diagramme:", font="Helvetica-Bold", size=14, dy=10 * mm)

        # Diagramme als PNG aus Matplotlib-Figures rendern
        try:
            # Maximaler Bildbereich (A4 mit Rändern)
            max_w = width - 2 * margin_x
            # Lass genug Platz für zwei Diagramme untereinander
            max_h_each = (height - top_margin - bottom_margin - 25 * mm) / 2.0

            png1 = self.chart_1.to_png_bytes(dpi=170)
            draw_image(png1, "CSB-Abbau", max_w=max_w, max_h=max_h_each)

            png2 = self.chart_2.to_png_bytes(dpi=170)
            draw_image(png2, "Nitrifikation", max_w=max_w, max_h=max_h_each)

        except Exception as e:
            draw_line(f"Fehler beim Einbetten der Diagramme: {e}", font="Helvetica", size=10, dy=6 * mm)

        c.save()
        self.log(f"PDF erfolgreich gespeichert: {filename}")


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
