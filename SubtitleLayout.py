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
SAY_BUTTON = 3
PREV_BUTTON = 4

# CSS labels colors
CSS_BASE_COLOR_NO_HOVER = "QLabel{color: SlateGrey; font-size: 25px; font-weight: bold;}"
CSS_BASE_COLOR = "QLabel{color: SlateGrey; font-size: 25px; font-weight: bold;} QLabel:hover{background: rgba(70,130,180,0.25); color: SlateGrey; font-size: 25px; font-weight: bold;}"
CSS_CORRECT_COLOR = "QLabel{color: SteelBlue; font-size: 25px; font-weight: bold;} QLabel:hover{background: rgba(70,130,180,0.25); color: SteelBlue; font-size: 25px; font-weight: bold;}"
CSS_WARNING_COLOR = "QLabel{color: LightSteelBlue; font-size: 25px; font-weight: bold;} QLabel:hover{background: rgba(70,130,180,0.25); color: LightSteelBlue; font-size: 25px; font-weight: bold;}"
CSS_ERROR_COLOR = "QLabel{color: IndianRed; font-size: 25px; font-weight: bold;} QLabel:hover{background: rgba(70,130,180,0.25); color: IndianRed; font-size: 25px; font-weight: bold;}"
# say mode
CSS_BASE_SAY_COLOR = "QLabel{color: Green; font-size: 25px; font-weight: bold;}"
CSS_CORRECT_SAY_COLOR = "QLabel{color: Blue; font-size: 25px; font-weight: bold;}"


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
        self.state = PREV_BUTTON

    def enable_prev_button(self):
        """ enable prev button """
        print "enable prev button 3"
        self.setEnabled(True)
        self.setText("Prev")
        self.update()
        self.state = PREV_BUTTON

    def say_something(self):
        """ say something display """
        self.setEnabled(True)
        self.setText("Saying")
        self.update()

    def say_button(self):
        """ say button """
        self.setEnabled(True)
        self.setText("Say")
        self.state = SAY_BUTTON

    def get_state(self):
        """ retorna el valor de state """
        return self.state


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

    def say_button(self):
        """ say button """
        self.setEnabled(True)
        self.setText("Say")
        self.state = SAY_BUTTON

    def get_state(self):
        """ retorna el valor de state """
        return self.state


SPELL_MODE = 0
VOICE_MODE = 1


