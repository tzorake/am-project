from PyQt6 import QtCore, QtGui, QtWidgets

from ui.tabs import TabWidget
from ui.settings import Settings
from ui.hsa_map import HSAMap
from ui.lesssa_map import LESSSAMap
from ui.information import Information

import resources

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi()
        self.setWindowIcon(QtGui.QIcon(":/icons/icon.png"))

        self.tab.startChanged.connect(self.tab_2.on_start_changed)
        self.tab.endChanged.connect(self.tab_2.on_end_changed)
        self.tab.filenamesChanged.connect(self.tab_2.on_filenames_changed)
        self.tab.horizontalLabelChanged.connect(self.tab_2.on_horizontalLabel_changed)
        self.tab.verticalLabelChanged.connect(self.tab_2.on_verticalLabel_changed)
        self.tab.folderPathTextChanged.connect(self.tab_2.on_folderPath_textChanged)

        self.tab.startChanged.connect(self.tab_3.on_start_changed)
        self.tab.endChanged.connect(self.tab_3.on_end_changed)
        self.tab.filenamesChanged.connect(self.tab_3.on_filenames_changed)
        self.tab.horizontalLabelChanged.connect(self.tab_3.on_horizontalLabel_changed)
        self.tab.verticalLabelChanged.connect(self.tab_3.on_verticalLabel_changed)
        self.tab.folderPathTextChanged.connect(self.tab_3.on_folderPath_textChanged)
    
    def setupUi(self):
        self.setObjectName("AMP")
        self.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent=self)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = TabWidget(parent=self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = Settings()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = HSAMap()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = LESSSAMap()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = Information()
        self.tab_4.setObjectName("tab_4")
        self.tabWidget.addTab(self.tab_4, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.setCentralWidget(self.centralwidget)

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("AMP", "AMP"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("AMP", "Настройки"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("AMP", "HSAM"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("AMP", "LESSSAM"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("AMP", "Информация"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec())
