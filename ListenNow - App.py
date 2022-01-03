import sys
import mysql.connector
import sqlite3

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from View.PY.ui_Interface import Ui_MainWindow
from tkinter.filedialog import askdirectory, askopenfilenames
from tkinter import Tk

maxi = 0
newWidth = 0
musics = None

bank = sqlite3.connect('bank_music')

cursor = bank.cursor()


class ListenNow(QMainWindow):

    def __init__(self):
        global musics

        # Loading Songs
        self.Musics()

        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Animation Menu
        self.ui.btn_menu.clicked.connect(self.Animation)
        self.window().setWindowFlags(Qt.FramelessWindowHint)

        # Top Bar
        self.ui.btn_max_min.clicked.connect(self.Maxmize)
        self.ui.btn_exit.clicked.connect(lambda: self.window().close())
        self.ui.btn_min.clicked.connect(lambda: self.window().showMinimized())

        # Home
        if len(musics) == 0:
            self.ui.btn_home.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
            self.ui.stackedWidget.setCurrentIndex(0)
        else:
            self.ui.btn_home.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
            self.ui.stackedWidget.setCurrentIndex(2)

        # Download Screen
        self.ui.btn_screen_download.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))

        # Add Songs
        self.ui.btn_add_songs.clicked.connect(self.Add_Songs)

    def mousePressEvent(self, event):
        self.oldPosition = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPosition)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPosition = event.globalPos()

    def Animation(self):
        global newWidth
        width = self.ui.slide_menu.width()

        print(width)
        if width == 0:
            newWidth = 273
        else:
            newWidth = 0

        self.animation = QPropertyAnimation(self.ui.slide_menu, b"minimumWidth")
        self.animation.setDuration(400)
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

    def Musics(self):
        global musics
        cursor.execute('SELECT * FROM music')
        musics = cursor.fetchall()

    def Add_Songs(self):

        root = Tk()
        root.withdraw()
        root.iconbitmap('View/QRC/Logo.ico')

        files = askopenfilenames()

        for music in files:
            if music[-4:] == '.mp3':
                cursor.execute(f'SELECT nome FROM music WHERE nome = "{music}"')
                songs = cursor.fetchall()

                if len(songs) == 0:
                    cursor.execute('SELECT MAX(id) FROM music')
                    last_id = cursor.fetchone()

                    for id_bank in last_id:
                        if id_bank == None:
                            id = 1
                        else:
                            id = int(id_bank) + 1

                    cursor.execute(f'INSERT INTO music VALUES({id}, "{music}")')
                    bank.commit()

                    self.ui.stackedWidget.setCurrentIndex(2)
                else:
                    self.PopUps('Error - Add Songs', f"Music {music} is already added to the bank!")

    def PopUps(self, title, msg):

        message = QMessageBox()
        message.setWindowTitle(str(title))
        message.setText(str(msg))

        icon = QIcon()
        icon.addPixmap(QPixmap('View/QRC/Logo.ico'), QIcon.Normal, QIcon.Off)
        message.setWindowIcon(icon)
        x = message.exec_()

#    def Table(self):



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ListenNow()
    window.show()
    sys.exit(app.exec_())