class LbWord2(QLabel):
    """ estructura de una palabra """
    def __init__(self, parent=None):
        super(LbWord2, self).__init__(parent)
        self.setText(" ")
        self.valid_word = True
        self.word = " "
        # self.show_word = ""
        self.setStyleSheet(CSS_BASE_COLOR_NO_HOVER)
        self.mode = SPELL_MODE
        self.cnt_word = 0
        self.lst_chr = []
        self.is_spell_completed = False
        self.is_voice_completed = False
        self.word_xml = None
        self.dictionary = PyDictionary()

    def set_word(self, word_xml):
        """ set word"""
        self.clean()
        word = word_xml[0].text
        self.word_xml = word_xml

        if word == "None_field":
            self.valid_word = False
            return False

        self.word = word

        if word_xml.attrib["is_completed"] == 'True':
            self.is_spell_completed = True
            self.cnt_word = int(word_xml.attrib["cnt_word"])
            self.evaluate_error()
        else:
            self.lst_chr = list(re.sub(r'[\W]', '', word))
            self.setText(self.replace_word(word))
            self.setStyleSheet(CSS_BASE_COLOR)

        return True

    def replace_word(self, word):
        """ remplaza las letras y numero por *"""
        if self.lst_chr == []:
            return word
        re_word = word[::-1]
        # replace any word character \w
        re_word = re.sub(r"\w", POINTER_WORD, re_word, len(self.lst_chr))
        return re_word[::-1]

    def evaluate_error(self):
        """ evalua los errores y los clasifica """
        if self.cnt_word < 2:
            self.setStyleSheet(CSS_CORRECT_COLOR)
        elif self.cnt_word < 4:
            self.setStyleSheet(CSS_WARNING_COLOR)
        elif self.cnt_word >= 4:
            self.setStyleSheet(CSS_ERROR_COLOR)
        self.setText(self.replace_word(self.word))

    def evaluate_key(self, key=None, debug=False):
        """ evaluate key in word """
        if key is None:
            return False
        is_completed = False

        if self.lst_chr[0].upper() == chr(key):
            self.lst_chr.pop(0)
        else:
            self.cnt_word += 1

        if debug is True:
            show_word = self.replace_word(self.word)
            print "word: %s cnt_word: %d left_word: %s show_word: %s" % (self.word, self.cnt_word, str(self.lst_chr), show_word)

        if (self.lst_chr == []) or (self.cnt_word >= 4):
            self.lst_chr = []
            is_completed = True
            self.word_xml.attrib["is_completed"] = "True"
            self.is_spell_completed = True
            self.word_xml.attrib["cnt_word"] = str(self.cnt_word)

        self.evaluate_error()

        return is_completed

    def init_voice_mode(self):
        """ init say mode """
        self.setStyleSheet(CSS_BASE_SAY_COLOR)
        self.mode = VOICE_MODE
        if self.word_xml.attrib["is_voice_completed"] == 'True':
            self.setStyleSheet(CSS_CORRECT_SAY_COLOR)
            self.is_voice_completed = True

    def set_voice_completed(self):
        """set voice completed """
        self.setStyleSheet(CSS_CORRECT_SAY_COLOR)
        self.word_xml.attrib["is_voice_completed"] = "True"
        self.is_voice_completed = True

    def __str__(self):
        """ __str__ """
        return self.word

    def mousePressEvent(self, event):
        """ ejecuta accion al presional el label """
        if self.valid_word is False:
            if self.mode == SPELL_MODE and self.is_spell_completed:
                word = re.sub(REPLACE_WORD_TO_DICTIONARY, "", self.word)
                text = str(self.dictionary.meaning(word))
                print text

    def clean(self):
        """ clean """
        self.setText(" ")
        self.valid_word = True
        self.word = " "
        self.setStyleSheet(CSS_BASE_COLOR_NO_HOVER)
        self.mode = SPELL_MODE
        # self.show_word = ""
        self.cnt_word = 0
        self.lst_chr = []
        self.is_spell_completed = False
        self.is_voice_completed = False
        self.word_xml = None


