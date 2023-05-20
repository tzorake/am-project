from PyQt6 import QtCore, QtGui, QtWidgets

import os
import numpy as np

from functools import reduce

import matplotlib as mpl
import matplotlib.colors as cl
import matplotlib.ticker as mticker

from ui.common_map_interface import CommonMapInterface

from utilities.helper import Helper
from utilities.lesssa import LESSSA


def handler(file_name, params):
    start_time = params["start_time"]
    end_time = params["end_time"]
    e_dim = params["e_dim"]
    tau = params["tau"]
    iterations = params["iterations"]
    eps_min = params["eps_min"]
    eps_step = params["eps_step"]
    min_neighbors = params["min_neighbors"]
    gamma = params["gamma"]

    data = np.loadtxt(file_name)
    t, w = data[:, 0], data[:, 1]

    lesssa = LESSSA(e_dim, tau, iterations, eps_min, eps_step, min_neighbors)

    lesssa.set_data(t, w, start_time, end_time)
    sp_type, sp_exps = lesssa.evaluate(gamma)

    return file_name, sp_type, sp_exps


class LESItem(QtWidgets.QWidget):
    def __init__(self, fileName, spType, sp_coefs, parent = None):
        super(LESItem, self).__init__(parent)

        self.setObjectName("LESItem")
        self.resize(400, 168)
        self.setMinimumSize(QtCore.QSize(400, 0))
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.filename = QtWidgets.QLabel(parent=self)
        self.filename.setObjectName("filename")
        self.verticalLayout.addWidget(self.filename)
        self.les = QtWidgets.QTextEdit(parent=self)
        self.les.setEnabled(True)
        self.les.setMinimumSize(QtCore.QSize(0, 96))
        self.les.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByKeyboard|QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.les.setObjectName("les")
        self.verticalLayout.addWidget(self.les)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.type = QtWidgets.QWidget(parent=self)
        self.type.setMinimumSize(QtCore.QSize(24, 24))
        self.type.setMaximumSize(QtCore.QSize(24, 24))
        self.type.setStyleSheet("background-color: rgba(0, 0, 0, 255);")
        self.type.setObjectName("type")
        self.horizontalLayout_2.addWidget(self.type)
        self.name = QtWidgets.QLabel(parent=self)
        self.name.setObjectName("name")
        self.horizontalLayout_2.addWidget(self.name)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.filename.setText(fileName)
        self.les.setText(reduce(lambda acc, cur: acc + str(cur) + "\n", sp_coefs, ""))

        color_theme_path = os.path.join(".", "color_theme.json")
        color_theme = Helper.colors(color_theme_path)["lesssa_map"]

        color_values, color_hexes = zip(*list(map(lambda x: (x["value"], x["color"]), color_theme.values())))
        colors = dict(zip(color_values, color_hexes))
        color = colors[spType]
        color_key_mapping = dict(zip(color_values, list(color_theme.keys())))
        color_string = color_key_mapping[spType]

        self.type.setStyleSheet(f"background-color: {color}")
        self.name.setText(color_string)

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("ResultItem", "ResultItem"))


class LESWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(LESWindow, self).__init__(parent)

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
                widget.setParent(None)

        clearlayout(self.verticalLayout_2)

        for fileName, (sp_type, sp_coefs) in self.elements.items():
            item = LESItem(fileName, sp_type, sp_coefs)
            self.verticalLayout_2.addWidget(item)

    def clearItems(self):
        self.elements.clear()
    
    def addItem(self, key, value):
        self.elements[key] = value


