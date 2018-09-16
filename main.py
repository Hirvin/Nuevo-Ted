# este contiene la unio de todas las retructuras
# git push -u origin master // para subir 


import sys
import PyQt5.QtGui as QtGui
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction, QSlider, QDesktopWidget
from SubtitleLayout import SubtitleLayout
from VideoLayout import VideoPlayer
from XmlHandler import HandlerXml
from speech import get_audio, get_differences
import os
from time import sleep



# constantes del programa
PATH_VIDEO = "/home/hirvin/Documentos/Hirvin/Proyectos/Ted_Test/NuevoTed/" \
    "video.mp4"
SRT_FILE = "test.xml"


ENABLE_BUTTON = 0
REAPEAT_BUTTON = 2
SAY_BUTTON = 3
PREV_BUTTON = 4


class SayLayout(QHBoxLayout):
    """ Say Layout """
    def __init__(self, parent=None):
        super(SayLayout, self).__init__(parent)
        self.tag = QLabel(" ")
        self.text = QLabel(" ")
        self.addStretch()
        self.addWidget(self.tag)
        self.addWidget(self.text)
        self.addStretch()

        # set sizes
        self.tag.setMinimumWidth(120)

    def set_tag(self, tag=""):
        """ set tag label """
        self.tag.setText(tag)

    def set_label(self, text=""):
        """ set text label """
        self.text.setText(text)

    def set_you_said(self, text=""):
        """ set you said """
        self.set_tag("  You haev said:")
        self.set_label(text)

    def say_something(self):
        """ say something """
        self.set_tag("Say Something...")
        self.set_label(" ")
        self.tag.repaint()
        self.text.repaint()
        self.update()

    def processing(self):
        """ procesing """
        self.tag.setText("Processing...")
        self.text.setText(" ")
        self.tag.repaint()
        self.text.repaint()
        self.update()

    def clean(self):
        """ clean """
        self.set_tag(" ")
        self.set_label(" ")
        self.tag.repaint()
        self.text.repaint()
        self.update()


class MainWindow(QMainWindow):
    """Ventana Principal del Programa"""
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("PyTedict")

        self.info_label = QLabel()
        self.info_label.setText("Este layout es solo de uso exclusivo"
                                " para pruebas")
        # say layout
        self.you_said_label = QLabel()
        self.mi_label = SayLayout()
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
        # layout.addWidget(self.you_said_label)
        layout.addLayout(self.mi_label)

        # Set widget to contain window contents
        wid.setLayout(layout)

        # inicializacion
        self.frame_buffer = HandlerXml(SRT_FILE)
        self.init_configuration()

        # conectando senales
        self.sub_lay.next_button.clicked.connect(self.next_global_clicked)
        self.sub_lay.prev_button.clicked.connect(self.prev_global_clicked)

    def center(self):
        """ center window """
        # geometry of the main window
        qr_size = self.frameGeometry()

        # center point of screen
        cp_size = QDesktopWidget().availableGeometry().center()

        # move rectangle's center point to screen's center point
        qr_size.moveCenter(cp_size)

        # top left of rectangle becomes top left of window centering it
        self.move(qr_size.topLeft())

    def init_configuration(self):
        """ inicializa todas las configuraciones iniciales """
        if self.frame_buffer.get_is_speech_complete_frame() is True:
            print "necesito bucar"
            for frame in self.frame_buffer.root[1:]:
                print frame.attrib["speech_is_complete"]
                if frame.attrib["speech_is_complete"] == "false":
                    break
                else:
                    print "iterando"
                    self.frame_buffer.next_frame()

        # hirvin modificar init_sub_layout 
        self.sub_lay.init_sub_layout(self.frame_buffer, debug_mode=False)
        self.sub_lay.repeat_next_button()
        self.video_player.init_configuration(video_path=PATH_VIDEO, frame_buffer=self.frame_buffer, offset=11600)
        if self.frame_buffer.get_is_text_complete_frame() is True:
            self.sub_lay.init_say_mode()

    def next_global_clicked(self):
        """ reproduce el siguiente frame """
        if self.sub_lay.get_state_next_button() == REAPEAT_BUTTON:
            self.video_player.repeat()
        else:
            self.frame_buffer.save()
            self.frame_buffer.next_frame()
            self.sub_lay.next_clicked()
            self.sub_lay.repeat_next_button()
            self.video_player.next_clicked()
            self.you_said_label.setText(" ")

    def prev_global_clicked(self):
        """ reproduce el frame anterior """
        if self.sub_lay.get_state_prev_button() == PREV_BUTTON:
            self.frame_buffer.prev_frame()
            self.sub_lay.prev_clicked()
            self.sub_lay.enable_next_button()
            self.video_player.prev_clicked()
        elif self.sub_lay.get_state_prev_button() == SAY_BUTTON:
            self.process_voice()

    def process_voice(self):
        """ procesamiento de la voz """
        self.mi_label.clean()
        os.system("clear")
        text = self.sub_lay.get_words_text()
        self.mi_label.say_something()
        audio = get_audio()
        self.mi_label.processing()
        diff, you_said = get_differences(audio=audio, sub_text=text)

        if self.sub_lay.evaluate_diff(diff) is True:
            self.sub_lay.enable_next_button()
            self.sub_lay.enable_prev_button()
            self.frame_buffer.set_is_speech_complete_frame("true")
        self.mi_label.set_you_said(you_said)

    def exitCall(self):
        """ cierra la apliccaion """
        sys.exit(app.exec_())

    def keyPressEvent(self, event):
        """ key press event """
        if type(event) == QtGui.QKeyEvent:
            key = event.key()
            if self.sub_lay.is_character(key):
                if self.sub_lay.is_word_complete(key) is True:
                    self.frame_buffer.set_is_text_complete_frame("true")
                    self.frame_buffer.save()
                    self.sub_lay.init_say_mode()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MainWindow()
    player.resize(980, 580)
    player.center()
    player.show()
    sys.exit(app.exec_())