class WordArray(object):
    """ array of words """
    def __init__(self, max_words=0):
        self.lst_words = []
        self.lst_spell = []
        self.lst_voice = []
        self.is_spell_complete = False
        self.frame = None

        for element in range(max_words):
            self.lst_words.append(LbWord2())

    def set_frame(self, frame=None):
        """ set frame words """
        if frame is None:
            return False

        self.frame = frame

        self.clean()

        line1 = frame.get_line(line_number=0)
        line2 = frame.get_line(line_number=1)
        cnt = 0

        # set line 1
        for word_field in line1:
            self.lst_words[cnt].set_word(word_field)
            cnt += 1

        # set line 2
        for word_field in line2:
            self.lst_words[cnt].set_word(word_field)
            cnt += 1

        self.init_internal_lst()

        return True

    def init_internal_lst(self):
        """ initializate lst_spell and lst_voice """
        for word in self.lst_words:
            if word.valid_word is True:
                if word.is_spell_completed is False:
                    self.lst_spell.append(word)
        return True

    def evaluate_key_spell(self, key=None, debug=False):
        """ evaluate new key entered """
        if key is None:
            return False

        if self.is_spell_complete is True:
            return True

        if self.frame.get_is_text_complete_frame() is True:
            self.is_spell_complete = True
            return True

        if self.lst_spell[0].evaluate_key(key, debug=debug) is True:
            self.lst_spell.pop(0)

        if self.lst_spell == []:
            self.is_spell_complete = True
            self.frame.set_is_text_complete_frame("True")
            self.frame.save()
            return True

        return False

    def process_diff_voice_word(self, word_said=None, debug=False):
        """ proccess each word """
        is_match = "False"
        if word_said is None:
            return False

        for word in self.lst_voice:
            e_word = re.sub(r"[^\w\']", '', word.word).lower()

            if e_word == word_said:
                is_match = True
                word.set_voice_completed()
                self.lst_voice.pop(self.lst_voice.index(word))
            else:
                is_match = False

            if debug is True:
                print "Evaluating %s == %s -- %s, [%d]" % (word_said, e_word, str(is_match), len(self.lst_voice))

            if self.lst_voice == []:
                return True

            if is_match is True:
                return False

        return False

    def process_voice(self, diff=None, debug=False):
        """ evaluate the diff said words """
        if diff is None:
            return False

        if self.lst_voice == []:
            return True

        for value, txt in diff:
            if value == 0:
                for word_said in txt.split(" "):
                    if (word_said != " ") and (word_said != ''):
                        if self.process_diff_voice_word(word_said=word_said, debug=debug) is True:
                            return True
        return False

    def init_voice_mode(self):
        """ init say mode """
        for word in self.lst_words:
            if word.valid_word:
                word.init_voice_mode()
                if word.is_voice_completed is False:
                    self.lst_voice.append(word)

    def __str__(self):
        """ __str__ """
        txt = '['
        for word in self.lst_voice:
            txt += word.word + " "
        return txt + ']'

    def clean(self):
        """ clean all words """
        self.lst_spell = []
        self.lst_voice = []
        self.is_spell_complete = False
        # self.frame = None
        for word in self.lst_words:
            word.clean()


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
        self.is_none = False

    def get_word(self):
        """ return word if is not space """
        if self.word != " ":
            return self.word + " "
        return ""

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


    def evaluate_errors(self):
        """ evalua lo errore en cada palabra """
        if self.is_none is False:
            if (self.index_chr == 0) and (self.cnt_word == 0):
                self.setStyleSheet(CSS_BASE_COLOR)
            elif self.cnt_word < 2:
                self.setStyleSheet(CSS_CORRECT_COLOR)
            elif self.cnt_word < 4:
                self.setStyleSheet(CSS_WARNING_COLOR)
            elif self.cnt_word >= 4:
                self.setStyleSheet(CSS_ERROR_COLOR)


    def init_text(self, word):
        """ inicializa la palabra en el label """
        self.word_xml = word
        self.word = word[0].text
        if self.word == "None":
            self.setStyleSheet(CSS_BASE_COLOR_NO_HOVER)
            self.word = " "
            self.word_xml = " "
            self.is_none = True
        else:
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


    def clean(self):
        """ limpia la estrucutra de LbWord """
        self.setText(" ")
        self.update()
        self.is_complete = False
        self.index_chr = 0
        self.word = ""
        self.dsp_word = ""
        self.cnt_word = 0
        self.index_curr_word = 0
        self.key_out = False
        self.word_xml = None
        self.setStyleSheet(CSS_BASE_COLOR_NO_HOVER)
        self.is_none = False


class SubLine(QHBoxLayout):
    """ Contiene una linea de palbras de subtitulo """
    def __init__(self, parent=None, line_number=0, lst_word=None):
        super(SubLine, self).__init__(parent)
        self.words = []
        self.set_layout(lst_word)
        self.line_number = line_number
        self.is_complete = False
        self.key_out = False

    def set_layout(self, lst_words):
        """ add to layout a especific list of words """
        self.addStretch()
        for word in lst_words:
            self.addWidget(word)
        self.addStretch()


