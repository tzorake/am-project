from PyQt6 import QtCore, QtGui, QtWidgets

import os
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as cl
import matplotlib.ticker as mticker

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from ui.common_map_interface import CommonMapInterface

from utilities.helper import Helper
from utilities.hsa import HeuristicSpectrumAnalyzer


def handler(file_name, params):
    timeColumn = params["time_column"]
    valuesColumn = params["values_column"]
    start_time = params["start_time"]
    end_time = params["end_time"]
    omega = params["omega"]
    max_omega = omega * 2.1
    time_step = params["time_step"]

    data = np.loadtxt(file_name)
    t, w = data[:, timeColumn], data[:, valuesColumn]

    hsa = HeuristicSpectrumAnalyzer()

    hsa.set_data(t, w, start_time, end_time)
    oscillation_type = hsa.evaluate(max_omega, time_step)

    fft = hsa.result[:]
    half = len(fft)
    nyquist = 1.0 / (2 * time_step)
    freq = 2.0 * np.pi * nyquist * (np.linspace(1, half, half)) / half

    return file_name, oscillation_type, omega, freq, fft


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

        color_theme_path = os.path.join(".", "color_theme.json")
        color_theme = Helper.colors(color_theme_path)["hsa_map"]
        
        color_values, color_hexes = zip(*list(map(lambda x: (x["value"], x["color"]), color_theme.values())))
        colors = dict(zip(color_values, color_hexes))
        color = colors[oscType]
        color_key_mapping = dict(zip(color_values, list(color_theme.keys())))
        color_string = color_key_mapping[oscType]

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
        self.label.setText(color_string)

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

        self.elements = {}

    def updateItems(self):
        def clearlayout(layout):
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                widget = item.widget()
                layout.removeItem(item)
                widget.close()
                widget.setParent(None)

        clearlayout(self.verticalLayout_2)

        for fileName, (oscType, data) in self.elements.items():
            fft = FFTItem(fileName, oscType, data)
            fft.draw()
            self.verticalLayout_2.addWidget(fft)
            
    def clearItems(self):
        self.elements.clear()

    def addItem(self, file_name, data):
        self.elements[file_name] = data


