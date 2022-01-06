import os
import sys
import sqlite3
import eyed3.utils
import youtube_dl

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from View.PY.ui_Interface import Ui_MainWindow
from tkinter.filedialog import askdirectory, askopenfilenames
from tkinter import Tk

musics = None

bank = sqlite3.connect('bank_music')
cursor = bank.cursor()


class ListenNow(QMainWindow):

    def __init__(self):
        global musics

        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Loading Songs
        self.Musics()

        # Loading Table
        self.Table()
        self.UpdateTable()

        # Animation Menu
        self.ui.btn_menu.clicked.connect(self.Animation)
        self.window().setWindowFlags(Qt.FramelessWindowHint)

        # Top Bar
        self.ui.btn_max_min.clicked.connect(self.Maxmize)
        self.ui.btn_exit.clicked.connect(lambda: self.window().close())
        self.ui.btn_min.clicked.connect(lambda: self.window().showMinimized())

        # Home Screen
        self.Home()
        self.ui.btn_home.clicked.connect(self.Home)

        # Download Screen and Button
        self.ui.btn_screen_download.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.btn_download.clicked.connect(self.Donwload_Songs)

        # Add Songs
        self.ui.btn_add_songs.clicked.connect(self.Add_Songs)

        # Directory
        self.ui.btn_select.clicked.connect(self.Directory)

        # Search Bar
        self.ui.search_music_home.returnPressed.connect(self.Search)
        self.ui.btn_search_home.clicked.connect(self.Search)

    def mousePressEvent(self, event):
        self.oldPosition = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPosition)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPosition = event.globalPos()

    def Animation(self):
        width = self.ui.slide_menu.width()

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

        self.ui.tableWidget.insertColumn(0)
        self.ui.tableWidget.insertColumn(0)
        self.ui.tableWidget.insertColumn(0)

        header = self.ui.tableWidget.horizontalHeader()

        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        columns = ['ID','Name', 'Delete']
        self.ui.tableWidget.setHorizontalHeaderLabels(columns)
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidget.verticalHeader().setVisible(False)
        self.ui.tableWidget.verticalScrollBar().setVisible(False)
        self.ui.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.tableWidget.setFocusPolicy(Qt.NoFocus)

        self.ui.tableWidget.setStyleSheet('QTableWidget {color: white;font: 11pt "Century Gothic";}'
                                          'QTableWidget::item:selected{background-color:rgb(87, 87, 87);; outline:0px; color: white;}'
                                          'QHeaderView::section:horizontal{background-color: rgb(87, 87, 87); color: white; border: 1px solid #4A4A4A; font: 10pt "Century Gothic";}')

        self.UpdateTable()

    def UpdateTable(self):
        global musics

        self.ui.tableWidget.setRowCount(len(musics))

        # Completer Search
        self.completer = list()
        self.completer.clear()


        row = 0

        for music in musics:
            # Tratando erro dos metadados
            eyed3.log.setLevel("ERROR")


            # Creating a button delete
            self.button_delete = QPushButton()
            self.button_delete.setFixedWidth(60)
            self.button_delete.setStyleSheet('QPushButton {border: 0px;}'
                                             'QPushButton:hover {background-color: rgb(87, 87, 87);}')

            icon = QIcon()
            icon.addPixmap(QPixmap('View/QRC/lixo_br.png'), QIcon.Normal, QIcon.Off)
            self.button_delete.setIcon(icon)
            self.button_delete.clicked.connect(self.Delete_Table)

            try:
                audiofile = eyed3.load(music[1])
                title = audiofile.tag.title
                if str(title) == 'None':
                    try:
                        self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(str(music[0])))
                        self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(os.path.basename(music[1])))
                        self.ui.tableWidget.setCellWidget(row, 2, self.button_delete)
                        self.completer.append(os.path.basename(music[1]))
                        row += 1
                    except:
                        self.PopUps('Error - Add to Song',
                                    f'Music {os.path.basename(music[1])} not found or is corrupted. Music will be deleted!')
                        self.Delete_Music(music[1])
                else:
                    try:
                        self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(str(music[0])))
                        self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(str(title)))
                        self.ui.tableWidget.setCellWidget(row, 2, self.button_delete)
                        self.completer.append(title)
                        row += 1
                    except:
                        self.PopUps('Error - Add to Song',
                                    f'Music {os.path.basename(music[1])} not found or is corrupted. Music will be deleted!')
                        self.Delete_Music(music[1])
            except AttributeError:
                if str(title) == 'None':
                    try:
                        self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(str(music[0])))
                        self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(os.path.basename(music[1])))
                        self.ui.tableWidget.setCellWidget(row, 2, self.button_delete)
                        self.completer.append(os.path.basename(music[1]))
                        row += 1
                    except:
                        self.PopUps('Error - Add to Song',
                                    f'Music {os.path.basename(music[1])} not found or is corrupted. Music will be deleted!')
                        self.Delete_Music(music[0])
                else:
                    try:
                        self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(str(music[0])))
                        self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(str(title)))
                        self.ui.tableWidget.setCellWidget(row, 2, self.button_delete)
                        self.completer.append(title)
                        row += 1
                    except:
                        self.PopUps('Error - Add to Song',
                                    f'Music {os.path.basename(music[1])} not found or is corrupted. Music will be deleted!')
                        self.Delete_Music(music[0])
            except OSError:
                self.PopUps('Error - Add to Song',
                            f'Music {os.path.basename(music[1])} not found or is corrupted. Music will be deleted!')
                self.Delete_Music(music[0])

            self.completer_songs = QCompleter(self.completer)
            self.completer_songs.popup().setStyleSheet('background-color: rgb(87, 87, 87); color: white; border: 1px solid #4A4A4A; font: 11pt "Century Gothic";')
            self.completer_songs.popup().setFocusPolicy(Qt.NoFocus)
            self.completer_songs.setCaseSensitivity(Qt.CaseInsensitive)
            self.ui.search_music_home.setCompleter(self.completer_songs)

    def Home(self):
        if len(musics) > 0:
            self.ui.stackedWidget.setCurrentIndex(2)
        else:
            self.ui.stackedWidget.setCurrentIndex(0)

    def Delete_Music(self, delete_music):
        id_deleted = delete_music

        cursor.execute(f'DELETE FROM music WHERE id = {id_deleted}')
        bank.commit()

        for music in musics:
            if int(music[0]) > id_deleted:
                cursor.execute(f'UPDATE music set id = {music[0] - 1} WHERE nome = "{music[1]}"')
                bank.commit()

        self.Musics()
        self.UpdateTable()

    def Delete_Table(self):
        id = self.ui.tableWidget.currentIndex().row() + 1
        self.Delete_Music(int(id))
        self.Home()

    def Directory(self):
        root = Tk()
        root.withdraw()
        root.iconbitmap('View/QRC/Logo.ico')

        self.directory = askdirectory()

    def Donwload_Songs(self):
        if self.directory != '' and self.ui.link_youtube.text() != '':

            link = self.ui.link_youtube.text()

            try:
                self.PopUps('Download Started', "Your download has started, we'll notify you when it's ready.")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([f'{link}'])
            except:
                self.PopUps("Error - Download", 'Sorry, but your download was not successful, please check the link and try again.')

    def Search(self):
        items = self.ui.tableWidget.findItems(self.ui.search_music_home.text(), Qt.MatchContains)

        if items:
            item = items[0]
            self.ui.tableWidget.setCurrentItem(item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ListenNow()
    window.show()
    sys.exit(app.exec_())