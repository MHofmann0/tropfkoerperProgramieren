import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QVBoxLayout,
    QHBoxLayout, QFormLayout, QStatusBar, QSizePolicy, QFrame
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class LineChartWidget(QWidget):
    """Ein einfaches Widget mit einem matplotlib-Liniendiagramm."""
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        if title:
            self.ax.set_title(title)

        # Beispiel-Daten
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 1, 0, 2, 1, 3]
        self.ax.plot(x, y)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def set_data(self, x, y, label: str | None = None):
        """Optional: Daten später aktualisieren."""
        self.ax.clear()
        if label:
            self.ax.set_title(label)
        self.ax.plot(x, y)
        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt GUI mit Inputs + 2 Liniendiagrammen")
        self.resize(1100, 650)

        # ---- Zentraler Container
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(10)
        central.setLayout(root_layout)

        # ---- Überschrift
        header = QLabel("Tropfkörperberechnung")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: 700;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
        """)
        root_layout.addWidget(header)

        # ---- Mittelbereich (links Inputs, rechts Charts)
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(12)
        root_layout.addLayout(middle_layout, stretch=1)

        # ========== Links: 5 Input-Felder ==========
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.Shape.StyledPanel)
        left_panel.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        left_panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        left_panel.setMinimumWidth(320)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(10)

        self.input_1 = QLineEdit()
        self.input_2 = QLineEdit()
        self.input_3 = QLineEdit()
        self.input_4 = QLineEdit()
        self.input_5 = QLineEdit()

        self.input_1.setPlaceholderText("Input 1 ...")
        self.input_2.setPlaceholderText("Input 2 ...")
        self.input_3.setPlaceholderText("Input 3 ...")
        self.input_4.setPlaceholderText("Input 4 ...")
        self.input_5.setPlaceholderText("Input 5 ...")

        form_layout.addRow("Feld 1:", self.input_1)
        form_layout.addRow("Feld 2:", self.input_2)
        form_layout.addRow("Feld 3:", self.input_3)
        form_layout.addRow("Feld 4:", self.input_4)
        form_layout.addRow("Feld 5:", self.input_5)

        left_panel.setLayout(form_layout)
        middle_layout.addWidget(left_panel)

        # ========== Rechts: 2 Charts untereinander ==========
        charts_container = QFrame()
        charts_container.setFrameShape(QFrame.Shape.NoFrame)
        charts_layout = QVBoxLayout()
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(12)
        charts_container.setLayout(charts_layout)

        self.chart_top = LineChartWidget("CSB-Berechnung")
        self.chart_bottom = LineChartWidget("Nitrifikationsberechnung")

        charts_layout.addWidget(self.chart_top, stretch=1)
        charts_layout.addWidget(self.chart_bottom, stretch=1)

        middle_layout.addWidget(charts_container, stretch=1)

        # ---- Fußzeile (Statusbar)
        status = QStatusBar()
        status.showMessage("Fußzeile / Status: bereit")
        self.setStatusBar(status)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

