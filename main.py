# https://stackoverflow.com/questions/12459811/how-to-embed-matplotlib-in-pyqt-for-dummies

# import sys
# from PyQt6.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout

# from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
# import matplotlib.pyplot as plt

# import random

# class Window(QDialog):
#     def __init__(self, parent=None):
#         super(Window, self).__init__(parent)

#         # a figure instance to plot on
#         self.figure = plt.figure()

#         # this is the Canvas Widget that displays the `figure`
#         # it takes the `figure` instance as a parameter to __init__
#         self.canvas = FigureCanvas(self.figure)

#         # this is the Navigation widget
#         # it takes the Canvas widget and a parent

#         # Just some button connected to `plot` method
#         self.button = QPushButton('Plot')
#         self.button.clicked.connect(self.plot)

#         # set the layout
#         layout = QVBoxLayout()
#         layout.addWidget(self.canvas)
#         layout.addWidget(self.button)
#         self.setLayout(layout)

#     def plot(self):
#         ''' plot some random stuff '''
#         # random data
#         data = [random.random() for i in range(10)]

#         # instead of ax.hold(False)
#         self.figure.clear()

#         # create an axis
#         ax = self.figure.add_subplot(111)

#         # discards the old graph
#         # ax.hold(False) # deprecated, see above

#         # plot data
#         ax.plot(data, '*-')

#         # refresh canvas
#         self.canvas.draw()

# if __name__ == '__main__':
#     app = QApplication(sys.argv)

#     main = Window()
#     main.show()

#     sys.exit(app.exec())

import sys
from PyQt6.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import numpy as np

class Window(QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.signal_figure = plt.figure()
        self.fft_figure = plt.figure()

        self.signal_canvas = FigureCanvas(self.signal_figure)
        self.fft_canvas = FigureCanvas(self.fft_figure)

        self.button = QPushButton('Random plot')
        self.button.clicked.connect(self.random_plot)

        layout = QVBoxLayout()
        layout.addWidget(self.signal_canvas)
        layout.addWidget(self.fft_canvas)
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.signal_canvas.draw()
        self.fft_canvas.draw()
    
    def random_plot(self):
        data = np.loadtxt('5a2a7091-5f42-406a-8623-9acfa811ac37.txt')[500:1500,1]
        self.signal_figure.clear()
        signal_ax = self.signal_figure.add_subplot(111)
        signal_ax.plot(data)
        self.signal_canvas.draw()

        fft_data = np.abs(np.fft.fftshift(data))

        self.fft_figure.clear()
        fft_ax = self.fft_figure.add_subplot(111)
        fft_ax.plot(fft_data)
        self.fft_canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec())