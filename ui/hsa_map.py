from PyQt6 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.colors as cl

from types import SimpleNamespace
import numpy as np
import json
import os

from PIL import ImageColor

from utilities.helper import Helper
from utilities.hsa import HeuristicSpectrumAnalyzer, osc_type



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

        oscType = osc_type.as_str(oscType)

        color_theme_path = os.path.join(".", "color_theme.json")
        color_theme = Helper.colors(color_theme_path)["hsa_map"]

        color = color_theme[oscType]
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
        self.label.setText(oscType)

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
            
    def clear(self):
        self.ffts.clear()

    def addItem(self, file_name, data):
        self.ffts[file_name] = data

class HSAMap(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(HSAMap, self).__init__(parent)
        self.setupUi()

        self.hsa = HeuristicSpectrumAnalyzer()
        self.fftWindow = FFTWindow(self)

        self.calculateButton.clicked.connect(self.on_calculateButton_clicked)
        self.showButton.clicked.connect(self.on_showButton_clicked)

    def setupUi(self):
        self.setObjectName("HSAMap")
        self.resize(874, 684)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(parent=self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_3 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_6.addWidget(self.label_3)
        self.lineEdit = QtWidgets.QLineEdit(parent=self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMinimumSize(QtCore.QSize(100, 0))
        self.lineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_6.addWidget(self.lineEdit)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label = QtWidgets.QLabel(parent=self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout_4.addWidget(self.label)
        self.lineEdit_3 = QtWidgets.QLineEdit(parent=self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_3.sizePolicy().hasHeightForWidth())
        self.lineEdit_3.setSizePolicy(sizePolicy)
        self.lineEdit_3.setMinimumSize(QtCore.QSize(100, 0))
        self.lineEdit_3.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.horizontalLayout_4.addWidget(self.lineEdit_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_2 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_5.addWidget(self.label_2)
        self.lineEdit_5 = QtWidgets.QLineEdit(parent=self.groupBox)
        self.lineEdit_5.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_5.sizePolicy().hasHeightForWidth())
        self.lineEdit_5.setSizePolicy(sizePolicy)
        self.lineEdit_5.setMinimumSize(QtCore.QSize(100, 0))
        self.lineEdit_5.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEdit_5.setText("")
        self.lineEdit_5.setFrame(False)
        self.lineEdit_5.setReadOnly(True)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.horizontalLayout_5.addWidget(self.lineEdit_5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.horizontalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(parent=self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_7 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_14.addWidget(self.label_7)
        self.start = QtWidgets.QLineEdit(parent=self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.start.sizePolicy().hasHeightForWidth())
        self.start.setSizePolicy(sizePolicy)
        self.start.setMinimumSize(QtCore.QSize(100, 0))
        self.start.setMaximumSize(QtCore.QSize(100, 16777215))
        self.start.setObjectName("start")
        self.horizontalLayout_14.addWidget(self.start)
        self.verticalLayout_5.addLayout(self.horizontalLayout_14)
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.label_8 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_17.addWidget(self.label_8)
        self.end = QtWidgets.QLineEdit(parent=self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.end.sizePolicy().hasHeightForWidth())
        self.end.setSizePolicy(sizePolicy)
        self.end.setMinimumSize(QtCore.QSize(100, 0))
        self.end.setMaximumSize(QtCore.QSize(100, 16777215))
        self.end.setObjectName("end")
        self.horizontalLayout_17.addWidget(self.end)
        self.verticalLayout_5.addLayout(self.horizontalLayout_17)
        self.horizontalLayout_18 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.label_9 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_9.setText("")
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_18.addWidget(self.label_9)
        self.lineEdit_9 = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_9.setEnabled(False)
        self.lineEdit_9.setMinimumSize(QtCore.QSize(100, 0))
        self.lineEdit_9.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEdit_9.setAutoFillBackground(False)
        self.lineEdit_9.setFrame(False)
        self.lineEdit_9.setReadOnly(True)
        self.lineEdit_9.setClearButtonEnabled(False)
        self.lineEdit_9.setObjectName("lineEdit_9")
        self.horizontalLayout_18.addWidget(self.lineEdit_9)
        self.verticalLayout_5.addLayout(self.horizontalLayout_18)
        self.horizontalLayout_13.addLayout(self.verticalLayout_5)
        self.horizontalLayout_2.addWidget(self.groupBox_2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.figure = plt.figure()
        self.map = FigureCanvas(self.figure)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.map.sizePolicy().hasHeightForWidth())
        self.map.setSizePolicy(sizePolicy)
        self.map.setMinimumSize(QtCore.QSize(500, 500))
        self.map.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.map.setObjectName("map")
        self.verticalLayout_7.addWidget(self.map)
        self.verticalLayout.addLayout(self.verticalLayout_7)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.saveButton = QtWidgets.QPushButton(parent=self)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout_12.addWidget(self.saveButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem1)
        self.calculateButton = QtWidgets.QPushButton(parent=self)
        self.calculateButton.setObjectName("calculateButton")
        self.horizontalLayout_12.addWidget(self.calculateButton)
        self.showButton = QtWidgets.QPushButton(parent=self)
        self.showButton.setObjectName("showButton")
        self.horizontalLayout_12.addWidget(self.showButton)
        self.verticalLayout.addLayout(self.horizontalLayout_12)
        self.verticalLayout.setStretch(1, 1)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi()
    
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("HSAMap", "HSAMap"))
        self.groupBox.setTitle(_translate("HSAMap", "Параметры"))
        self.label_3.setText(_translate("HSAMap", "Главная частота"))
        self.label.setText(_translate("HSAMap", "Шаг по времени"))
        self.groupBox_2.setTitle(_translate("HSAMap", "Интервал для расчетов"))
        self.label_7.setText(_translate("HSAMap", "Начало интервала"))
        self.label_8.setText(_translate("HSAMap", "Конец интервала"))
        self.saveButton.setText(_translate("HSAMap", "Сохранить"))
        self.calculateButton.setText(_translate("HSAMap", "Вычислить"))
        self.showButton.setText(_translate("HSAMap", "Просмотр"))

    def resizeEvent(self, event):
        w = self.map.size().height()
        self.map.setMaximumWidth(w)

        QtWidgets.QWidget.resizeEvent(self, event)
 
    def on_showButton_clicked(self):
        self.fftWindow.updateItems()
        self.fftWindow.show()
    
    def on_calculateButton_clicked(self):
        file_names = Helper.get_file_names()

        omega0 = sorted(list(set([Helper.get_omega0(file_name) for file_name in file_names])))
        a0_1 = sorted(list(set([Helper.get_a0_1(file_name) for file_name in file_names])))

        values = [[0] * len(a0_1) for _ in range(len(omega0))]
        self.fftWindow.clear()

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
            
            values[j][i] = oscillation_type

            fft = self.hsa.result[:]
            half = len(fft)
            nyquist = 1.0 / (2 * time_step)
            freq = 2.0 * np.pi * nyquist * (np.linspace(1, half, half)) / half
            self.fftWindow.addItem(file_name, (oscillation_type, (omega, freq, fft)))

        color_theme_path = os.path.join(".", "color_theme.json")
        color_theme = Helper.colors(color_theme_path)["hsa_map"]

        colors = [
            color_theme["CHAOS"], 
            color_theme["FAKE"],
            color_theme["UNDEF"],
            color_theme["SP_IND_FREQ"],
            color_theme["IND_FREQ"],
            color_theme["HARMONIC"],
        ]

        cmap = cl.ListedColormap(colors, len(colors))

        self.figure.clear()
        map_ax = self.figure.add_subplot(111)
        map_ax.set_xticks(list(range(len(omega0))), labels = omega0)
        map_ax.set_yticks(list(range(len(a0_1))), labels = a0_1)
        im = map_ax.imshow(values, cmap = cmap, vmin = -5.5, vmax=0.5, origin='lower')
        self.figure.colorbar(im)
        self.map.draw()