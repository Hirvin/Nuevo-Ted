# video library,  engargada de la reproducion del video
from PyQt5.QtCore import QDir, Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
import sys
import time

PATH_VIDEO = "/home/hirvin/Documentos/Hirvin/Proyectos/Ted_Test/NuevoTed/" \
"video.mp4"



class VideoPlayer(QVBoxLayout):
    """ layout con toda la estructura para video player """
    def __init__(self, parent=None):
        # estructura del widget de subtitulos
        super(VideoPlayer, self).__init__(parent)
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.addWidget(self.video_widget)
        # hirvin poner video error handler

    def set_video_path(self, video_path):
        """ estable el video que se va a reproducir """
        media_content = QMediaContent(QUrl.fromLocalFile(video_path))
        self.media_player.setMedia(media_content)

    def play(self):
        """ play video """
        if(self.media_player.state() == QMediaPlayer.StoppedState) or \
                (self.media_player.state() == QMediaPlayer.PausedState):
            self.media_player.play()

    def stop(self):
        """ stop video """
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.stop()

    def pause(self):
        """ pause video """
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()

    def init_configuration(self, video_path):
        """ init configuration of video """
        self.set_video_path(video_path)
        # self.media_player.positionChanged.connect(self.duration_scheduler)
        # timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)  # timeout signal
        self.timer.start(5000)  # updates every second
        self.play()

    def timeout(self):
        print "hola timer "
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()


    def init_box_layout(self, parent):
        """ inicializa el layout para video player """
        parent.addLayout(self)

    def duration_scheduler(self, position):
        """ se llama cada vez que el video cambia de posicion """
        if self.media_player.state() == QMediaPlayer.PlayingState:
            if position > 5000:
                print position
                # chage this for pause()
                # hirvin
                self.media_player.stop()
                # self.media_player.pause()
                # self.video_control.prev_button.enable()
                # self.video_control.next_button.enable_first_frame()


class VideoWindow(QMainWindow):
    """Ventana Principal del Programa"""
    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("PyTedict")

        self.info_label = QLabel()
        self.info_label.setText("Este layout es solo de uso exclusivo"
                                " para pruebas")
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        layout = QVBoxLayout()
        layout.addWidget(self.info_label)

        # anadir subtitle layout
        # anadir video layout
        self.video_player = VideoPlayer()
        self.video_player.init_box_layout(layout)

        # este es solo contenido de pruebas no copiar
        self.pause_button = QPushButton("pause")
        self.play_button = QPushButton("play")
        self.play_button.clicked.connect(self.video_player.play)
        self.pause_button.clicked.connect(self.video_player.pause)
        layout.addWidget(self.play_button)
        layout.addWidget(self.pause_button)

        # Set widget to contain window contents
        wid.setLayout(layout)

        # inicializacion
        self.init_configuration()

    def init_configuration(self):
        """ inicializa todas las configuraciones iniciales """
        # inicializacion de subtitle layout
        # inicializacion de video latoyut
        self.video_player.init_configuration(PATH_VIDEO)

    def exitCall(self):
        """ cierra la apliccaion """
        sys.exit(app.exec_())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())