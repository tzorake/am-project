import sys
from PyQt6.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QWidget
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

import numpy as np

from hsa import HeuristicSpectrumAnalyzer, osc_type

class Window(QDialog):
    def __init__(self, parent = None):
        super(Window, self).__init__(parent)

        self.signal_figure = plt.figure()
        self.fft_figure = plt.figure()

        layout = QVBoxLayout()

        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()

        groupBox1 = QGroupBox('Signal')
        groupBox2 = QGroupBox('FFT')
        groupBox3 = QGroupBox('Type')

        layout4 = QHBoxLayout()
        layout5 = QHBoxLayout()
        layout6 = QHBoxLayout()

        self.signal_canvas = FigureCanvas(self.signal_figure)
        self.fft_canvas = FigureCanvas(self.fft_figure)
        self.osc_type = QWidget()

        self.osc_type.setStyleSheet('background-color: rgb(255, 255, 255)')

        layout4.addWidget(self.signal_canvas)
        layout5.addWidget(self.fft_canvas)
        layout6.addWidget(self.osc_type)

        groupBox1.setLayout(layout4)
        groupBox2.setLayout(layout5)
        groupBox3.setLayout(layout6)

        layout1.addWidget(groupBox1)
        layout2.addWidget(groupBox2)
        layout2.addWidget(groupBox3)

        button = QPushButton('Plot')
        button.clicked.connect(self.random_plot)

        layout.addLayout(layout1)
        layout.addLayout(layout2)
        layout.addWidget(button)

        self.setLayout(layout)

        self.signal_canvas.draw()
        self.fft_canvas.draw()

        self.hsa = HeuristicSpectrumAnalyzer()

    
    def random_plot(self):
        file_name = 'txt/01b3ec1f-c6f1-4253-873d-1a3c90251cbb.txt'
        start_time = 1000.0
        omega0 = 20.3
        max_omega = omega0 * 2.1
        time_step = 0.015625

        data = np.loadtxt(file_name)
        t, w = data[:, 0], data[:, 1]

        self.hsa.set_data(t, w, start_time)
        oscillation_type = self.hsa.evaluate(max_omega, time_step)

        signal_data = self.hsa.values
        fft_data = self.hsa.result

        half = len(fft_data)
        nyquist = 1.0 / (2 * time_step)
        freq = 2.0 * np.pi * nyquist * (np.linspace(1, half, half)) / half

        self.signal_figure.clear()
        signal_ax = self.signal_figure.add_subplot(111)
        signal_ax.set_xlim(0, len(signal_data))
        signal_ax.plot(signal_data)
        self.signal_canvas.draw()

        self.fft_figure.clear()
        fft_ax = self.fft_figure.add_subplot(111)
        fft_ax.set_xlim(0.0, 1.1*omega0)
        fft_ax.plot(freq, fft_data)
        self.fft_canvas.draw()

        colors = osc_type.colors()
        color = colors[oscillation_type]
        self.osc_type.setStyleSheet(f'background-color: {color}')

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec())