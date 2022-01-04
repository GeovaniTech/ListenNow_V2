import os.path
import sys
import sqlite3
import eyed3.utils

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from View.PY.ui_Interface import Ui_MainWindow
from tkinter.filedialog import askdirectory, askopenfilenames
from tkinter import Tk

newWidth = 0
musics = None

bank = sqlite3.connect('bank_music')

cursor = bank.cursor()
cursor.execute('DELETE FROM music')
bank.commit()

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

        # Loading Table
        self.Table()

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
        if self.window().isMaximized() == True:
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def Musics(self):
        global musics
        cursor.execute('SELECT * FROM music ORDER BY Id ASC')
        musics = cursor.fetchall()

    def Add_Songs(self):

        root = Tk()
        root.withdraw()
        root.iconbitmap('View/QRC/Logo.ico')

        files = askopenfilenames()

        for music in files:
            if music[-4:] == '.mp3':
                cursor.execute(f'SELECT nome FROM music WHERE nome = "{music}"')
                songs = cursor.fetchone()

                if songs == None:
                    cursor.execute('SELECT MAX(id) FROM music')
                    last_id = cursor.fetchone()

                    for id_bank in last_id:
                        if id_bank == None:
                            id = 1
                        else:
                            id = int(id_bank) + 1

                    print(music)
                    cursor.execute(f'INSERT INTO music VALUES({id}, "{str(music)}")')
                    bank.commit()

                    self.Musics()
                    self.UpdateTable()
                    self.ui.stackedWidget.setCurrentIndex(2)

                else:
                    self.PopUps('Error - Add Songs', f"Music {os.path.basename(music[:-4])} is already added to the bank!")

    def PopUps(self, title, msg):

        message = QMessageBox()
        message.setWindowTitle(str(title))
        message.setText(str(msg))

        icon = QIcon()
        icon.addPixmap(QPixmap('View/QRC/Logo.ico'), QIcon.Normal, QIcon.Off)
        message.setWindowIcon(icon)
        x = message.exec_()

    def Table(self):
        global musics

        # Inserindo as Colunas na tabela
        self.ui.tableWidget.insertColumn(0)
        self.ui.tableWidget.insertColumn(0)

        columns = ['ID', 'Name']
        self.ui.tableWidget.setHorizontalHeaderLabels(columns)
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidget.verticalHeader().setVisible(False)

        self.UpdateTable()

    def UpdateTable(self):
        global musics

        self.ui.tableWidget.setRowCount(len(musics))

        row = 0

        for music in musics:
            # Tratando erro dos metadados
            eyed3.log.setLevel("ERROR")

            try:
                audiofile = eyed3.load(music[1])

                if audiofile != None:
                    self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(str(music[0])))
                    self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(os.path.basename(music[1])))
                    row += 1

                else:
                    self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(str(music[0])))
                    self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(str(audiofile.tag.title)))
                    row += 1

            except IOError:
                ...


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ListenNow()
    window.show()
    sys.exit(app.exec_())
