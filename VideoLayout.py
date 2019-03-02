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
from GlobalConstant import TIMER_VIDEO
# from XmlHandler import HandlerXml
from SubtitleJson import DataFrame


PATH_VIDEO = "/home/hirvin/Documentos/Hirvin/Proyectos/Ted_Test/NuevoTed/" \
             "video.mp4"
SRT_FILE = "test.xml"

# TIMER_VIDEO = 500

PLAYER_STOP = 0
PLAYER_RUN = 1


class VideoPlayer(QVBoxLayout):
    """ layout con toda la estructura para video player """
    def __init__(self, parent=None):
        # estructura del widget de subtitulos
        super(VideoPlayer, self).__init__(parent)
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        # label que indica el tiempo
        self.l_time = QLabel("Hola mundo")
        self.addWidget(self.l_time)
        self.addWidget(self.video_widget)
        self.player_status = PLAYER_STOP
        self.init_time = None
        self.end_time = None
        self.offset = 0
        self.frame_buffer = None
        self.timer = None
        # hirvin poner video error handler

    def set_video_path(self, video_path):
        """ estable el video que se va a reproducir """
        media_content = QMediaContent(QUrl.fromLocalFile(video_path))
        self.media_player.setMedia(media_content)

    def get_position(self):
        """ retorna la posicion actual del frame """
        return self.end_time

    def print_position(self):
        """ imprime la posicion de init y end """
        if self.init_time is None:
            init_time = 0
        else:
            init_time = self.init_time

        if self.end_time is None:
            end_time = 0
        else:
            end_time = self.end_time

        print "init: %d end: %d" % (init_time, end_time)

    def play(self, init_time=None, end_time=None):
        """ play video """
        if(self.media_player.state() == QMediaPlayer.StoppedState) or \
                (self.media_player.state() == QMediaPlayer.PausedState):
            if init_time is not None:
                if init_time >= 0 and init_time < end_time:
                    self.init_time = init_time + self.offset
                    self.media_player.setPosition(self.init_time)
                else:
                    print "invalid init_time"
                    return False
            if end_time is not None:
                if init_time is None:
                    self.init_time = self.end_time
                self.end_time = end_time + self.offset
                self.player_status = PLAYER_RUN
                # ejecuta el timer en un derterminado intervalo
                self.timer.start(TIMER_VIDEO)
                self.media_player.play()
                return True
            else:
                print "End time no valido"
                return False

    def stop(self):
        """ stop video """
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.stop()

    def pause(self):
        """ pause video """
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()

    def init_configuration(self, video_path=None, frame=None, offset=0):
        """ init configuration of video """
        self.offset = offset
        self.set_video_path(video_path)
        self.media_player.positionChanged.connect(self.duration_scheduler)
        # timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)  # timeout signal
        if frame is not None:
            # end_time = int(self.frame_buffer.get_end_time())
            # init_time = int(self.frame_buffer.get_init_time())
            init_time = frame["start_time"]
            end_time = frame["end_time"]
            self.play(init_time=init_time, end_time=end_time)

    def timeout(self):
        """ timeout """
        if self.media_player.state() == QMediaPlayer.PlayingState:
            if self.player_status == PLAYER_STOP:
                self.media_player.pause()
                self.timer.stop()

    def init_box_layout(self, parent):
        """ inicializa el layout para video player """
        parent.addLayout(self)

    def duration_scheduler(self, position):
        """ se llama cada vez que el video cambia de position """
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.l_time.setText(str(position))
            if position >= self.end_time:
                self.player_status = PLAYER_STOP

    def next_clicked(self, frame=None):
        """ next clicked action """
        # init_time = int(self.frame_buffer.get_init_time())
        if frame is None:
            return False
        # end_time = int(self.frame_buffer.get_end_time())
        end_time = frame["end_time"]
        self.play(init_time=None, end_time=end_time)
        return True
        # self.print_position()

    def prev_clicked(self, frame=None):
        """ prev clicked action """
        # init_time = int(self.frame_buffer.get_init_time())
        # end_time = int(self.frame_buffer.get_end_time())
        if frame is None:
            return False
        init_time = frame["start_time"]
        end_time = frame["end_time"]
        self.play(init_time=init_time, end_time=end_time)
        return True
        # self.print_position()

    def repeat(self, frame=None):
        """ repeat frame """
        self.init_time = frame["start_time"] + self.offset
        self.end_time = frame["end_time"] + self.offset
        if(self.media_player.state() == QMediaPlayer.StoppedState) or \
                (self.media_player.state() == QMediaPlayer.PausedState):
            self.media_player.setPosition(self.init_time)
            self.player_status = PLAYER_RUN
            self.timer.start(TIMER_VIDEO)
            self.media_player.play()


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
        self.video_player = VideoPlayer()
        self.video_player.init_box_layout(layout)

        # adicional elements
        # self.frame_buffer = HandlerXml(SRT_FILE)
        self.data_frame = DataFrame("test_json.txt")


        # este es solo contenido de pruebas no copiar
        self.pause_button = QPushButton("Prev")
        self.play_button = QPushButton("Next")
        self.play_button.clicked.connect(self.next_clicked)
        self.pause_button.clicked.connect(self.prev_clicked)
        layout.addWidget(self.play_button)
        layout.addWidget(self.pause_button)

        # Set widget to contain window contents
        wid.setLayout(layout)

        # inicializacion
        self.init_configuration()

    def next_clicked(self):
        """ reprodce video y ande 10 segundos al frame """
        # self.frame_buffer.next_frame()
        self.video_player.next_clicked(frame=self.data_frame.get_next())

    def prev_clicked(self):
        """ reproduce el video y atrasa 20 segundos """
        # self.frame_buffer.prev_frame()
        self.video_player.prev_clicked(frame=self.data_frame.get_prev())

    def init_configuration(self):
        """ inicializa todas las configuraciones iniciales """
        # inicializacion de subtitle layout
        # inicializacion de video latoyut
        frame = self.data_frame.get_init()
        # 11600
        header = self.data_frame.get_header()
        offset = header["offset"]
        self.video_player.init_configuration(video_path=PATH_VIDEO, frame=frame, offset=offset)

    def exitCall(self):
        """ cierra la apliccaion """
        sys.exit(app.exec_())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())