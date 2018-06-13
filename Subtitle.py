# enlace para descargar subtitulos : http://www.amara.org/en/teams/ted/
""" contiene todo el prototipo para obtener los subtitulos """
import re
from GlobalConstant import NUM_WORD_BY_SUB
# NUM_WORD_BY_SUB = 15

END_FRAME_STAMP = "** End frame **"
SPLIT_TIME = r"(\d+):(\d+):(\d+)\,(\d+)"


class FrameTime(object):
    """SubFrameTime, contiene informacion del tiempo de un sub frame"""
    def __init__(self):
        self.hour = 0
        self.min = 0
        self.sec = 0
        self.mil = 0
        self.time_milis = 0

    def clean(self):
        """ setea en 0 todos los campos """
        self.hour = 0
        self.min = 0
        self.sec = 0
        self.mil = 0
        self.time_milis = 0

    def get_time_milis(self):
        """ retorna el valor del tiempo en milis """
        return self.time_milis

    def set_time(self, data):
        """ set time from data"""
        split_time = re.match(SPLIT_TIME, data).groups()
        self.hour = int(split_time[0])
        self.min = int(split_time[1])
        self.sec = int(split_time[2])
        self.mil = int(split_time[3])
        self.time_milis = self.mil + (self.sec * 1000)
        self.time_milis += self.min * 60 * 1000
        self.time_milis += self.hour * 60 * 60 * 1000

    def __str__(self):
        txt = "%d:%d:%d.%d => %d" % (self.hour, self.min,
                                     self.sec, self.mil, self.time_milis)
        return txt


class SubBuffer(object):
    """ contine el buffer de datos del subtitle"""
    def __init__(self):
        self.buffer = []

    def open_srt(self, txt_srt):
        """ open srt file """
        with open(txt_srt, 'r') as f_read:
            read_data = f_read.read()
            self.buffer = read_data.replace("\r", "")
            self.buffer = self.buffer.replace("\n", " ").split(" ")
            self.buffer[0] = 1
            f_read.close()
            return True
        return False

    def set_end_frames(self):
        """ pone una marca en cada end frame """
        for i_index in range(len(self.buffer)):
            if self.buffer[i_index] == "":
                self.buffer[i_index] = END_FRAME_STAMP

    def get_srt(self, txt_srt):
        """ obtiene la informacion y la trata del archivo srt """
        if self.open_srt(txt_srt) is True:
            self.set_end_frames()
            return True
        print "No es posible hacer open"
        return False

    def print_buffer(self):
        """ imprime todo el contenido de buffer """
        for n_element in self.buffer:
            print n_element

    def get_word(self):
        """ return actaul word """
        word = None
        if self.buffer != []:
            word = self.buffer.pop(0)
        else:
            print "Buffer vacio"
        return word

    def get_len(self):
        """ return actual len of the buffer """
        return len(self.buffer)

    def has_head(self):
        """ return true if has head """
        return self.get_len() > 3

    def is_end_frame(self):
        """ verify is end frame, if pop it """
        is_end_frame = False

        if self.buffer[0] == END_FRAME_STAMP:
            self.buffer.pop(0)
            is_end_frame = True
        else:
            is_end_frame = False
        return is_end_frame

    def is_not_empty(self):
        """ retorna True si el buffer esta vacio """
        if self.buffer == []:
            return False
        return True


class FrameSrt(object):
    """ contiene la estructura de un frame de subtitulo"""
    def __init__(self):
        self.number = None
        self.init_time = FrameTime()
        self.end_time = FrameTime()
        self.words = []

    def set_number(self, number):
        """ set number of frame """
        self.number = int(number)

    def set_init_time(self, init_time):
        """ set init time of frame """
        self.init_time.set_time(init_time)

    def set_end_time(self, end_time):
        """ set end time of frame """
        self.end_time.set_time(end_time)

    def set_word(self, word):
        """ set word of frame """
        self.words.append(word)

    def set_head(self, buffer_srt):
        """ obtiene la informacion de la cabeza del frame """
        if buffer_srt.has_head():
            self.set_number(buffer_srt.get_word())
            self.set_init_time(buffer_srt.get_word())
            buffer_srt.get_word()
            self.set_end_time(buffer_srt.get_word())
            return True
        return False

    def get_frame(self, buffer_srt):
        """ obtitne toda la informacion del frame """
        if self.set_head(buffer_srt) is True:
            while buffer_srt.is_end_frame() is False:
                self.set_word(buffer_srt.get_word())
            # se comprueba que no se sobrepase el maximo numero de palabras
            if len(self.words) > NUM_WORD_BY_SUB:
                print "El Numero de palabras es mayor a %d total: %d" % \
                    (NUM_WORD_BY_SUB, len(self.words))
                return False
            return True
        return False

    def __str__(self):
        """ imprime el frame """
        number_txt = "number = " + str(self.number)
        init_txt = "init time: " + str(self.init_time)
        end_txt = "end time: " + str(self.end_time)
        words_txt = str(self.words)
        next_txt = " ******************* \n"
        return number_txt + '\n' + init_txt + '\n' + end_txt + '\n' \
            + words_txt + '\n' + next_txt


class Subtitle(object):
    """ contitne toda la estructura sobre los subtitulos """
    def __init__(self):
        self.buffer_srt = SubBuffer()
        self.buffer_frames = []
        self.num_frames = 0
        self.ready = False
        self.index = 0

    def open_srt(self, txt_srt):
        """ carga el archivo srt al buffer """
        return self.buffer_srt.get_srt(txt_srt)

    def get_frame(self):
        """ obtiene un frame del buffer """
        frame = FrameSrt()
        if frame.get_frame(self.buffer_srt) is True:
            return frame
        return None

    def get_frames(self):
        """ carga todos los frames dentro de buffer frames """
        while self.buffer_srt.is_not_empty():
            frame = self.get_frame()
            if frame is not None:
                self.buffer_frames.append(frame)
            else:
                return False
        self.ready = True
        self.num_frames = len(self.buffer_frames)
        return True

    def is_ready(self):
        """ devuelve True si Subtitle esta listo """
        return self.ready

    def is_prev_ready(self):
        """ devulve si el buffer esta activo ante un prev event """
        if self.index > 2:
            # print "index: %d True" % (self.index)
            return True
        # print "index: %d False" % (self.index)
        return False

    def is_next_ready(self):
        """ verifica el evento next es valido """
        if self.index < (self.num_frames - 2):
            return True
        return False

    def get_next_word(self):
        """ retorna el texto del siguiente frame """
        if self.index < self.num_frames:
            frame = self.buffer_frames[self.index]
            # print str(self.index) + ": " + str(frame.words)
            self.index += 1
            return frame.words
        return None

    def get_prev_word(self):
        """ retorna el texto del anterior frame """
        if self.index > 2:
            self.index -= 1
            frame = self.buffer_frames[self.index - 2]
            # print str(self.index) + ": " + str(frame.words)
            return frame.words
        return None

    def print_frames(self):
        """ imprime todos los frames """
        for i_element in self.buffer_frames:
            print i_element

# 0 hola 1   2 mama 3
# 1 casa 2   3 papa 4


# este es solo codigo de pruebas no se ejecuta al cargar el modulo
if __name__ == '__main__':
    test = Subtitle()
    test.open_srt("sub.srt")
    test.get_frames()
    test.print_frames()
