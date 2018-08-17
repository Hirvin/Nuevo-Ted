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
from XmlHandler import HandlerXml

# see QColor(0, 200, 0)

# definicion de constantes
[MAX_BUTTON_WIDTH, MAX_BUTTON_HIGH] = [80, 80]
# NUM_WORD_BY_SUB = 15

# constantes del programa
SRT_FILE = "test.xml"
REPLACE_WORD_TO_ASTERISC = r"[a-zA-Z0-9]"
REPLACE_WORD_TO_DICTIONARY = r"[/,/./-/_]"
POINTER_WORD = '*'



ENABLE_BUTTON = 0
DISABLE_BUTTON = 1
REAPEAT_BUTTON = 2

# CSS labels colors
CSS_BASE_COLOR = "QLabel{color: SlateGrey; font-size: 25px; font-weight: bold;} QLabel:hover{background: rgba(70,130,180,0.25); color: SlateGrey; font-size: 25px; font-weight: bold;}"
CSS_CORRECT_COLOR = "QLabel{color: SteelBlue; font-size: 25px; font-weight: bold;} QLabel:hover{background: rgba(70,130,180,0.25); color: SteelBlue; font-size: 25px; font-weight: bold;}"
CSS_WARNING_COLOR = "QLabel{color: LightSteelBlue; font-size: 25px; font-weight: bold;} QLabel:hover{background: rgba(70,130,180,0.25); color: LightSteelBlue; font-size: 25px; font-weight: bold;}"
CSS_ERROR_COLOR = "QLabel{color: IndianRed; font-size: 25px; font-weight: bold;} QLabel:hover{background: rgba(70,130,180,0.25); color: IndianRed; font-size: 25px; font-weight: bold;}"


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
        # self.setEnabled(False)
        self.state = ENABLE_BUTTON

    def enable_button(self):
        """ habilita el boton """
        self.setEnabled(True)
        self.setText("Next")
        self.state = ENABLE_BUTTON

    def disable_button(self):
        """ desabilita el boton """
        self.setEnabled(False)
        self.state = DISABLE_BUTTON

    def repeat_button(self):
        """ repetir button """
        self.setEnabled(True)
        self.setText("Repeat")
        self.state = REAPEAT_BUTTON

    def get_state(self):
        """ retorna el valor de state """
        return self.state


class LbWord(QLabel):
    """ estructura de una palabra """
    def __init__(self, parent=None):
        super(LbWord, self).__init__(parent)
        self.setText("")
        self.is_complete = False
        # self.word = []
        self.index_chr = 0
        # self.word_point = []
        self.word = ""
        # palabra que se muestra
        self.dsp_word = ""
        self.cnt_word = 0
        self.dictionary = PyDictionary()
        self.index_curr_word = 0
        self.key_out = False
        self.word_xml = None

    def mousePressEvent(self, event):
        """ ejecuta accion al presional el label """
        if self.word != "" and self.is_complete:
            word = re.sub(REPLACE_WORD_TO_DICTIONARY, "", self.word)
            text = str(self.dictionary.meaning(word))
            print text

    def replace_word(self, word):
        """ remplaza las letras y numero por *"""
        return re.sub(REPLACE_WORD_TO_ASTERISC, POINTER_WORD, word)

    def find_letter(self):
        """ encuentra la primera letra disponible """
        for letter in self.dsp_word[self.index_chr:]:
            if letter == POINTER_WORD:
                return True
            self.index_chr += 1
        return False

    def complete_word(self, key):
        """ acompleta las palabras """
        if key is None:
            return False

        if self.find_letter() is False:
            self.is_complete = True

        if self.is_complete is False:
            key_w = chr(key)
            if key_w == self.word[self.index_chr].upper():
                self.index_chr += 1
                self.dsp_word = self.word[:self.index_chr] + self.replace_word(self.word[self.index_chr:])
            else:
                self.cnt_word += 1
                self.word_xml.attrib["cnt_word"] = str(self.cnt_word)

            if (self.dsp_word == self.word) or (self.cnt_word >= 4):
                self.dsp_word = self.word
                self.is_complete = True
                self.key_out = True
                self.word_xml.attrib["is_completed"] = 'True'

            # print "%s (%s) : cnt = %d" % (self.word, key_w, self.cnt_word)
            self.evaluate_errors()
            self.setText(self.dsp_word)

        return self.is_complete

    def evaluate_errors(self):
        """ evalua lo errore en cada palabra """
        if (self.index_chr == 0) and (self.cnt_word == 0):
            self.setStyleSheet(CSS_BASE_COLOR)
        elif (self.cnt_word < 2):
            self.setStyleSheet(CSS_CORRECT_COLOR)
        elif self.cnt_word < 4:
            self.setStyleSheet(CSS_WARNING_COLOR)
        elif self.cnt_word >= 4:
            self.setStyleSheet(CSS_ERROR_COLOR)


    def init_text(self, word):
        """ inicializa la palabra en el label """
        self.word_xml = word
        self.word = word[0].text
        self.setStyleSheet(CSS_BASE_COLOR)

        if word.attrib["is_completed"] == 'True':
            self.is_complete = True
            self.dsp_word = self.word
        else:
            self.is_complete = False
            self.dsp_word = self.replace_word(self.word)

        self.cnt_word = int(word.attrib["cnt_word"])
        self.index_curr_word = int(word.attrib["index"])
        self.evaluate_errors()
        self.setText(self.dsp_word)

    def is_word_complete(self, key):
        """ determina si la palabra es completa """
        if self.is_complete is True:
            return True
        return self.complete_word(key)

    def clean(self):
        """ limpia la estrucutra de LbWord """
        self.setText(" ")
        self.update()
        self.is_complete = False
        self.index_chr = 0
        self.word = ""
        # palabra que se muestra
        self.dsp_word = ""
        self.cnt_word = 0
        self.index_curr_word = 0
        self.key_out = False
        self.word_xml = None
        self.setStyleSheet(CSS_BASE_COLOR)


