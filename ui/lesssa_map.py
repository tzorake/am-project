from PyQt6 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.colors as cl
import matplotlib.ticker as mticker

from utilities.helper import Helper
from utilities.lesssa import LESSSA

import os
import numpy as np
from tqdm import tqdm
from functools import reduce
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

def handler(file_name):
    start_time = 1700.0
    end_time = 1710.0

    data = np.loadtxt(file_name)
    t, w = data[:, 0], data[:, 1]

    lesssa = LESSSA(4, 4, 0, 0, 1.2, 30)

    lesssa.set_data(t, w, start_time, end_time)
    sp_type, sp_exps = lesssa.evaluate()

    return file_name, sp_type, sp_exps


class ResultItem(QtWidgets.QWidget):
    def __init__(self, fileName, spType, sp_coefs, parent = None):
        super(ResultItem, self).__init__(parent)

        self.setObjectName("ResultItem")
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


class ResultWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super(ResultWindow, self).__init__(parent)

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
        self.updateItems()

    def updateItems(self):
        def clearlayout(layout):
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                widget = item.widget()
                layout.removeItem(item)
                widget.setParent(None)

        clearlayout(self.verticalLayout_2)

        for fileName, (sp_type, sp_coefs) in self.elements.items():
            item = ResultItem(fileName, sp_type, sp_coefs)
            self.verticalLayout_2.addWidget(item)

    def clearItems(self):
        self.elements.clear()
    
    def addItem(self, key, value):
        self.elements[key] = value


class LESSSAMap(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(LESSSAMap, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("LESSSAMap")
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
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_5.addWidget(self.label_2)
        self.lineEdit_5 = QtWidgets.QLineEdit(parent=self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_5.sizePolicy().hasHeightForWidth())
        self.lineEdit_5.setSizePolicy(sizePolicy)
        self.lineEdit_5.setMinimumSize(QtCore.QSize(100, 0))
        self.lineEdit_5.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.horizontalLayout_5.addWidget(self.lineEdit_5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_6 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_9.addWidget(self.label_6)
        self.lineEdit_2 = QtWidgets.QLineEdit(parent=self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_2.sizePolicy().hasHeightForWidth())
        self.lineEdit_2.setSizePolicy(sizePolicy)
        self.lineEdit_2.setMinimumSize(QtCore.QSize(100, 0))
        self.lineEdit_2.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout_9.addWidget(self.lineEdit_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_4 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_7.addWidget(self.label_4)
        self.lineEdit_4 = QtWidgets.QLineEdit(parent=self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_4.sizePolicy().hasHeightForWidth())
        self.lineEdit_4.setSizePolicy(sizePolicy)
        self.lineEdit_4.setMinimumSize(QtCore.QSize(100, 0))
        self.lineEdit_4.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.horizontalLayout_7.addWidget(self.lineEdit_4)
        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_5 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_8.addWidget(self.label_5)
        self.lineEdit_6 = QtWidgets.QLineEdit(parent=self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_6.sizePolicy().hasHeightForWidth())
        self.lineEdit_6.setSizePolicy(sizePolicy)
        self.lineEdit_6.setMinimumSize(QtCore.QSize(100, 0))
        self.lineEdit_6.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.horizontalLayout_8.addWidget(self.lineEdit_6)
        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
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
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_18.addWidget(self.label_9)
        self.lineEdit_9 = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.lineEdit_9.setEnabled(False)
        self.lineEdit_9.setMinimumSize(QtCore.QSize(100, 0))
        self.lineEdit_9.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEdit_9.setAutoFillBackground(False)
        self.lineEdit_9.setFrame(False)
        self.lineEdit_9.setClearButtonEnabled(True)
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
        self.map_figure = plt.figure()
        self.map = FigureCanvas(self.map_figure)
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
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.saveButton = QtWidgets.QPushButton(parent=self)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout_13.addWidget(self.saveButton)
        self.status = QtWidgets.QWidget(parent=self)
        self.status.setMinimumSize(QtCore.QSize(22, 22))
        self.status.setMaximumSize(QtCore.QSize(22, 22))
        self.status.setStyleSheet("background-color: #ffffff")
        self.status.setObjectName("status")
        self.horizontalLayout_13.addWidget(self.status)
        self.horizontalLayout_12.addLayout(self.horizontalLayout_13)
        self.progressBar = QtWidgets.QProgressBar(parent=self)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout_12.addWidget(self.progressBar)
        self.showButton = QtWidgets.QPushButton(parent=self)
        self.showButton.setObjectName("showButton")
        self.horizontalLayout_12.addWidget(self.showButton)
        self.calculateButton = QtWidgets.QPushButton(parent=self)
        self.calculateButton.setObjectName("calculateButton")
        self.horizontalLayout_12.addWidget(self.calculateButton)
        self.verticalLayout.addLayout(self.horizontalLayout_12)
        self.verticalLayout.setStretch(1, 1)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.resultWindow = ResultWindow(self)

        self.retranslateUi()
        self.calculateButton.clicked.connect(self.on_calculateButton_clicked)
        self.showButton.clicked.connect(self.on_showButton_clicked)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("LESSSAMap", "LESSSAMap"))
        self.groupBox.setTitle(_translate("LESSSAMap", "Параметры"))
        self.label_3.setText(_translate("LESSSAMap", "Размер встраивания"))
        self.label.setText(_translate("LESSSAMap", "Задержка восстановления"))
        self.label_2.setText(_translate("LESSSAMap", "Количество итераций"))
        self.label_6.setText(_translate("LESSSAMap", "Начальный размер окрестности"))
        self.label_4.setText(_translate("LESSSAMap", "Коэффициент увеличения окрестности"))
        self.label_5.setText(_translate("LESSSAMap", "Размер окрестности"))
        self.groupBox_2.setTitle(_translate("LESSSAMap", "Интервал для расчетов"))
        self.label_7.setText(_translate("LESSSAMap", "Начало интервала"))
        self.label_8.setText(_translate("LESSSAMap", "Конец интервала"))
        self.label_9.setText(_translate("LESSSAMap", " "))
        self.saveButton.setText(_translate("LESSSAMap", "Сохранить"))
        self.calculateButton.setText(_translate("LESSSAMap", "Вычислить"))
        self.showButton.setText(_translate("LESSSAMap", "Просмотр"))

    def resizeEvent(self, event):
        w = self.map.size().height()
        self.map.setMaximumWidth(w)

        QtWidgets.QWidget.resizeEvent(self, event)

    def on_showButton_clicked(self):
        self.resultWindow.updateItems()
        self.resultWindow.show()

    def on_calculateButton_clicked(self):
        file_names = Helper.get_file_names('.')
        n_files = len(file_names)

        omega0 = sorted(list(set([Helper.get_omega0(file_name) for file_name in file_names])))
        a0_1 = sorted(list(set([Helper.get_a0_1(file_name) for file_name in file_names])))

        num_cores = multiprocessing.cpu_count()
        values = [-1] * len(file_names)

        pbar = tqdm(total=n_files)

        with ProcessPoolExecutor(max_workers=num_cores) as executor:
            results = []

            for file_name in file_names:
                future = executor.submit(handler, file_name)
                results.append(future)

            for idx, future in enumerate(results):
                result = future.result()
                values[idx] = result
                pbar.update()

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

        self.resultWindow.clearItems()

        for value in transposed_values:
            file_name, sp_type, sp_exps = value
            self.resultWindow.addItem(file_name, (sp_type, sp_exps))

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