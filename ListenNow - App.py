import os
import sys
import sqlite3
import eyed3.utils
import pytube as pt
import shutil
import pygame

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from View.PY.ui_Interface import Ui_MainWindow
from tkinter.filedialog import askdirectory, askopenfilenames
from tkinter import Tk
from moviepy.editor import *

bank = sqlite3.connect('bank_music')
cursor = bank.cursor()

musics = None
link = ''
directory = ''


class ListenNow(QMainWindow):

    def __init__(self):
        global musics

        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Init Pygame
        pygame.init()
        pygame.mixer.init()

        # Loading Songs
        self.Musics()

        # Loading Table
        self.Table()
        self.UpdateTable()

        # Som Slider
        sld = self.ui.som_slider
        sld.setRange(0, 9)
        sld.setValue(1)
        sld.valueChanged.connect(self.Som)
        pygame.mixer.music.set_volume(float(0.1))

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

        # Add Songs
        self.ui.btn_add_songs.clicked.connect(self.Add_Songs)

        # Directory
        self.ui.btn_select.clicked.connect(self.Directory)

        # Search Bar
        self.ui.search_music_home.returnPressed.connect(self.Search)
        self.ui.btn_search_home.clicked.connect(self.Search)

        # Play Songs
        self.ui.tableWidget.doubleClicked.connect(self.PlayTable)

        # Button Play/Pause
        self.count_play = 0
        self.ui.btn_play.clicked.connect(self.Play_Pause)

        # Button Next Music
        self.ui.btn_next.clicked.connect(self.Next_Music)

        # Button Return Music
        self.ui.btn_return.clicked.connect(self.Return_Music)

        # Styles Button Play
        self.stylePlay = 'QPushButton {border: 0px;background-image: url(:/icons/imagens/toque.png);}' \
                         'QPushButton:hover {border: 0px;background-image: url(:/icons/imagens/toque_hover.png);}'

        self.stylePause = 'QPushButton {border: 0px;background-image: url(:/icons/imagens/pausa.png);}' \
                          'QPushButton:hover {border: 0px;background-image: url(:/icons/imagens/pausa_hover.png);}'

        # Button Sound
        self.ui.btn_sound.clicked.connect(self.Sound_Max_Min)

        # Download Screen and Button
        self.ui.btn_screen_download.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.btn_download.clicked.connect(self.Donwload_Songs)

    def mousePressEvent(self, event):
        self.oldPosition = event.globalPos()

    def mouseMoveEvent(self, event):
        try:
            delta = QPoint(event.globalPos() - self.oldPosition)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPosition = event.globalPos()
        except:
            window.showMaximized()

    def Animation(self):
        width = self.ui.slide_menu.width()

        if width == 0:
            newWidth = 273
        else:
            newWidth = 0

        self.animation = QPropertyAnimation(self.ui.slide_menu, b"minimumWidth")
        self.animation.setDuration(600)
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
        ...

    def Home(self):
        if len(musics) > 0:
            self.ui.stackedWidget.setCurrentIndex(2)
        else:
            self.ui.stackedWidget.setCurrentIndex(0)

    def Delete_Music(self, id):
        id_deleted = id

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
        global directory
        root = Tk()
        root.withdraw()
        root.iconbitmap('View/QRC/Logo.ico')

        directory = askdirectory()

    def Donwload_Songs(self):
        global link
        link = self.ui.link_youtube.text()

        # Configuring Thread
        self.thread = QThread()
        self.worker = Threads()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.Download)

        # PopUps Started Download
        self.worker.started_download.connect(lambda: self.PopUps('Download started', 'We will notify you when it is ready.'))

        # PopUps and finishing threading
        self.worker.finished.connect(lambda: self.PopUps('Successful Download', f'Your download was completed successfully! Your file is located at {directory}.'))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # PopUps and finishing threading
        self.worker.error_link.connect(lambda: self.PopUps('Error - download launch', 'Link not entered or directory not selected.'))
        self.worker.error_link.connect(self.thread.quit)
        self.worker.error_link.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # PopUps and finishing threading
        self.worker.error_download.connect(lambda: self.PopUps('Error - Download Song', 'Unfortunately we were unable to complete your download, please check your link or enter another one.'))
        self.worker.error_download.connect(self.thread.quit)
        self.worker.error_download.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # PopUps and finishing threading
        self.worker.error_save.connect(lambda: self.PopUps('Error - Move Song', 'There is already a song with the same name existing at your destination.'))
        self.worker.error_save.connect(self.thread.quit)
        self.worker.error_save.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Starting Thread
        self.thread.start()

        # Enabling and disabling button download
        self.ui.btn_download.setEnabled(False)
        self.thread.finished.connect(lambda: self.ui.btn_download.setEnabled(True))

    def Search(self):
        items = self.ui.tableWidget.findItems(self.ui.search_music_home.text(), Qt.MatchContains)

        if items:
            item = items[0]
            self.ui.tableWidget.setCurrentItem(item)

    def Som(self, value):
        self.value = value
        volume = f"{0}.{value}"
        pygame.mixer.music.set_volume(float(volume))

    def PlaySongs(self, id):
        try:
            self.id_music = id
            self.Artist_Music()
            self.pygame_controller = pygame.mixer.music

            self.pygame_controller.unload()
            self.pygame_controller.load(musics[id][1])
            self.pygame_controller.play()
        except:
            self.PopUps('Error Play Song', f'Unfortunately we were unable to play this song, it may be corrupted or deleted from the location.')
            self.Delete_Music(id + 1)
            self.Musics()
            self.UpdateTable()
            if len(musics) > 0:
                self.pygame_controller.load(musics[id - 1][1])
                self.pygame_controller.play()
                self.Artist_Music()

    def PlayTable(self):
        id = self.ui.tableWidget.currentIndex().row()
        self.PlaySongs(int(id))

        self.count_play = 1
        self.Play()

        if self.count_play == 0:
            self.Automatic_Musics()

    def Pause(self):
        self.ui.btn_play.setStyleSheet(self.stylePlay)
        self.pygame_controller.pause()

    def Play(self):
        self.ui.btn_play.setStyleSheet(self.stylePause)
        self.pygame_controller.unpause()

    def Play_Pause(self):
        if self.count_play == 0:
            self.PlaySongs(0)
            self.count_play = 1
            self.Play()
        else:
            if self.count_play % 2 == 1:
                self.Pause()
                self.count_play = 2
            else:
                self.Play()
                self.count_play = 1

        self.Automatic_Musics()

    def Artist_Music(self):
        try:
            audiofile = eyed3.load(musics[self.id_music][1])
            titile = audiofile.tag.title
            artist = audiofile.tag.artist

            music = musics[self.id_music][1]

            if str(titile) != 'None':
                self.ui.lbl_name_Music.setText(titile)
            else:
                self.ui.lbl_name_Music.setText(os.path.basename(music[:-4]))

            if str(artist) != 'None':
                self.ui.lbl_name_Artist.setText(artist)
            else:
                self.ui.lbl_name_Artist.setText('Artist not Found')
        except AttributeError:
            self.ui.lbl_name_Music.setText(os.path.basename(music[:-4]))
            self.ui.lbl_name_Artist.setText('Artist not Found')

    def Next_Music(self):
        if len(musics) > 0:
            self.id_music += 1
            if self.id_music == len(musics):
                self.id_music = 0

            self.PlaySongs(self.id_music)
            self.count_play = 1
            self.Play()

    def Return_Music(self):
        if len(musics) > 0:
            self.id_music -= 1
            if self.id_music < 0:
                self.id_music = int(len(musics)) - 1

            self.PlaySongs(self.id_music)
            self.count_play = 1
            self.Play()

    def Automatic_Musics(self):
        END_EVENT = pygame.USEREVENT +1
        self.pygame_controller.set_endevent(END_EVENT)

        while True:
            for event in pygame.event.get():
                if event.type == END_EVENT:
                    if len(musics) > 0:
                        self.Next_Music()

    def Sound_Max_Min(self):

        if pygame.mixer.music.get_volume() > 0:
            self.Som(0)
            self.ui.som_slider.setValue(0)
        else:
            self.Som(9)
            self.ui.som_slider.setValue(9)


