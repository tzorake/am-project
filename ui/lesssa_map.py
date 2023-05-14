from PyQt6 import QtCore, QtGui, QtWidgets

import os
import numpy as np

from functools import reduce

import matplotlib.colors as cl
import matplotlib.ticker as mticker

from ui.common_map_interface import CommonMapInterface

from utilities.helper import Helper
from utilities.lesssa import LESSSA


def handler(file_name):
    start_time = 1700.0
    end_time = 1710.0
    e_dim = 4
    tau = 4
    iterations = 0
    eps_min = 0
    eps_step = 1.2
    min_neighbors = 30

    data = np.loadtxt(file_name)
    t, w = data[:, 0], data[:, 1]

    lesssa = LESSSA(e_dim, tau, iterations, eps_min, eps_step, min_neighbors)

    lesssa.set_data(t, w, start_time, end_time)
    sp_type, sp_exps = lesssa.evaluate()

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
        QtCore.QMetaObject.connectSlotsByName(self)

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
        validator6 = QtGui.QDoubleValidator()
        validator6.setLocale(locale)
        self.minNeigh.setValidator(validator6)

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
        self.interval.setTitle(_translate("LESSSTopPanel", "Интервал для расчетов"))
        self.label_4.setText(_translate("LESSSTopPanel", "Начало интервала"))
        self.label_5.setText(_translate("LESSSTopPanel", "Конец интервала"))


class LESSSAMap(CommonMapInterface):
    def __init__(self, parent = None):
        super(LESSSAMap, self).__init__(LESSSTopPanel(), parent)

        self.lesWindow = LESWindow(self)

        self.default_parameters = {
            "e_dim": 4,
            "tau": 4,
            "iterations": 0,
            "eps_min": 0,
            "eps_step": 1.2,
            "min_neighbors": 30
        }

        top = self.topPanel()
        self.field_mapping = {
            "e_dim": top.eDim,
            "tau": top.tau,
            "iterations": top.iterations,
            "eps_min": top.epsMin,
            "eps_step": top.epsStep,
            "min_neighbors": top.minNeigh
        }

        self.on_defaultParameters_setup(self.default_parameters)

        self.showButton.clicked.connect(self.on_showButton_clicked)
        self.calculateButton.clicked.connect(self.on_calculateButton_clicked)

    @QtCore.pyqtSlot(dict)
    def on_defaultParameters_setup(self, params: dict):
        for key in params.keys():
            param = self.default_parameters[key]
            field = self.field_mapping[key]
            field.setText(str(param))

    @QtCore.pyqtSlot(str)
    def on_start_changed(self, x):
        panel = self.topPanel()
        panel.start.setText(x)

    @QtCore.pyqtSlot(str)
    def on_end_changed(self, x):
        panel = self.topPanel()
        panel.end.setText(x)

    @QtCore.pyqtSlot()
    def on_showButton_clicked(self):
        self.lesWindow.updateItems()
        self.lesWindow.show()
    
    @QtCore.pyqtSlot()
    def on_calculateButton_clicked(self):
        super().on_calculateButton_clicked(init_value=-1, handler=handler)

    @QtCore.pyqtSlot(list)
    def on_map_redraw(self, values):
        file_names = list(map(lambda x: x[0], values))

        omega0 = sorted(list(set([Helper.get_omega0(file_name) for file_name in file_names])))
        a0_1 = sorted(list(set([Helper.get_a0_1(file_name) for file_name in file_names])))

        color_theme_path = os.path.join(".", "color_theme.json")
        color_theme = Helper.colors(color_theme_path)["lesssa_map"]

        color_labels = list(color_theme.keys())
        color_values, color_hexes = zip(*list(map(lambda x: (x["value"], x["color"]), color_theme.values())))

        vmin = min(color_values) - 0.5 # left bound
        vmax = max(color_values) + 0.5 # right bound

        cmap = cl.ListedColormap(color_hexes)

        transposed_values = np.array(
            values, np.dtype([('file_name', 'O'), ('sp_type', np.int32), ('sp_exps', np.ndarray)])
        ).reshape((len(omega0), len(a0_1))).T.reshape(-1)

        self.lesWindow.clearItems()

        for value in transposed_values:
            file_name, sp_type, sp_exps = value
            self.lesWindow.addItem(file_name, (sp_type, sp_exps))

        map_values = np.array([value[1] for value in values]).reshape((len(omega0), len(a0_1))).T

        self.map_figure.clear()
        map_ax = self.map_figure.add_subplot(111)
        map_ax.set_xticks(list(range(len(omega0))), labels = omega0)
        map_ax.set_yticks(list(range(len(a0_1))), labels = a0_1)
        im = map_ax.imshow(map_values, cmap = cmap, vmin = vmin, vmax = vmax, origin='lower')
        cbar = self.map_figure.colorbar(im)
        ticks_loc = cbar.ax.get_yticks().tolist()
        cbar.ax.yaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
        cbar.ax.set_yticklabels([''] + color_labels + [''])
        self.map.draw()