class SubLine(QHBoxLayout):
    """ Contiene una linea de palbras de subtitulo """
    def __init__(self, parent=None, line_number=0):
        super(SubLine, self).__init__(parent)
        self.words = []
        self.create_words()
        self.set_layout()
        self.line_number = line_number
        self.is_complete = False
        self.key_out = False
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

    def set_words(self, frame, debug_mode=False):
        """ actualiza el subtitulo con el valor de words """
        self.clean()

        index = 0
        line_words = frame.get_line(line_number=self.line_number)
        for i_word in line_words:
            self.words[index].init_text(i_word)
            index += 1

            if debug_mode:
                if i_word[0].text != " ":
                    print i_word[0].text
        if debug_mode:
            print "#################################"
        return True

    def clean(self):
        """ limpia todas las palabras """
        self.is_complete = False
        self.key_out = False
        for i_word in self.words:
            i_word.clean()

    def is_word_complete(self, key):
        """ is word complete """
        if self.is_complete:
            return True

        if key is None:
            return False

        for word in self.words:
            if word.is_word_complete(key) is False:
                return False
            else:
                if word.key_out is True:
                    key = None
                    word.key_out = False

        self.is_complete = True
        self.key_out = True
        return True


class SubVBox(QVBoxLayout):
    """ box que contienen todos los labels para los subtitles """
    def __init__(self, parent=None):
        super(SubVBox, self).__init__(parent)
        self.sub_line1 = SubLine(line_number=0)
        self.sub_line2 = SubLine(line_number=1)

        self.addLayout(self.sub_line1)
        self.addLayout(self.sub_line2)

    def set_sub_line1(self, frame, debug_mode=False):
        """ setea las palabras en la linea 1 """
        self.sub_line1.set_words(frame, debug_mode)

    def set_sub_line2(self, frame, debug_mode=False):
        """ setea las palabras en la linea 2 """
        self.sub_line2.set_words(frame, debug_mode)

    def is_word_complete(self, key):
        """ is word complete"""
        if self.sub_line1.is_word_complete(key) is True:
            if self.sub_line1.key_out:
                key = None
                self.sub_line1.key_out = False
            return self.sub_line2.is_word_complete(key)
        return False