class LESSSTopPanel(QtWidgets.QWidget):
    startChanged = QtCore.pyqtSignal(str)
    endChanged = QtCore.pyqtSignal(str)
    eDimChanged = QtCore.pyqtSignal(str)
    tauChanged = QtCore.pyqtSignal(str)
    iterationsChanged = QtCore.pyqtSignal(str)
    epsMinChanged = QtCore.pyqtSignal(str)
    epsStepChanged = QtCore.pyqtSignal(str)
    minNeighborsChanged = QtCore.pyqtSignal(str)
    gammaChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent = None):
        super(LESSSTopPanel, self).__init__(parent)
        self.setupUi()

        locale = QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates)
        locale.setNumberOptions(QtCore.QLocale.NumberOption.RejectGroupSeparator)
        validator = QtGui.QIntValidator()
        validator.setLocale(locale)
        self.eDim.setValidator(validator)
        validator2 = QtGui.QIntValidator()
        validator2.setLocale(locale)
        self.tau.setValidator(validator2)
        validator3 = QtGui.QIntValidator()
        validator3.setLocale(locale)
        self.iterations.setValidator(validator3)
        validator4 = QtGui.QDoubleValidator()
        validator4.setLocale(locale)
        self.epsMin.setValidator(validator4)
        validator5 = QtGui.QDoubleValidator()
        validator5.setLocale(locale)
        self.epsStep.setValidator(validator5)
        validator6 = QtGui.QIntValidator()
        validator6.setLocale(locale)
        self.minNeigh.setValidator(validator6)
        validator7 = QtGui.QDoubleValidator()
        validator7.setLocale(locale)
        self.gamma.setValidator(validator7)

        self.start.editingFinished.connect(self.on_start_finished)
        self.end.editingFinished.connect(self.on_end_finished)
        self.eDim.editingFinished.connect(self.on_eDim_finished)
        self.tau.editingFinished.connect(self.on_tau_finished)
        self.iterations.editingFinished.connect(self.on_iterations_finished)
        self.epsMin.editingFinished.connect(self.on_epsMin_finished)
        self.epsStep.editingFinished.connect(self.on_epsStep_finished)
        self.minNeigh.editingFinished.connect(self.on_minNeighbors_finished)
        self.gamma.editingFinished.connect(self.on_gamma_finished)

    def setupUi(self):
        self.setObjectName("LESSSTopPanel")
        self.resize(870, 138)
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
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.parameters)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(parent=self.parameters)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.eDim = QtWidgets.QLineEdit(parent=self.parameters)
        self.eDim.setMinimumSize(QtCore.QSize(100, 0))
        self.eDim.setMaximumSize(QtCore.QSize(100, 16777215))
        self.eDim.setObjectName("eDim")
        self.horizontalLayout_2.addWidget(self.eDim)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(parent=self.parameters)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.tau = QtWidgets.QLineEdit(parent=self.parameters)
        self.tau.setMinimumSize(QtCore.QSize(100, 20))
        self.tau.setMaximumSize(QtCore.QSize(100, 20))
        self.tau.setObjectName("tau")
        self.horizontalLayout_3.addWidget(self.tau)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(parent=self.parameters)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.iterations = QtWidgets.QLineEdit(parent=self.parameters)
        self.iterations.setEnabled(True)
        self.iterations.setMinimumSize(QtCore.QSize(100, 20))
        self.iterations.setMaximumSize(QtCore.QSize(100, 20))
        self.iterations.setFrame(True)
        self.iterations.setObjectName("iterations")
        self.horizontalLayout_4.addWidget(self.iterations)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_8.addLayout(self.verticalLayout_4)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_7 = QtWidgets.QLabel(parent=self.parameters)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_9.addWidget(self.label_7)
        self.epsMin = QtWidgets.QLineEdit(parent=self.parameters)
        self.epsMin.setMinimumSize(QtCore.QSize(100, 20))
        self.epsMin.setMaximumSize(QtCore.QSize(100, 20))
        self.epsMin.setObjectName("epsMin")
        self.horizontalLayout_9.addWidget(self.epsMin)
        self.verticalLayout_5.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_8 = QtWidgets.QLabel(parent=self.parameters)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_10.addWidget(self.label_8)
        self.epsStep = QtWidgets.QLineEdit(parent=self.parameters)
        self.epsStep.setMinimumSize(QtCore.QSize(100, 20))
        self.epsStep.setMaximumSize(QtCore.QSize(100, 20))
        self.epsStep.setObjectName("epsStep")
        self.horizontalLayout_10.addWidget(self.epsStep)
        self.verticalLayout_5.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_9 = QtWidgets.QLabel(parent=self.parameters)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_11.addWidget(self.label_9)
        self.minNeigh = QtWidgets.QLineEdit(parent=self.parameters)
        self.minNeigh.setMinimumSize(QtCore.QSize(100, 20))
        self.minNeigh.setMaximumSize(QtCore.QSize(100, 20))
        self.minNeigh.setObjectName("minNeigh")
        self.horizontalLayout_11.addWidget(self.minNeigh)
        self.verticalLayout_5.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_8.addLayout(self.verticalLayout_5)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_10 = QtWidgets.QLabel(parent=self.parameters)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_12.addWidget(self.label_10)
        self.gamma = QtWidgets.QLineEdit(parent=self.parameters)
        self.gamma.setMinimumSize(QtCore.QSize(100, 20))
        self.gamma.setMaximumSize(QtCore.QSize(100, 20))
        self.gamma.setObjectName("gamma")
        self.horizontalLayout_12.addWidget(self.gamma)
        self.verticalLayout_6.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_11 = QtWidgets.QLabel(parent=self.parameters)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_13.addWidget(self.label_11)
        self.placeholder = QtWidgets.QLineEdit(parent=self.parameters)
        self.placeholder.setEnabled(False)
        self.placeholder.setMinimumSize(QtCore.QSize(100, 20))
        self.placeholder.setMaximumSize(QtCore.QSize(100, 20))
        self.placeholder.setFrame(False)
        self.placeholder.setObjectName("placeholder")
        self.horizontalLayout_13.addWidget(self.placeholder)
        self.verticalLayout_6.addLayout(self.horizontalLayout_13)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_12 = QtWidgets.QLabel(parent=self.parameters)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_14.addWidget(self.label_12)
        self.placeholder2 = QtWidgets.QLineEdit(parent=self.parameters)
        self.placeholder2.setEnabled(False)
        self.placeholder2.setMinimumSize(QtCore.QSize(100, 20))
        self.placeholder2.setMaximumSize(QtCore.QSize(100, 20))
        self.placeholder2.setFrame(False)
        self.placeholder2.setObjectName("placeholder2")
        self.horizontalLayout_14.addWidget(self.placeholder2)
        self.verticalLayout_6.addLayout(self.horizontalLayout_14)
        self.horizontalLayout_8.addLayout(self.verticalLayout_6)
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
        self.start.setObjectName("start")
        self.start.setValidator(validator)
        self.horizontalLayout_5.addWidget(self.start)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_5 = QtWidgets.QLabel(parent=self.interval)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_6.addWidget(self.label_5)
        validator2 = QtGui.QDoubleValidator()
        validator2.setLocale(locale)
        self.end = QtWidgets.QLineEdit(parent=self.interval)
        self.end.setMinimumSize(QtCore.QSize(100, 20))
        self.end.setMaximumSize(QtCore.QSize(100, 20))
        self.end.setObjectName("end")
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
        self.setWindowTitle(_translate("LESSSTopPanel", "LESSSTopPanel"))
        self.parameters.setTitle(_translate("LESSSTopPanel", "Параметры"))
        self.label.setText(_translate("LESSSTopPanel", "Размер встраивания"))
        self.label_2.setText(_translate("LESSSTopPanel", "Задержка восстановления"))
        self.label_3.setText(_translate("LESSSTopPanel", "Количество итераций"))
        self.label_7.setText(_translate("LESSSTopPanel", "Начальный размер окрестности"))
        self.label_8.setText(_translate("LESSSTopPanel", "Коэффициент увеличения окрестности"))
        self.label_9.setText(_translate("LESSSTopPanel", "Размер окрестности"))
        self.label_10.setText(_translate("LESSSTopPanel", "Коэффициент зануление"))
        self.interval.setTitle(_translate("LESSSTopPanel", "Интервал для расчетов"))
        self.label_4.setText(_translate("LESSSTopPanel", "Начало интервала"))
        self.label_5.setText(_translate("LESSSTopPanel", "Конец интервала"))

    @QtCore.pyqtSlot()
    def on_start_finished(self):
        x = self.start.text()
        self.startChanged.emit(x)

    @QtCore.pyqtSlot()
    def on_end_finished(self):
        x = self.end.text()
        self.endChanged.emit(x)

    @QtCore.pyqtSlot()
    def on_eDim_finished(self):
        x = self.eDim.text()
        self.eDimChanged.emit(x)
    
    @QtCore.pyqtSlot()
    def on_tau_finished(self):
        x = self.tau.text()
        self.tauChanged.emit(x)

    @QtCore.pyqtSlot()
    def on_iterations_finished(self):
        x = self.iterations.text()
        self.iterationsChanged.emit(x)

    @QtCore.pyqtSlot()
    def on_epsMin_finished(self):
        x = self.epsMin.text()
        self.epsMinChanged.emit(x)

    @QtCore.pyqtSlot()
    def on_epsStep_finished(self):
        x = self.epsStep.text()
        self.epsStepChanged.emit(x)

    @QtCore.pyqtSlot()
    def on_minNeighbors_finished(self):
        x = self.minNeigh.text()
        self.minNeighborsChanged.emit(x)

    @QtCore.pyqtSlot()
    def on_gamma_finished(self):
        print("on_gamma_finished")
        x = self.gamma.text()
        self.gammaChanged.emit(x)

