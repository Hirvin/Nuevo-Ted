# contiene todo el layout de subtitulos
# to do : agregar barra de progreso 

import sys
import PyQt5.QtGui as QtGui
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction, QSlider
from Subtitle import Subtitle2
from GlobalConstant import NUM_WORD_BY_SUB
import re
from PyDictionary import PyDictionary

# see QColor(0, 200, 0)

# definicion de constantes
[MAX_BUTTON_WIDTH, MAX_BUTTON_HIGH] = [80, 80]
# NUM_WORD_BY_SUB = 15

# constantes del programa
# silver para activado
# tan malo intermedio
# steelblue or slateblue correcto
# slategrey or slategray en proceso
# init darkslategray
SRT_FILE = "sub.srt_ted"
REPLACE_WORD_TO_ASTERISC = r"[a-zA-Z0-9]"
REPLACE_WORD_TO_DICTIONARY = r"[/,/./-/_]"

POINTER_WORD = "*"
ERROR_COLOR = "sienna"
INIT_WORD_COLOR = "darkslategrey"
ACTIVE_WORD_COLOR = "slategrey"
CORRECT_WORD_COLOR = "royalblue"
WARNING_COLOR = "tan"


class SubSlider(QSlider):
    """ slider que muestra el avance de los suntitulos """
    def __init__(self, parent=None):
        super(SubSlider, self).__init__(Qt.Horizontal, parent)

    def set_range(self, min_v, max_v):
        """ establece el rango de operacion del slider """
        self.setRange(min_v, max_v)

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
        self.is_complete = True
        self.word = []
        self.index_word = 0
        self.word_point = []
        self.cnt_word = 0
        self.dictionary = PyDictionary()

    def mousePressEvent(self, event):
        """ ejecuta accion al presional el label """
        word = self.lst_to_str(self.word)
        if word != "" and self.is_complete:
            word = re.sub(REPLACE_WORD_TO_DICTIONARY, "", word)
            text = str(self.dictionary.meaning(word))
            print (text)

    def replace_word(self, word):
        """ remplaza las letras y numero por *"""
        return re.sub(REPLACE_WORD_TO_ASTERISC, POINTER_WORD, word)

    def set_color(self, color, txt):
        """ retorna el color planteado """
        return "<font color='%s'>%s</font>" % (color, txt)

    def find_letter(self):
        """ encuentra la primera letra disponible """
        for letter in self.word_point[self.index_word:]:
            if letter == POINTER_WORD:
                return True
            self.index_word += 1
        return False

    def lst_to_str(self, x_list):
        """ convierte una lista a string """
        return ''.join(map(str, x_list))

    def complete_word(self, key):
        """ acompleta las palabras """
        # verifica que no alla mas palabras
        if self.find_letter() is False:
            self.is_complete = True
            word = self.lst_to_str(self.word_point)
            self.setText(self.set_color(CORRECT_WORD_COLOR, word))
            return True

        chr_w = self.word[self.index_word].upper()
        if chr_w == chr(key):
            # print self.word_point
            # print self.word
            self.word_point[self.index_word] = self.word[self.index_word]
            text = self.lst_to_str(self.word_point)
            self.setText(self.set_color(ACTIVE_WORD_COLOR, text))
            self.index_word += 1
        else:
            self.cnt_word += 1

        # evalua los errores de cada palabra
        if self.evaluate_errors() is True:
            return True

        if self.index_word >= len(self.word):
            self.is_complete = True
            word = self.lst_to_str(self.word_point)
            self.setText(self.set_color(CORRECT_WORD_COLOR, word))
            return True

        return False

    def evaluate_errors(self):
        """ evalua lo errore en cada palabra """
        if self.cnt_word < 2:
            word = self.lst_to_str(self.word_point)
            self.setText(self.set_color(ACTIVE_WORD_COLOR, word))
        if self.cnt_word == 2:
            # print "esta palabra tiene errores"
            word = self.lst_to_str(self.word_point)
            self.setText(self.set_color(WARNING_COLOR, word))
        if self.cnt_word == 4:
            # self.setText(self.lst_to_str(self.word))
            word = self.lst_to_str(self.word)
            self.setText(self.set_color(ERROR_COLOR, word))
            self.is_complete = True
        return False

    def init_text(self, word):
        """ inicializa la palabra en el label """
        self.word_point = list(self.replace_word(word))
        text = self.lst_to_str(self.word_point)
        self.setText(self.set_color(INIT_WORD_COLOR, text))
        self.is_complete = False
        self.word = list(word)

    def is_word_complete(self, key):
        """ determina si la palabra es completa """
        if self.is_complete is True:
            return True
        # print chr(key)
        return self.complete_word(key)
        # return False

    def clean(self):
        """ limpia la estrucutra de LbWord """
        self.setText(" ")
        self.update()
        self.is_complete = True
        self.word = []
        self.word_point = []
        self.index_word = 0
        self.cnt_word = 0


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

    def set_words(self, words, debug_mode=False):
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

        if len(words) > NUM_WORD_BY_SUB:
            print "Numero de palabras excede el limite"
            return False

        # imprime las palabras para el debug mode
        if debug_mode is True:
            print words

        for i_word in words:
            self.words[index].init_text(i_word)
            index += 1
        return True

    def clean(self):
        """ limpia todas las palabras """
        for i_word in self.words:
            i_word.clean()

    def is_word_complete(self, key):
        """ is word complete """
        # return self.words[0].is_word_complete(key)
        for word in self.words:
            if word.is_word_complete(key) is False:
                return False
        return True