class SubVBox(QVBoxLayout):
    """ box que contienen todos los labels para los subtitles """
    def __init__(self, parent=None, word_array=None):
        super(SubVBox, self).__init__(parent)

        self.sub_line1 = SubLine(line_number=0,
                                 lst_word=word_array.lst_words[:15])
        self.sub_line2 = SubLine(line_number=1,
                                 lst_word=word_array.lst_words[15:])

        self.addLayout(self.sub_line1)
        self.addLayout(self.sub_line2)


class SubtitleLayout(QHBoxLayout):
    """ layout con toda la estructura para subtitulos """
    def __init__(self, parent=None, debug=False):
        # estructura del widget de subtitulos
        super(SubtitleLayout, self).__init__(parent)
        self.debug_mode = False

        # hirvin mejor afuera
        self.frame_buffer = None
        self.arr_words = WordArray(max_words=30)

        self.prev_button = PrevButton()
        self.next_button = NextButton()
        self.v_sub_layout = SubVBox(word_array=self.arr_words)
        # verifica si las palabras esta completa
        self.is_complete = True

        self.addWidget(self.prev_button)
        self.addLayout(self.v_sub_layout)
        self.addWidget(self.next_button)

        # subitle slide initialization
        self.sub_slider = SubSlider()

    def get_words_text_voice(self):
        """ get the text for all lines """
        return ''.join(e.word + " " for e in self.arr_words.lst_voice)

    def say_something(self):
        """ say something action """
        self.prev_button.say_something()

    def disable_next_button(self):
        """ deshabilita el next button """
        self.next_button.disable_button()

    def enable_next_button(self):
        """ habilita el button """
        self.next_button.enable_button()

    def enable_prev_button(self):
        """ habilitando prev button """
        print "enable prev button 2"
        self.prev_button.enable_prev_button()

    def repeat_next_button(self):
        """ repite el button """
        self.next_button.repeat_button()

    def init_voice_mode(self):
        """ init say mode """
        # self.v_sub_layout.init_say_mode()
        self.arr_words.init_voice_mode()
        self.prev_button.say_button()

    def get_state_next_button(self):
        """ retorna el valor de state """
        return self.next_button.get_state()

    def get_state_prev_button(self):
        """ retorna el vlaor del state """
        return self.prev_button.get_state()

    def init_sub_layout(self, frame_buffer, debug_mode=False):
        """ carga las configuraciones iniciales del sub layout """
        self.debug_mode = debug_mode

        self.frame_buffer = frame_buffer
        self.set_frame_in_words(frame=self.frame_buffer)

        # falta improvisar el slider
        self.sub_slider.set_range(0, 100 ) # cambiar esta por el numero maximo de frame ###########################
        self.sub_slider.set_value(2)

    def set_frame_in_words(self, frame=None):
        """ set the word into the frame """
        if frame is None:
            return False
        self.arr_words.set_frame(frame)

    def init_box_layout(self, parent):
        """ se anade asi mismo a la estrutura principal """
        parent.addWidget(self.sub_slider)
        parent.addLayout(self)

    def next_clicked(self):
        """ handler para cuando se presina next button """
        self.set_frame_in_words(frame=self.frame_buffer)

    def prev_clicked(self):
        """ handler prev button """
        self.set_frame_in_words(frame=self.frame_buffer)


    def is_letter(self, key):
        """ retorna True si es una letra """
        return key >= ord("A") and key <= ord("Z")

    def is_number(self, key):
        """ retorna True si es un numero"""
        return key >= ord("0") and key <= ord("9")

    def is_character(self, key):
        """ retorna si es un caracter """
        return self.is_letter(key) or self.is_number(key)

    def is_spell_complete(self, key):
        """ acompleta las palabara de cada juego """
        return self.arr_words.evaluate_key_spell(key=key)

    def process_voice_diff(self, diff):
        """ evaluate the said text """
        return self.arr_words.process_voice(diff=diff)

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
                if self.sub_lay.is_spell_complete(key) is True:
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