class Threads(QObject):
    finished = pyqtSignal()
    error_download = pyqtSignal()
    error_link = pyqtSignal()
    error_save = pyqtSignal()
    started_download = pyqtSignal()

    def PopUps(self, title, msg):
        message = QMessageBox()
        message.setWindowTitle(str(title))
        message.setText(str(msg))

        icon = QIcon()
        icon.addPixmap(QPixmap('View/QRC/Logo.ico'), QIcon.Normal, QIcon.Off)
        message.setWindowIcon(icon)
        x = message.exec_()

    def Download(self):
        global link, directory

        if link != '' and directory != '':
            try:
                self.started_download.emit()
                stream = pt.YouTube(url=link).streams.get_audio_only()
                stream.download('mp4')
                title = str(stream.title)
            except:
                self.error_download.emit()

            files = list()
            files.clear()

            for (dirpath, dirnames, filenames) in os.walk('mp4'):
                files.extend(filenames)
                break

            for file in files:
                music = f'mp4\{file}'
                self.mp4_to_mp3(music, f'{title}.mp3')
                os.remove(music)

            file = f'{title}.mp3'

            try:
                shutil.move(file, directory)
            except:
                self.error_save.emit()
            else:
                self.finished.emit()
        else:
            self.error_link.emit()

    def mp4_to_mp3(self, mp4, mp3):
        mp4_without_frames = AudioFileClip(mp4)
        mp4_without_frames.write_audiofile(mp3)
        mp4_without_frames.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ListenNow()
    window.showMaximized()
    sys.exit(app.exec_())