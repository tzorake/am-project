from PyQt6 import QtCore, QtGui, QtWidgets

class TabBar(QtWidgets.QTabBar):
    def tabSizeHint(self, index):
        s = super().tabSizeHint(index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QtWidgets.QStyle.ControlElement.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QtWidgets.QStyle.ControlElement.CE_TabBarTabLabel, opt)
            painter.restore()

    def __init__(self, parent = None):
        super().__init__(parent)

class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        tabBar = TabBar()
        self.setTabBar(tabBar)
        self.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
