# este contiene la unio de todas las retructuras
# git push -u origin master // para subir 


import sys
import PyQt5.QtGui as QtGui
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction, QSlider
from SubtitleLayout import SubtitleLayout
from VideoLayout import VideoPlayer

# constantes del programa
PATH_VIDEO = "/home/hirvin/Documentos/Hirvin/Proyectos/Ted_Test/NuevoTed/" \
    "video.mp4"
SRT_FILE = "sub.srt_ted"

ENABLE_BUTTON = 0
REAPEAT_BUTTON = 2

class MainWindow(QMainWindow):
    """Ventana Principal del Programa"""
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("PyTedict")

        self.info_label = QLabel()
        self.info_label.setText("Este layout es solo de uso exclusivo"
                                " para pruebas")
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # variables del sistema
        self.init_time = 0
        self.end_time = 0

        # Create layouts to place inside widget
        layout = QVBoxLayout()
        layout.addWidget(self.info_label)

        # anadir la parte de Video
        self.video_player = VideoPlayer()
        self.video_player.init_box_layout(layout)

        # anadir la parte de subtitulos
        self.sub_lay = SubtitleLayout()
        self.sub_lay.init_box_layout(layout)

        # Set widget to contain window contents
        wid.setLayout(layout)

        # inicializacion
        self.init_configuration()

        # conectando senales
        self.sub_lay.next_button.clicked.connect(self.next_clicked)
        self.sub_lay.prev_button.clicked.connect(self.prev_clicked)

    def init_configuration(self):
        """ inicializa todas las configuraciones iniciales """
        # inicializacion de subtitle layout
        self.sub_lay.init_sub_layout(SRT_FILE)
        # inicializacion de video latoyut
        self.init_time, self.end_time = self.sub_lay.get_init_time()
        self.video_player.init_configuration(PATH_VIDEO, self.end_time,
                                             offset=11500)
        self.sub_lay.repeat_next_button()

    def next_clicked(self):
        """ reproduce el siguiente frame """
        print "es state es:"
        print self.sub_lay.get_state_next_button()
        if self.sub_lay.get_state_next_button() == REAPEAT_BUTTON:
            self.video_player.play(init_time=self.init_time, end_time=self.end_time)
        else:
            self.init_time, self.end_time = self.sub_lay.get_next_frame_time()
            self.video_player.play(init_time=None, end_time=self.end_time)
            self.sub_lay.next_clicked()

    def prev_clicked(self):
        """ reproduce el frame anterior """
        self.init_time, self.end_time = self.sub_lay.get_prev_frame_time()
        self.video_player.play(init_time=self.init_time, end_time=self.end_time)

    def exitCall(self):
        """ cierra la apliccaion """
        sys.exit(app.exec_())

    def keyPressEvent(self, event):
        """ key press event """
        if type(event) == QtGui.QKeyEvent:
            key = event.key()
            if self.sub_lay.is_character(key):
                if self.sub_lay.is_word_complete(key) is True:
                    self.sub_lay.enable_next_button()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MainWindow()
    player.resize(980, 480)
    player.show()
    sys.exit(app.exec_())
