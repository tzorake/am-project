from PyQt6 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.colors as cl
import matplotlib.ticker as mticker

from typing import Callable, List, Tuple

import multiprocessing
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

from utilities.helper import Helper


class CustomColors:
    WORKING = "#7dd3fc"
    RESULT = "#6ee7b7"
    ERROR = "#f9a8d4"


class Worker(QtCore.QObject):
    started = QtCore.pyqtSignal()
    progressChanged = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal(list)

    def __init__(self, init_value, target, args) -> None:
        super(Worker, self).__init__(None)

        self.init_value = init_value
        self.target, self.args = target, args

    def run(self):
        assert self.target is not None
        assert len(self.args) == 2

        self.started.emit()

        file_names = list(self.args[0].keys())
        
        params = self.args[1]
        n_files = len(file_names)

        print('Parameters: ', params)

        num_cores = multiprocessing.cpu_count()
        values = [self.init_value] * len(file_names)

        pbar = tqdm(total=n_files)

        with ProcessPoolExecutor(max_workers=num_cores) as executor:
            results = []

            for file_name in file_names:
                future = executor.submit(self.target, file_name, params)
                results.append(future)

            for idx, future in enumerate(results):
                result = future.result()
                values[idx] = result
                pbar.update()

                self.progressChanged.emit(int((idx + 1) / n_files * 100))

        self.finished.emit(values)


class CommonMapInterface(QtWidgets.QWidget):
    def __init__(self, topPanel = None, parent = None):
        super(CommonMapInterface, self).__init__(parent)

        self._topPanel = topPanel
        self._params = {}
        self._filenames = {}
        self.setupUi(topPanel)

    def topPanel(self):
        return self._topPanel
    
    def params(self):
        return self._params
    
    def setParams(self, params):
        self._params = params.copy()

    def setParam(self, key, value):
        self._params[key] = value

    def filenames(self):
        return self._filenames

    @QtCore.pyqtSlot(dict)
    def on_parameters_update(self, params: dict):
        self.setParams(params)

        for key in self.params().keys():
            param = params[key]
            field = self.field_mapping[key]
            field.setText(str(param))

    def setupUi(self, topPanel):
        self.setObjectName("CommonMapInterface")
        self.resize(874, 684)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        if (topPanel is None):
            topPanel = QtWidgets.QWidget()
        
        self.horizontalLayout_2.addWidget(topPanel)

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
        self.map.setMinimumSize(QtCore.QSize(600, 600))
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
        self.progressBar.setProperty("value", 0)
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

        self.retranslateUi()
    
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("CommonMapInterface", "CommonMapInterface"))
        self.saveButton.setText(_translate("CommonMapInterface", "Сохранить"))
        self.calculateButton.setText(_translate("CommonMapInterface", "Вычислить"))
        self.showButton.setText(_translate("CommonMapInterface", "Просмотр"))

    def resizeEvent(self, event):
        w = self.map.size().height()
        self.map.setMaximumWidth(w)

        QtWidgets.QWidget.resizeEvent(self, event)
    
    @QtCore.pyqtSlot(dict)
    def on_filenames_changed(self, filenames):
        self._filenames = filenames

    @QtCore.pyqtSlot()
    def on_showButton_clicked(self):
        raise NotImplementedError("Subclasses should implement this!")

    def on_calculateButton_clicked(self, init_value, handler=None):
        if handler is None:
            raise RuntimeError("Handler function is not defined yet!")

        self.worker_thread = QtCore.QThread()
        self.worker = Worker(init_value = init_value, target = handler, args = (self.filenames(), self.params()))
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.started.connect(self.on_worker_started)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker.progressChanged.connect(self.progressBar.setValue)
        self.worker_thread.start()
    
    @QtCore.pyqtSlot(list)
    def on_map_redraw(self, values):
        raise NotImplementedError("Subclasses should implement this!")

    @QtCore.pyqtSlot()
    def on_worker_started(self):
        self.progressBar.setValue(0)
        self.status.setStyleSheet(f"background-color: {CustomColors.WORKING}")
        self.showButton.setDisabled(True)
        self.calculateButton.setDisabled(True)

    @QtCore.pyqtSlot(list)
    def on_worker_finished(self, result):
        self.worker_thread.quit()
        self.on_map_redraw(result)

        self.status.setStyleSheet(f"background-color: {CustomColors.RESULT}")
        self.showButton.setDisabled(False)
        self.calculateButton.setDisabled(False)