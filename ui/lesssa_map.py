from PyQt6 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from utilities.helper import Helper
from utilities.lesssa import LESSSA

import numpy as np
from tqdm import tqdm

class LESSSAMap(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(LESSSAMap, self).__init__(parent)

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

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalLayout.setStretch(0, 20)
        self.verticalLayout.setStretch(2, 1)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.setLayout(self.horizontalLayout)
 
        self.lesssa = LESSSA(4, 4, 0, 0, 1.2, 30)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.calculateButton.setText(_translate("MainWindow", "Calculate"))
 
    def on_calculateButton_clicked(self):
        file_names = Helper.get_file_names('.')

        omega0 = sorted(list(set([Helper.get_omega0(file_name) for file_name in file_names])))
        a0_1 = sorted(list(set([Helper.get_a0_1(file_name) for file_name in file_names])))

        values = [[0] * len(omega0) for _ in range(len(a0_1))]

        start_time = 1700.0
        end_time = 1701.0

        for file_name in tqdm(file_names):
            omega0_value = Helper.get_omega0(file_name)
            a0_1_value = Helper.get_a0_1(file_name)

            data = np.loadtxt(file_name)
            t, w = data[:, 0], data[:, 1]

            self.lesssa.set_data(t, w, start_time, end_time)
            sp_type = self.lesssa.evaluate()

            i = omega0.index(omega0_value)
            j = a0_1.index(a0_1_value)

            values[i][j] = sp_type

        self.map_figure.clear()
        map_ax = self.map_figure.add_subplot(111)
        map_ax.set_xticks(list(range(len(omega0))), labels = omega0)
        map_ax.set_yticks(list(range(len(a0_1))), labels = a0_1)
        map_ax.imshow(values)
        for i in range(len(omega0)):
            for j in range(len(a0_1)):
                map_ax.text(j, i, round(values[i][j], 1), ha = "center", va = "center", color = "black")

        self.map.draw()


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = LESSSAMap()
    main.show()
    sys.exit(app.exec())
 
if __name__ == '__main__':
    main()