class SubtitleLayout(QHBoxLayout):
    """ layout con toda la estructura para subtitulos """
    def __init__(self, parent=None, debug=False):
        # estructura del widget de subtitulos
        super(SubtitleLayout, self).__init__(parent)
        self.debug_mode = False

        # hirvin mejor afuera
        self.frame_buffer = None

        # self.sub_buffer = Subtitle2()

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

        # # inicializacion de los eventos
        # if debug is True:
        #     self.next_button.clicked.connect(self.next_clicked)
        # self.prev_button.clicked.connect(self.prev_clicked)

    def disable_next_button(self):
        """ deshabilita el next button """
        self.next_button.disable_button()

    def enable_next_button(self):
        """ habilita el button """
        self.next_button.enable_button()

    def repeat_next_button(self):
        """ repite el button """
        self.next_button.repeat_button()

    def get_state_next_button(self):
        """ retorna el valor de state """
        return self.next_button.get_state()

    def init_sub_layout(self, frame_buffer, debug_mode=False):
        """ carga las configuraciones iniciales del sub layout """
        self.debug_mode = debug_mode

        # mejor afuera
        self.frame_buffer = frame_buffer

        # hirvin cambiar por nueva implementacion
        self.v_sub_layout.set_sub_line1(self.frame_buffer, self.debug_mode)
        self.v_sub_layout.set_sub_line2(self.frame_buffer, self.debug_mode)
        self.sub_slider.set_range(0, 100 ) # cambiar esta por el numero maximo de frame ###########################

        self.sub_slider.set_value(2)

    def init_box_layout(self, parent):
        """ se anade asi mismo a la estrutura principal """
        parent.addWidget(self.sub_slider)
        parent.addLayout(self)

    def next_clicked(self):
        """ handler para cuando se presina next button """
        # if self.get_state_next_button() == ENABLE_BUTTON:
        #     if self.sub_buffer.is_next_ready() is True:
        #         l1_word, l2_word = self.sub_buffer.get_next_word()
        #         self.v_sub_layout.set_sub_line1(l1_word, self.debug_mode)
        #         self.v_sub_layout.set_sub_line2(l2_word, self.debug_mode)
        #         self.sub_slider.set_value(self.sub_buffer.index_txt)
        #         self.is_complete = False
        #         self.repeat_next_button()
        # hirvin mejor afuera
        

        self.v_sub_layout.set_sub_line1(self.frame_buffer, self.debug_mode)
        self.v_sub_layout.set_sub_line2(self.frame_buffer, self.debug_mode)


    def prev_clicked(self):
        """ handler prev button """
        # hirvin cambiar prev clicked 
        # self.v_sub_layout.set_sub_line2(l2_word, self.debug_mode)
        # self.v_sub_layout.set_sub_line1(l1_word, self.debug_mode)
        # self.sub_slider.set_value(self.sub_buffer.index_txt)
        # hirvin mejor afuera
        

        self.v_sub_layout.set_sub_line1(self.frame_buffer, self.debug_mode)
        self.v_sub_layout.set_sub_line2(self.frame_buffer, self.debug_mode)

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
        return self.is_complete

    def exit(self):
        """ exit """
        pass


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
        self.sub_lay = SubtitleLayout(debug=True)
        self.sub_lay.init_box_layout(layout)

        # Set widget to contain window contents
        wid.setLayout(layout)

        # adicional elements
        self.frame_buffer = HandlerXml(SRT_FILE)

        # inicializacion
        self.init_configuration()

        # add signals
        self.sub_lay.next_button.clicked.connect(self.next_global_clicked)
        self.sub_lay.prev_button.clicked.connect(self.prev_global_clicked)

    def init_configuration(self):
        """ inicializa todas las configuraciones iniciales """
        # self.sub_lay.open_srt(SRT_FILE)
        self.sub_lay.init_sub_layout(self.frame_buffer, debug_mode=True)
        # self.sub_lay.repeat_next_button() # cambiar esta Hirvin

    # esta funcion es necesaria incluirla en la ventan principal
    def keyPressEvent(self, event):
        """ key press event """
        if type(event) == QtGui.QKeyEvent:
            key = event.key()
            if self.sub_lay.is_character(key):
                if self.sub_lay.is_word_complete(key) is True:
                    self.sub_lay.enable_next_button()

    def exitCall(self):
        """ cierra la apliccaion """
        sys.exit(app.exec_())

    def next_global_clicked(self):
        """ next global clicked """
        self.frame_buffer.save()
        self.frame_buffer.next_frame()
        self.sub_lay.next_clicked()

    def prev_global_clicked(self):
        """ prev global clicked """
        self.frame_buffer.prev_frame()
        self.sub_lay.prev_clicked()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())
