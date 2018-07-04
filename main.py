# este contiene la unio de todas las retructuras

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
        init_time, end_time = self.sub_lay.get_init_time()
        self.video_player.init_configuration(PATH_VIDEO, end_time, offset=11500)

    def next_clicked(self):
        """ reproduce el siguiente frame """
        init_time, end_time = self.sub_lay.get_next_frame_time()
        self.video_player.play(init_time=None, end_time=end_time)

    def prev_clicked(self):
        """ reproduce el frame anterior """
        init_time, end_time = self.sub_lay.get_prev_frame_time()
        self.video_player.play(init_time=init_time, end_time=end_time)

    def exitCall(self):
        """ cierra la apliccaion """
        sys.exit(app.exec_())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MainWindow()
    player.resize(980, 480)
    player.show()
    sys.exit(app.exec_())