class HSATopPanel(QtWidgets.QWidget):
    startChanged = QtCore.pyqtSignal(str)
    endChanged = QtCore.pyqtSignal(str)
    omegaChanged = QtCore.pyqtSignal(str)
    timeStepChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent = None):
        super(HSATopPanel, self).__init__(parent)
        self.setupUi()

        self.start.editingFinished.connect(self.on_start_finished)
        self.end.editingFinished.connect(self.on_end_finished)
        self.omega.editingFinished.connect(self.on_omega_finished)
        self.timeStep.editingFinished.connect(self.on_timeStep_finished)

    def setupUi(self):
        self.setObjectName("HSATopPanel")
        self.resize(427, 136)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.parameters = QtWidgets.QGroupBox(parent=self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.parameters.sizePolicy().hasHeightForWidth())
        self.parameters.setSizePolicy(sizePolicy)
        self.parameters.setObjectName("parameters")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.parameters)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(parent=self.parameters)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        validator = QtGui.QDoubleValidator()
        validator.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates))
        self.omega = QtWidgets.QLineEdit(parent=self.parameters)
        self.omega.setMinimumSize(QtCore.QSize(100, 20))
        self.omega.setMaximumSize(QtCore.QSize(100, 20))
        self.omega.setObjectName("omega")
        self.omega.setValidator(validator)
        self.horizontalLayout_2.addWidget(self.omega)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(parent=self.parameters)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        validator = QtGui.QDoubleValidator()
        validator.setLocale(QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates))
        self.timeStep = QtWidgets.QLineEdit(parent=self.parameters)
        self.timeStep.setMinimumSize(QtCore.QSize(100, 20))
        self.timeStep.setMaximumSize(QtCore.QSize(100, 20))
        self.timeStep.setObjectName("timeStep")
        self.timeStep.setValidator(validator)
        self.horizontalLayout_3.addWidget(self.timeStep)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(parent=self.parameters)
        self.label_3.setText("")
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.placeholder = QtWidgets.QLineEdit(parent=self.parameters)
        self.placeholder.setEnabled(False)
        self.placeholder.setMinimumSize(QtCore.QSize(100, 20))
        self.placeholder.setMaximumSize(QtCore.QSize(100, 20))
        self.placeholder.setFrame(False)
        self.placeholder.setObjectName("placeholder")
        self.horizontalLayout_4.addWidget(self.placeholder)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout.addWidget(self.parameters)
        self.interval = QtWidgets.QGroupBox(parent=self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.interval.sizePolicy().hasHeightForWidth())
        self.interval.setSizePolicy(sizePolicy)
        self.interval.setObjectName("interval")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.interval)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_4 = QtWidgets.QLabel(parent=self.interval)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_5.addWidget(self.label_4)
        validator = QtGui.QDoubleValidator()
        locale = QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates)
        locale.setNumberOptions(QtCore.QLocale.NumberOption.RejectGroupSeparator)
        validator.setLocale(locale)
        self.start = QtWidgets.QLineEdit(parent=self.interval)
        self.start.setMinimumSize(QtCore.QSize(100, 20))
        self.start.setMaximumSize(QtCore.QSize(100, 20))
        self.start.setObjectName("lineEdit")
        self.start.setValidator(validator)
        self.horizontalLayout_5.addWidget(self.start)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_5 = QtWidgets.QLabel(parent=self.interval)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_6.addWidget(self.label_5)
        validator2 = QtGui.QDoubleValidator()
        locale = QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates)
        locale.setNumberOptions(QtCore.QLocale.NumberOption.RejectGroupSeparator)
        validator2.setLocale(locale)
        self.end = QtWidgets.QLineEdit(parent=self.interval)
        self.end.setMinimumSize(QtCore.QSize(100, 20))
        self.end.setMaximumSize(QtCore.QSize(100, 20))
        self.end.setObjectName("lineEdit_2")
        self.end.setValidator(validator2)
        self.horizontalLayout_6.addWidget(self.end)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_6 = QtWidgets.QLabel(parent=self.interval)
        self.label_6.setText("")
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_7.addWidget(self.label_6)
        self.lineEdit_3 = QtWidgets.QLineEdit(parent=self.interval)
        self.lineEdit_3.setEnabled(False)
        self.lineEdit_3.setMinimumSize(QtCore.QSize(100, 20))
        self.lineEdit_3.setMaximumSize(QtCore.QSize(100, 20))
        self.lineEdit_3.setFrame(False)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.horizontalLayout_7.addWidget(self.lineEdit_3)
        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
        self.horizontalLayout.addWidget(self.interval)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("HSATopPanel", "Form"))
        self.parameters.setTitle(_translate("HSATopPanel", "Параметры"))
        self.label.setText(_translate("HSATopPanel", "Главная частота"))
        self.label_2.setText(_translate("HSATopPanel", "Шаг по времени"))
        self.interval.setTitle(_translate("HSATopPanel", "Интервал для расчетов"))
        self.label_4.setText(_translate("HSATopPanel", "Начало интервала"))
        self.label_5.setText(_translate("HSATopPanel", "Конец интервала"))

    @QtCore.pyqtSlot()
    def on_start_finished(self):
        x = self.start.text()
        self.startChanged.emit(x)

    @QtCore.pyqtSlot()
    def on_end_finished(self):
        x = self.end.text()
        self.endChanged.emit(x)

    @QtCore.pyqtSlot()
    def on_omega_finished(self):
        x = self.omega.text()
        self.omegaChanged.emit(x)
    
    @QtCore.pyqtSlot()
    def on_timeStep_finished(self):
        x = self.timeStep.text()
        self.timeStepChanged.emit(x)


