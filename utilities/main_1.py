from PyQt6 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

import numpy as np

from helper import Helper
from hsa import HeuristicSpectrumAnalyzer, osc_type


class FFTItem(QtWidgets.QWidget):
    def __init__(self, fileName, oscType, data, parent = None):
        super(FFTItem, self).__init__(parent)

        self.setMinimumSize(QtCore.QSize(400, 300))
        self.setMaximumSize(QtCore.QSize(16777215, 300))

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName("verticalLayout")
        self.name = QtWidgets.QLabel(self)
        self.name.setObjectName("name")
        self.name.setMinimumSize(QtCore.QSize(0, 24))
        self.name.setMaximumSize(QtCore.QSize(16777215, 24))

        self.verticalLayout.addWidget(self.name)

        self.fft_figure = plt.figure()

        self.fft = FigureCanvas(self.fft_figure)

        self.verticalLayout.addWidget(self.fft)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.type = QtWidgets.QWidget(self)
        self.type.setObjectName("type")
        self.type.setMinimumSize(QtCore.QSize(24, 24))
        self.type.setMaximumSize(QtCore.QSize(24, 24))

        color = osc_type.colors()[oscType]
        self.type.setStyleSheet(f"background-color: {color}")

        self.horizontalLayout.addWidget(self.type)

        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName("label")

        self.horizontalLayout.addWidget(self.label)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 14)
        self.verticalLayout.setStretch(2, 1)

        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.setLayout(self.horizontalLayout_2)
        
        self.name.setText(fileName)
        self.label.setText(osc_type.as_str(oscType))

        self.omega0, self.freq, self.fft_data = data
    
    def close(self):
        plt.close(self.fft_figure)

    def draw(self):
        self.fft_figure.clear()
        fft_ax = self.fft_figure.add_subplot(111)
        fft_ax.set_xlim(0.0, 1.1*self.omega0)
        fft_ax.plot(self.freq, self.fft_data)
        self.fft.draw()


class FFTWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(FFTWindow, self).__init__(parent)

        self.centralwidget = QtWidgets.QWidget()

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMinimumSize(QtCore.QSize(400, 600))
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 361, 578))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.centralwidget.setLayout(self.horizontalLayout)
        self.setCentralWidget(self.centralwidget)

        self.ffts = {}

        self.updateItems()


    def updateItems(self):
        def clearlayout(layout):
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                widget = item.widget()
                layout.removeItem(item)
                widget.close()
                widget.setParent(None)

        clearlayout(self.verticalLayout_2)

        for fileName, (oscType, data) in self.ffts.items():
            fft = FFTItem(fileName, oscType, data)
            fft.draw()
            self.verticalLayout_2.addWidget(fft)
            


class HSAMap(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(HSAMap, self).__init__(parent)

        self.map_figure = plt.figure()

        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.map = FigureCanvas(self.map_figure)
        self.map.setObjectName("map")
        self.map.setMinimumSize(QtCore.QSize(800, 600))
        self.map.setStyleSheet("background-color: rgba(255, 0, 255, 50)")

        self.verticalLayout.addWidget(self.map)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.calculateButton = QtWidgets.QPushButton(self)
        self.calculateButton.setObjectName("calculateButton")

        self.horizontalLayout_2.addWidget(self.calculateButton)

        self.showButton = QtWidgets.QPushButton(self)
        self.showButton.setObjectName("showButton")

        self.horizontalLayout_2.addWidget(self.showButton)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalLayout.setStretch(0, 20)
        self.verticalLayout.setStretch(2, 1)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.setLayout(self.horizontalLayout)
 
        self.hsa = HeuristicSpectrumAnalyzer()
        
        self.fftWindow = FFTWindow(self)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
    
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.calculateButton.setText(_translate("MainWindow", "Calculate"))
        self.showButton.setText(_translate("MainWindow", "Show FFTs"))
 
    def on_showButton_clicked(self):
        self.fftWindow.updateItems()
        self.fftWindow.show()
    
    def on_calculateButton_clicked(self):
        file_names = Helper.get_file_names()

        omega0 = sorted(list(set([Helper.get_omega0(file_name) for file_name in file_names])))
        a0_1 = sorted(list(set([Helper.get_a0_1(file_name) for file_name in file_names])))

        values = [[0] * len(omega0) for _ in range(len(a0_1))]
        self.fftWindow.ffts.clear()

        start_time = 1700.0
        omega = 20.3
        max_omega = omega * 2.1
        time_step = 0.015625

        for file_name in file_names:
            omega0_value = Helper.get_omega0(file_name)
            a0_1_value = Helper.get_a0_1(file_name)

            data = np.loadtxt(file_name)
            t, w = data[:, 0], data[:, 1]

            self.hsa.set_data(t, w, start_time)
            oscillation_type = self.hsa.evaluate(max_omega, time_step)

            i = omega0.index(omega0_value)
            j = a0_1.index(a0_1_value)
            
            values[i][j] = oscillation_type

            fft = self.hsa.result[:]
            half = len(fft)
            nyquist = 1.0 / (2 * time_step)
            freq = 2.0 * np.pi * nyquist * (np.linspace(1, half, half)) / half
            self.fftWindow.ffts[file_name] = (oscillation_type, (omega, freq, fft))

        self.map_figure.clear()
        map_ax = self.map_figure.add_subplot(111)
        map_ax.set_xticks(list(range(len(omega0))), labels = omega0)
        map_ax.set_yticks(list(range(len(a0_1))), labels = a0_1)
        map_ax.imshow(values)
        self.map.draw()


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = HSAMap()
    main.show()
    sys.exit(app.exec())
 
if __name__ == '__main__':
    main()