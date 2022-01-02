import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from View.PY.ui_Interface import Ui_MainWindow

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

maxi = 0


class TestAnimation(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton_4.clicked.connect(self.Animation)

        self.window().setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        # Top Bar
        self.ui.pushButton.clicked.connect(self.Maxmize)
        self.ui.pushButton_2.clicked.connect(self.Close)
        self.ui.pushButton_3.clicked.connect(self.Minimum)

    def Animation(self):
        global newWidth
        width = self.ui.slide_menu.width()
        print(width)
        if width == 0:
            newWidth = 273
        else:
            newWidth = 0


        self.animation = QPropertyAnimation(self.ui.slide_menu, b"maximumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(newWidth)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()

    def Maxmize(self):
        global maxi
        maxi += 1

        if maxi % 2 == 1:
            self.window().showMaximized()
        else:
            self.window().showNormal()

    def Minimum(self):
        self.window().showMinimized()

    def Close(self):
        self.window().close()


if __name__ == '__main__':
    newWidth = 0
    # Configurando Aplicação
    app = QApplication(sys.argv)
    window = TestAnimation()
    window.show()

    sys.exit(app.exec_())