class LESSSAMap(CommonMapInterface):
    def __init__(self, parent = None):
        super(LESSSAMap, self).__init__(LESSSTopPanel(), parent)

        self.lesWindow = LESWindow(self)
        top = self.topPanel()

        self.default_parameters = {
            "start_time": 0.0,
            "end_time": 0.0,
            "e_dim": 4,
            "tau": 4,
            "iterations": 0,
            "eps_min": 0,
            "eps_step": 1.2,
            "min_neighbors": 30,
            "gamma": 0.001
        }
        self.field_mapping = {
            "start_time": top.start,
            "end_time": top.end,
            "e_dim": top.eDim,
            "tau": top.tau,
            "iterations": top.iterations,
            "eps_min": top.epsMin,
            "eps_step": top.epsStep,
            "min_neighbors": top.minNeigh,
            "gamma": top.gamma
        }

        self.on_parameters_update(self.default_parameters)

        top.startChanged.connect(self.on_start_update)
        top.endChanged.connect(self.on_end_update)
        top.eDimChanged.connect(self.on_eDim_update)
        top.tauChanged.connect(self.on_tau_update)
        top.iterationsChanged.connect(self.on_iterations_update)
        top.epsMinChanged.connect(self.on_epsMin_update)
        top.epsStepChanged.connect(self.on_epsStep_update)
        top.minNeighborsChanged.connect(self.on_minNeighbors_update)
        top.gammaChanged.connect(self.on_gamma_update)

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
    def on_eDim_update(self, x):
        self.setParam("e_dim", np.int64(x))

    @QtCore.pyqtSlot(str)
    def on_tau_update(self, x):
        self.setParam("tau", np.int64(x))

    @QtCore.pyqtSlot(str)
    def on_iterations_update(self, x):
        self.setParam("iterations", np.int64(x))
    
    @QtCore.pyqtSlot(str)
    def on_epsMin_update(self, x):
        self.setParam("eps_min", np.double(x))
    
    @QtCore.pyqtSlot(str)
    def on_epsStep_update(self, x):
        self.setParam("eps_step", np.double(x))

    @QtCore.pyqtSlot(str)
    def on_minNeighbors_update(self, x):
        self.setParam("min_neighbors", np.int64(x))

    @QtCore.pyqtSlot(str)
    def on_gamma_update(self, x):
        self.setParam("gamma", np.double(x))

    @QtCore.pyqtSlot()
    def on_showButton_clicked(self):
        self.lesWindow.updateItems()
        self.lesWindow.show()
    
    @QtCore.pyqtSlot()
    def on_calculateButton_clicked(self):
        super().on_calculateButton_clicked(init_value=-1, handler=handler)

    @QtCore.pyqtSlot(list)
    def on_map_redraw(self, values):
        file_names = self.filenames()
        file_name_list = list(file_names.keys())

        first_param, second_param = zip(*list(map(lambda key: file_names[key], file_name_list)))
        first_param, second_param = sorted(list(set(first_param))), sorted(list(set(second_param)))
        first_param, second_param = list(map(lambda x: x[1], first_param)), list(map(lambda x: x[1], second_param))

        color_theme_path = os.path.join(".", "color_theme.json")
        color_theme = Helper.colors(color_theme_path)["lesssa_map"]

        color_labels = list(color_theme.keys())
        color_values, color_hexes = zip(*list(map(lambda x: (x["value"], x["color"]), color_theme.values())))

        vmin = min(color_values) - 0.5 # left bound
        vmax = max(color_values) + 0.5 # right bound

        cmap = cl.ListedColormap(color_hexes)

        transposed_values = np.array(
            values, np.dtype([('file_name', 'O'), ('sp_type', np.int32), ('sp_exps', np.ndarray)])
        ).reshape((len(first_param), len(second_param))).T.reshape(-1)

        self.lesWindow.clearItems()

        for value in transposed_values:
            file_name, sp_type, sp_exps = value
            self.lesWindow.addItem(file_name, (sp_type, sp_exps))

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