class SubVBox(QVBoxLayout):
    """ box que contienen todos los labels para los subtitles """
    def __init__(self, parent=None):
        super(SubVBox, self).__init__(parent)
        self.sub_line1 = SubLine()
        self.sub_line2 = SubLine()

        self.addLayout(self.sub_line1)
        self.addLayout(self.sub_line2)

    def set_sub_line1(self, words, debug_mode=False):
        """ setea las palabras en la linea 1 """
        self.sub_line1.set_words(words, debug_mode)

    def set_sub_line2(self, words, debug_mode=False):
        """ setea las palabras en la linea 2 """
        self.sub_line2.set_words(words, debug_mode)

    def is_word_complete(self, key):
        """ is word complete"""
        if self.sub_line1.is_word_complete(key) is True:
            return self.sub_line2.is_word_complete(key)
        return False


class SubtitleLayout(QHBoxLayout):
    """ layout con toda la estructura para subtitulos """
    def __init__(self, parent=None):
        # estructura del widget de subtitulos
        super(SubtitleLayout, self).__init__(parent)
        self.debug_mode = False
        self.sub_buffer = Subtitle2()
        self.prev_button = PrevButton()
        self.next_button = NextButton()
        self.v_sub_layout = SubVBox()
        # verifica si las palabras esta completa
        self.is_complete = True

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

    def init_sub_layout(self, srt_text, debug_mode=False):
        """ carga las configuraciones iniciales del sub layout """
        self.open_srt(srt_text)
        if self.sub_buffer.is_ready() is True:
            self.debug_mode = debug_mode
            l1_word, l2_word = self.sub_buffer.get_next_word()
            self.v_sub_layout.set_sub_line1(l1_word, self.debug_mode)
            self.v_sub_layout.set_sub_line2(l2_word, self.debug_mode)
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
            l1_word, l2_word = self.sub_buffer.get_next_word()
            self.v_sub_layout.set_sub_line1(l1_word, self.debug_mode)
            self.v_sub_layout.set_sub_line2(l2_word, self.debug_mode)
            self.sub_slider.set_value(self.sub_buffer.index_txt)
            self.is_complete = False

    def prev_clicked(self):
        """ handler prev button """
        if self.sub_buffer.is_prev_ready() is True:
            l1_word, l2_word = self.sub_buffer.get_prev_word()
            self.v_sub_layout.set_sub_line2(l2_word, self.debug_mode)
            self.v_sub_layout.set_sub_line1(l1_word, self.debug_mode)
            self.sub_slider.set_value(self.sub_buffer.index_txt)
            self.is_complete = False

    def get_init_time(self):
        """ odteniendo el init time """
        return self.sub_buffer.get_init_time()

    def get_next_frame_time(self):
        """ retorna los valores del tiempo del siguiente frame """
        return self.sub_buffer.next_frame_time()

    def get_prev_frame_time(self):
        """ retorna los valores del tiempo del frame anterior """
        return self.sub_buffer.prev_frame_time()

    def is_letter(self, key):
        """ retorna True si es una letra """
        return key >= ord("A") and key <= ord("Z")

    def is_number(self, key):
        """ retorna True si es un numero"""
        return key >= ord("0") and key <= ord("9")

    def is_character(self, key):
        """ retorna si es un caracter """
        return self.is_letter(key) or self.is_number(key)

    def is_word_complete(self, key):
        """ acompleta las palabara de cada juego """
        self.is_complete = self.v_sub_layout.is_word_complete(key)



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
        self.sub_lay.init_box_layout(layout)

        # Set widget to contain window contents
        wid.setLayout(layout)

        # inicializacion
        self.init_configuration()

    def init_configuration(self):
        """ inicializa todas las configuraciones iniciales """
        # self.sub_lay.open_srt(SRT_FILE)
        self.sub_lay.init_sub_layout(SRT_FILE, debug_mode=True)

    # esta funcion es necesaria incluirla en la ventan principal
    def keyPressEvent(self, event):
        """ key press event """
        if type(event) == QtGui.QKeyEvent:
            key = event.key()
            if self.sub_lay.is_character(key):
                self.sub_lay.is_word_complete(key)

    def exitCall(self):
        """ cierra la apliccaion """
        sys.exit(app.exec_())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())