class HSAMap(CommonMapInterface):
    def __init__(self, parent = None):
        super(HSAMap, self).__init__(HSATopPanel(), parent)

        self.fftWindow = FFTWindow(self)
        top = self.topPanel()

        self._default_parameters = {
            "omega": 20.3,
            "time_step": 0.015625,
            "start_time": 0.0,
            "end_time": 0.0,
        }
        self._field_mapping = {
            "omega": top.omega,
            "time_step": top.timeStep,
            "start_time": top.start,
            "end_time": top.end,
        }

        self._default_parameters["time_column"] = self._timeColumn
        self._default_parameters["values_column"] = self._valuesColumn

        self.on_parameters_update(self._default_parameters)

        top.omegaChanged.connect(self.on_omega_update)
        top.timeStepChanged.connect(self.on_timeStep_update)
        top.startChanged.connect(self.on_start_update)
        top.endChanged.connect(self.on_end_update)

        self.showButton.clicked.connect(self.on_showButton_clicked)
        self.calculateButton.clicked.connect(self.on_calculateButton_clicked)

    @QtCore.pyqtSlot(str)
    def on_start_changed(self, x):
        panel = self.topPanel()
        panel.start.setText(x)
        self.on_start_update(x)

    @QtCore.pyqtSlot(str)
    def on_end_changed(self, x):
        panel = self.topPanel()
        panel.end.setText(x)
        self.on_end_update(x)

    @QtCore.pyqtSlot(str)
    def on_start_update(self, x):
        self.setParam("start_time", np.double(x))

    @QtCore.pyqtSlot(str)
    def on_end_update(self, x):
        self.setParam("end_time", np.double(x))

    @QtCore.pyqtSlot(str)
    def on_omega_update(self, x):
        self.setParam("omega", np.double(x))

    @QtCore.pyqtSlot(str)
    def on_timeStep_update(self, x):
        self.setParam("time_step", np.double(x))

    @QtCore.pyqtSlot()
    def on_showButton_clicked(self):
        self.fftWindow.updateItems()
        self.fftWindow.show()
    
    @QtCore.pyqtSlot()
    def on_calculateButton_clicked(self):
        super().on_calculateButton_clicked(init_value=1, handler=handler)

    @QtCore.pyqtSlot(list)
    def on_map_redraw(self, values):
        file_names = self.filenames()
        file_name_list = list(file_names.keys())

        first_param, second_param = zip(*list(map(lambda key: file_names[key], file_name_list)))
        first_param, second_param = sorted(list(set(first_param))), sorted(list(set(second_param)))
        first_param, second_param = list(map(lambda x: x[1], first_param)), list(map(lambda x: x[1], second_param))

        color_theme_path = os.path.join(".", "color_theme.json")
        color_theme = Helper.colors(color_theme_path)["hsa_map"]

        color_labels = list(color_theme.keys())
        color_values, color_hexes = zip(*list(map(lambda x: (x["value"], x["color"]), color_theme.values())))

        vmin = min(color_values) - 0.5 # left bound
        vmax = max(color_values) + 0.5 # right bound

        cmap = cl.ListedColormap(color_hexes)

        transposed_values = np.array(
            values, np.dtype([("file_name", "O"), ("osc_type", np.int32), ("omega", np.float32), ("freq", np.ndarray), ("fft", np.ndarray)])
        ).reshape((len(first_param), len(second_param))).T.reshape(-1)

        self.fftWindow.clearItems()

        for value in transposed_values:
            file_name, oscillation_type, omega, freq, fft = value
            self.fftWindow.addItem(file_name, (oscillation_type, (omega, freq, fft)))

        map_values = np.array([value[1] for value in values]).reshape((len(first_param), len(second_param))).T

        self.map_figure.clear()

        map_ax = self.map_figure.add_subplot(111)

        map_ax.set_xticks(list(range(len(first_param))), labels = first_param)
        map_ax.set_yticks(list(range(len(second_param))), labels = second_param)

        hLabel = self.horizontalLabel()
        vLabel = self.verticalLabel()

        map_ax.set_xlabel(fr'$\mathrm{{ {hLabel} }}$', fontsize=mpl.rcParams["font.size"])
        map_ax.set_ylabel(fr'$\mathrm{{ {vLabel} }}$', fontsize=mpl.rcParams["font.size"])

        im = map_ax.imshow(map_values, cmap = cmap, vmin = vmin, vmax = vmax, origin='lower')

        cbar = self.map_figure.colorbar(im)
        ticks_loc = cbar.ax.get_yticks().tolist()
        cbar.ax.yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        cbar.ax.set_yticklabels([''] + color_labels + [''])

        self.map.draw()