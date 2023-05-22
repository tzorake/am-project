from PyQt6 import QtCore, QtGui, QtWidgets

import os
import re
import numpy as np

class Settings(QtWidgets.QWidget):
    folderPathTextChanged = QtCore.pyqtSignal(str)
    startChanged = QtCore.pyqtSignal(str)
    endChanged = QtCore.pyqtSignal(str)
    filenamesChanged = QtCore.pyqtSignal(dict)
    horizontalLabelChanged = QtCore.pyqtSignal(str)
    verticalLabelChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent = None):
        super(Settings, self).__init__(parent)
        self.setupUi()

        self.folderPath.textChanged.connect(self.on_folderPath_textChanged)
        self.openButton.clicked.connect(self.openFolder)
        self.checkButton.clicked.connect(self.checkParams)
        self.labelsCheckbox.stateChanged.connect(self.enableLabels)
        self.start.textChanged.connect(self.on_start_changed)
        self.end.textChanged.connect(self.on_end_changed)
        self.horizontalLabel.textChanged.connect(self.on_horizontalLabel_changed)
        self.verticalLabel.textChanged.connect(self.on_verticalLabel_changed)


    @QtCore.pyqtSlot(str)
    def on_start_changed(self):
        v = self.start.text()
        self.startChanged.emit(v)

    @QtCore.pyqtSlot(str)
    def on_end_changed(self):
        v = self.end.text()
        self.endChanged.emit(v)

    @QtCore.pyqtSlot(str)
    def on_horizontalLabel_changed(self):
        v = self.horizontalLabel.text()
        self.horizontalLabelChanged.emit(v)

    @QtCore.pyqtSlot(str)
    def on_verticalLabel_changed(self):
        v = self.verticalLabel.text()
        self.verticalLabelChanged.emit(v)

    def setupUi(self):
        self.setObjectName("Settings")
        self.resize(591, 730)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(9, -1, 9, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(parent=self)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.folderPath = QtWidgets.QLineEdit(parent=self)
        self.folderPath.setObjectName("folderPath")
        self.horizontalLayout.addWidget(self.folderPath)
        self.openButton = QtWidgets.QPushButton(parent=self)
        self.openButton.setObjectName("openButton")
        self.horizontalLayout.addWidget(self.openButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.groupBox = QtWidgets.QGroupBox(parent=self)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pattern = QtWidgets.QLineEdit(parent=self.groupBox)
        self.pattern.setObjectName("pattern")
        self.horizontalLayout_2.addWidget(self.pattern)
        self.checkButton = QtWidgets.QPushButton(parent=self.groupBox)
        self.checkButton.setObjectName("checkButton")
        self.horizontalLayout_2.addWidget(self.checkButton)
        self.verticalLayout_7.addLayout(self.horizontalLayout_2)
        self.found = QtWidgets.QLabel(text="", parent=self.groupBox)
        self.found.setObjectName("found")
        self.verticalLayout_7.addWidget(self.found)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(parent=self)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_3.setMinimumSize(QtCore.QSize(150, 0))
        self.label_3.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.timeColumn = QtWidgets.QComboBox(parent=self.groupBox_2)
        self.timeColumn.setMinimumSize(QtCore.QSize(50, 0))
        self.timeColumn.setMaximumSize(QtCore.QSize(50, 16777215))
        self.timeColumn.setObjectName("timeColumn")
        self.horizontalLayout_4.addWidget(self.timeColumn)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_4 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_4.setMinimumSize(QtCore.QSize(150, 0))
        self.label_4.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_5.addWidget(self.label_4)
        self.valuesColumn = QtWidgets.QComboBox(parent=self.groupBox_2)
        self.valuesColumn.setMinimumSize(QtCore.QSize(50, 0))
        self.valuesColumn.setMaximumSize(QtCore.QSize(50, 16777215))
        self.valuesColumn.setObjectName("valuesColumn")
        self.horizontalLayout_5.addWidget(self.valuesColumn)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_5 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_5.setMinimumSize(QtCore.QSize(175, 0))
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_6.addWidget(self.label_5)
        validator = QtGui.QDoubleValidator()
        locale = QtCore.QLocale(QtCore.QLocale.Language.English, QtCore.QLocale.Country.UnitedStates)
        locale.setNumberOptions(QtCore.QLocale.NumberOption.RejectGroupSeparator)
        validator.setLocale(locale)
        self.start = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.start.setMinimumSize(QtCore.QSize(100, 0))
        self.start.setMaximumSize(QtCore.QSize(100, 16777215))
        self.start.setObjectName("start")
        self.start.setValidator(validator)
        self.horizontalLayout_6.addWidget(self.start)
        self.verticalLayout_4.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_6 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_6.setMinimumSize(QtCore.QSize(175, 0))
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_7.addWidget(self.label_6)
        validator2 = QtGui.QDoubleValidator()
        validator2.setLocale(locale)
        self.end = QtWidgets.QLineEdit(parent=self.groupBox_2)
        self.end.setMinimumSize(QtCore.QSize(100, 0))
        self.end.setMaximumSize(QtCore.QSize(100, 16777215))
        self.end.setObjectName("end")
        self.start.setValidator(validator2)
        self.horizontalLayout_7.addWidget(self.end)
        self.verticalLayout_4.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.horizontalLayout_3.setStretch(3, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(parent=self)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setSpacing(6)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.labelsCheckbox = QtWidgets.QCheckBox(parent=self.groupBox_3)
        self.labelsCheckbox.setObjectName("labelsCheckbox")
        self.verticalLayout_6.addWidget(self.labelsCheckbox)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_8 = QtWidgets.QLabel(parent=self.groupBox_3)
        self.label_8.setMinimumSize(QtCore.QSize(150, 0))
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_9.addWidget(self.label_8)
        self.horizontalLabel = QtWidgets.QLineEdit(parent=self.groupBox_3)
        self.horizontalLabel.setMinimumSize(QtCore.QSize(0, 0))
        self.horizontalLabel.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.horizontalLabel.setObjectName("horizontalLabel")
        self.horizontalLabel.setEnabled(False)
        self.horizontalLayout_9.addWidget(self.horizontalLabel)
        self.verticalLayout_6.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_7 = QtWidgets.QLabel(parent=self.groupBox_3)
        self.label_7.setMinimumSize(QtCore.QSize(150, 0))
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_8.addWidget(self.label_7)
        self.verticalLabel = QtWidgets.QLineEdit(parent=self.groupBox_3)
        self.verticalLabel.setMinimumSize(QtCore.QSize(0, 0))
        self.verticalLabel.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLabel.setObjectName("verticalLabel")
        self.verticalLabel.setEnabled(False)
        self.horizontalLayout_8.addWidget(self.verticalLabel)
        self.verticalLayout_6.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_10.addLayout(self.verticalLayout_6)
        self.verticalLayout_5.addLayout(self.horizontalLayout_10)
        self.verticalLayout.addWidget(self.groupBox_3)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem2)

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Settings", "Settings"))
        self.label.setText(_translate("Settings", "Открыть папку"))
        self.openButton.setText(_translate("Settings", "Обзор"))
        self.groupBox.setTitle(_translate("Settings", "Шаблон названия файла"))
        self.pattern.setText("signal_{omega0=.}_{a0_1=.}.txt")
        self.checkButton.setText(_translate("Settings", "Проверить"))
        self.groupBox_2.setTitle(_translate("Settings", "Номера столбцов и временные границы"))
        self.label_3.setText(_translate("Settings", "Номер столбца времени"))
        self.label_4.setText(_translate("Settings", "Номер столбца значений"))
        self.label_5.setText(_translate("Settings", "Начало временного интервала"))
        self.label_6.setText(_translate("Settings", "Конец временного интервала"))
        self.groupBox_3.setTitle(_translate("Settings", "Метки осей"))
        self.labelsCheckbox.setText(_translate("Settings", "Включить отображение меток на осях"))
        self.label_8.setText(_translate("Settings", "Горизонтальная ось"))
        self.label_7.setText(_translate("Settings", "Вертикальная ось"))

    def on_folderPath_textChanged(self):
        v = self.folderPath.text()
        self.folderPathTextChanged.emit(v)

    def openFolder(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")

        if os.path.exists(path):
            self.folderPath.setText(path)

    def checkParams(self):
        path = self.folderPath.text()
        pattern = self.pattern.text()

        param = "\{[^\}]*\}"
        
        def get_dec_point(s):
            return s[-1] if len(s) > 1 else ""

        def get_equal(s):
            return s[-2] if len(s) > 2 else ""

        def strip(s):
            return s[1:-1] if len(s) > 2 else ""

        def handle_param(param: str, equal: str, dec_point: str):
            key, value = param.split(equal)

            value = float(value.replace(dec_point, "."))

            return key, value

        if (len(pattern) != 0):
            matches = re.findall(param, pattern)
            pattern_with_repl = pattern[:]

            for match in matches:
                striped_match = strip(match)

                equal = get_equal(striped_match)
                dec_point = get_dec_point(striped_match)

                has_equal = False
                has_dec_point = False

                if len(equal) > 0:
                    has_equal = True
                
                if len(dec_point) > 0:
                    has_dec_point = True

                offset = (1 if has_equal else 0) + (1 if has_dec_point else 0)
                symbol = striped_match[:-offset] if offset > 0 else striped_match
                replacement = f"({symbol}{equal}[+-]?(?:[0-9]*[{dec_point}])?[0-9]+)"
                pattern_with_repl = pattern_with_repl.replace(match, replacement)
                
            if os.path.exists(path):
                files = os.listdir(path)

                if len(files) > 0:
                    filenames = {}

                    for file in files:
                        if os.path.isfile(os.path.join(path, file)):
                            matches = re.findall(pattern_with_repl, file)

                            if len(matches) == 1 and len(matches[0]) == 2:
                                first, second = matches[0]

                                first_param = handle_param(first, equal, dec_point)
                                second_param = handle_param(second, equal, dec_point)

                                filename = os.path.normpath(os.path.join(path, file))

                                filenames[filename] = (first_param, second_param)

                    self.found.setText(f"Найдено: {len(filenames)}")
                    self.found.setVisible(True)

                    keys = list(filenames.keys())
                    first_filename = keys[0]
                    data = np.loadtxt(os.path.join(path, first_filename))
                    shape = data.shape

                    self.timeColumn.addItems(list(map(lambda x: str(x), range(shape[1]))))
                    self.valuesColumn.addItems(list(map(lambda x: str(x), range(shape[1]))))
                    self.valuesColumn.setCurrentIndex(1)

                    self.start.setText(str(data[0, 0]))
                    self.end.setText(str(data[-1, 0]))

                    self.filenamesChanged.emit(filenames)

    def enableLabels(self):
        self.horizontalLabel.setEnabled(not self.horizontalLabel.isEnabled())
        self.verticalLabel.setEnabled(not self.verticalLabel.isEnabled())