# contiene todo el layout de subtitulos

import sys
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from Subtitle import Subtitle

# definicion de constantes
[MAX_BUTTON_WIDTH, MAX_BUTTON_HIGH] = [80, 80]
NUM_WORD_BY_SUB = 15

# constantes del programa
SRT_FILE = "sub.srt"

class PrevButton(QPushButton):
    """ estructura del Prev Button """
    def __init__(self, parent=None):
        super(PrevButton, self).__init__("Prev", parent)
        self.setMaximumSize(MAX_BUTTON_WIDTH, MAX_BUTTON_HIGH)

class NextButton(QPushButton):
    """ estructura del Next Button """
    def __init__(self, parent=None):
        super(NextButton, self).__init__("Next", parent)
        self.setMaximumSize(MAX_BUTTON_WIDTH, MAX_BUTTON_HIGH)

class LbWord(QLabel):
    """ estructura de una palabra """
    def __init__(self, parent=None):
        super(LbWord, self).__init__(parent)
        self.setText("")


class SubLine(QHBoxLayout):
    """ Contiene una linea de palbras de subtitulo """
    def __init__(self, parent=None):
        super(SubLine, self).__init__(parent)
        self.words = []
        self.create_words()
        self.set_layout()
        # self.clean()

    def create_words(self):
        """ crea las palabras de una linea """
        for i_word in range(NUM_WORD_BY_SUB):
            self.words.append(LbWord())

    def set_layout(self):
        """ setea todas las palabras en el layout """
        self.addStretch()
        for i_word in range(NUM_WORD_BY_SUB):
            self.addWidget(self.words[i_word])
        self.addStretch()

    def set_words(self, words):
        """ actualiza el subtitulo con el valor de words """
        index = 0
        self.clean()

        if len(words) > NUM_WORD_BY_SUB:
            print "Numero de palabras excede el limite"
            return False

        for i_word in words:
            self.words[index].setText(i_word)
            index += 1
        return True

    def clean(self):
        """ limpia todas las palabras """
        for i_word in self.words:
            i_word.setText("")


class SubVBox(QVBoxLayout):
    """ box que contienen todos los labels para los subtitles """
    def __init__(self, parent=None):
        super(SubVBox, self).__init__(parent)
        self.sub_line1 = SubLine()
        self.sub_line2 = SubLine()

        self.addLayout(self.sub_line1)
        self.addLayout(self.sub_line2)

        # self.sub_line1.set_words(["hola", "como", "estas", "mala"])

    def set_sub_line1(self, words):
        """ setea las palabras en la linea 1 """
        self.sub_line1.set_words(words)

    def set_sub_line2(self, words):
        """ setea las palabras en la linea 2 """
        self.sub_line2.set_words(words)


class SubtitleLayout(QHBoxLayout):
    """ layout con toda la estructura para subtitulos """
    def __init__(self, parent=None):
        # estructura del widget de subtitulos
        super(SubtitleLayout, self).__init__(parent)
        self.sub_buffer = Subtitle()
        self.prev_button = PrevButton()
        self.next_button = NextButton()
        self.v_sub_layout = SubVBox()

        self.addWidget(self.prev_button)
        self.addLayout(self.v_sub_layout)
        self.addWidget(self.next_button)

    def open_srt(self, srt_text):
        """ carga los subtitulos """
        # hirvin por Trues
        self.sub_buffer.open_srt(srt_text)
        self.sub_buffer.get_frames()

    def init_sub_layout(self):
        """ carga las configuraciones iniciales del sub layout """
        # hirvin poner si esta readi : is_ready()
        self.v_sub_layout.set_sub_line1(self.sub_buffer.buffer_frames[0].words)
        self.v_sub_layout.set_sub_line2(self.sub_buffer.buffer_frames[1].words)


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

        # anadiendo estrutura
        self.sub_lay = SubtitleLayout()
        layout.addLayout(self.sub_lay)

        # Set widget to contain window contents
        wid.setLayout(layout)

        # inicializacion
        self.init_configuration()

    def init_configuration(self):
        """ inicializa todas las configuraciones iniciales """
        self.sub_lay.open_srt(SRT_FILE)
        self.sub_lay.init_sub_layout()

    def exitCall(self):
        """ cierra la apliccaion """
        sys.exit(app.exec_())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())