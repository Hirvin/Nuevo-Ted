# contiene todo el layout de subtitulos
# to do : agregar barra de progreso 

import sys
import PyQt5.QtGui as QtGui
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction, QSlider
from Subtitle import Subtitle
from GlobalConstant import NUM_WORD_BY_SUB

# definicion de constantes
[MAX_BUTTON_WIDTH, MAX_BUTTON_HIGH] = [80, 80]
# NUM_WORD_BY_SUB = 15

# constantes del programa
SRT_FILE = "sub.srt"


class SubSlider(QSlider):
    """ slider que muestra el avance de los suntitulos """
    def __init__(self, parent=None):
        super(SubSlider, self).__init__(Qt.Horizontal, parent)

    def set_range(self, min, max):
        """ establece el rango de operacion del slider """
        self.setRange(min, max)

    def set_value(self, value):
        """ establece la posicion actual del slider """
        self.setValue(value)

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

    def mousePressEvent(self, event):
        """ ejecuta accion al presional el label """
        word = self.text()
        if word != "":
            print word


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

        if words is None:
            # print "se ha finalizado el buffer"
            words = []

        if len(words) > NUM_WORD_BY_SUB:
            print "words es mayor que NUM_WORD_BY_SUB : %d" % (len(words))
            print words
            return False

        offset = int((NUM_WORD_BY_SUB - len(words)) / 2)
        index = offset
        # print "el offset es : %d " % (offset)

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

        # subitle slide initialization
        self.sub_slider = SubSlider()

        # inicializacion de los eventos
        self.next_button.clicked.connect(self.next_clicked)
        self.prev_button.clicked.connect(self.prev_clicked)

    def open_srt(self, srt_text):
        """ carga los subtitulos """
        if self.sub_buffer.open_srt(srt_text) is False:
            print "No es posible abrir srt"
            return False
        if self.sub_buffer.get_frames() is False:
            print "No es posible get_frames()"
            return False
        return True

    def init_sub_layout(self):
        """ carga las configuraciones iniciales del sub layout """
        if self.sub_buffer.is_ready() is True:
            self.v_sub_layout.set_sub_line1(self.sub_buffer.get_next_word())
            self.v_sub_layout.set_sub_line2(self.sub_buffer.get_next_word())
            self.sub_slider.set_range(0, self.sub_buffer.num_frames)
            self.sub_slider.set_value(2)
            return True
        return False

    def init_box_layout(self, parent):
        """ se anade asi mismo a la estrutura principal """
        parent.addWidget(self.sub_slider)
        parent.addLayout(self)

    def next_clicked(self):
        """ handler para cuando se presina next button """
        if self.sub_buffer.is_next_ready() is True:
            self.v_sub_layout.set_sub_line1(self.sub_buffer.get_next_word())
            self.v_sub_layout.set_sub_line2(self.sub_buffer.get_next_word())
            self.sub_slider.set_value(self.sub_buffer.index)

    def prev_clicked(self):
        """ handler prev button """
        if self.sub_buffer.is_prev_ready() is True:
            self.v_sub_layout.set_sub_line2(self.sub_buffer.get_prev_word())
            self.v_sub_layout.set_sub_line1(self.sub_buffer.get_prev_word())
            self.sub_slider.set_value(self.sub_buffer.index)


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
        #layout.addLayout(self.sub_lay)
        self.sub_lay.init_box_layout(layout)

        # Set widget to contain window contents
        wid.setLayout(layout)

        # inicializacion
        self.init_configuration()

    def init_configuration(self):
        """ inicializa todas las configuraciones iniciales """
        self.sub_lay.open_srt(SRT_FILE)
        self.sub_lay.init_sub_layout()

    # esta funcion es necesaria incluirla en la ventan principal
    def keyPressEvent(self, event):
        """ key press event """
        if type(event) == QtGui.QKeyEvent:
            key = event.key()
            if key >= ord("A") and key <= ord("Z"):
                print chr(key)

    def exitCall(self):
        """ cierra la apliccaion """
        sys.exit(app.exec_())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())