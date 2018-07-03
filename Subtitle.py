# enlace para descargar subtitulos : http://www.amara.org/en/teams/ted/
""" contiene todo el prototipo para obtener los subtitulos """
import re
from GlobalConstant import NUM_WORD_BY_SUB
# NUM_WORD_BY_SUB = 15

END_FRAME_STAMP = "** End frame **"
END_LINE_STAMP = "** End Line **"
SPLIT_TIME = r"(\d+):(\d+):(\d+)\,(\d+)"
OUT_SRT_FILE = "sub.srt_ted"


class convertSrt(object):
    """ convierte el archivo srt a .srtTed"""
    def __init__(self):
        self.in_buffer = []
        self.out_buffer = []
        self.number_frame = 1

    def open_srt(self, txt_srt):
        """ open srt file """
        with open(txt_srt, 'r') as f_read:
            read_data = f_read.read()
            self.in_buffer = read_data.replace("\r", "")
            self.in_buffer = self.in_buffer.replace("\n", " ").split(" ")
            self.in_buffer[0] = 1
            f_read.close()
            return True
        return False

    def print_in_buffer(self):
        """ imprime el in buffer"""
        for line in self.in_buffer:
            print line

    def print_out_buffer(self):
        """ imprime el out buffer """
        for line in self.out_buffer:
            print line

    def set_end_frames(self):
        """ pone una marca en cada end frame """
        for i_index in range(len(self.in_buffer)):
            if self.in_buffer[i_index] == "":
                self.in_buffer[i_index] = END_FRAME_STAMP

    def is_not_in_empty(self):
        """ verifica si el buffer de entrada esta vacio """
        if self.in_buffer == []:
            return False
        return True

    def get_head(self):
        """ obtiene la cabecera de cada frame """
        if len(self.in_buffer) > 4:
            # elimina el numero de frame
            self.in_buffer.pop(0)
            # obtiene el init time
            init_time = self.in_buffer.pop(0)
            # elimina -->
            self.in_buffer.pop(0)
            # obtiene el end time
            end_time = self.in_buffer.pop(0)
            return init_time, end_time
        return None, None

    def get_words(self):
        """obtiene todas las palabras de una linea """
        words = []
        while self.in_buffer[0] != END_FRAME_STAMP:
            words.append(self.in_buffer.pop(0) + "\n")
        self.in_buffer.pop(0)
        return words

    def generate_out(self):
        """ genera el out buffer """
        while self.is_not_in_empty():
            self.out_buffer.append(str(self.number_frame) + "\n")
            init_time, end_time = self.get_head()
            self.out_buffer.append(init_time + "\n")
            self.out_buffer.append(end_time + "\n")
            n_end_time = len(self.out_buffer) - 1
            self.out_buffer.extend(self.get_words())
            if self.is_not_in_empty():
                init_time, end_time = self.get_head()
                self.out_buffer[n_end_time] = end_time + "\n"
                self.out_buffer.append(END_LINE_STAMP + "\n")
                self.out_buffer.extend(self.get_words())
            self.out_buffer.append(END_FRAME_STAMP + "\n")
            self.number_frame += 1

    def write_out(self):
        """ se guarda write """
        out_file = open(OUT_SRT_FILE, "w")
        # for line in self.out_buffer:
        #     print line
        #     out_file.write(line)
        out_file.writelines(self.out_buffer)
        out_file.close()

    def process(self, txt_srt):
        """ procesa toda la informacion"""
        if self.open_srt(txt_srt) is True:
            self.set_end_frames()
            self.generate_out()
            # self.print_out_buffer()
            self.write_out()
        else:
            print "No se pudo abrir el archivo SRT"


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


class subBuffer2(object):
    """ carga el valor de los archivos .ted_srt """
    def __init__(self):
        self.buffer = []

    def open_srt(self, txt_srt):
        """ carga el archivo srt"""
        with open(txt_srt, 'r') as f_read:
            read_data = f_read.read()
            self.buffer = read_data.split("\n")
            f_read.close()
            return True
        return False

    def print_buffer(self):
        """ imprime todo el contenido de buffer """
        for n_element in self.buffer:
            print n_element

    def process(self, txt_srt):
        """ genera las operaciones de buffer """
        if self.open_srt(txt_srt) is True:
            # self.print_buffer()
            return True
        else:
            print "No se pudo abrir el archivo"
            return False

    def is_not_empty(self):
        """ retorna True si el buffer esta vacio """
        if self.buffer == []:
            return False
        return True

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

    def is_end_frame(self):
        """ verify is end frame, if pop it """
        is_end_frame = False

        if self.buffer == []:
            return True

        if self.buffer[0] == END_FRAME_STAMP:
            self.buffer.pop(0)
            is_end_frame = True
        else:
            is_end_frame = False
        return is_end_frame

    def is_end_line(self):
        """ verify is end line, if pop it """
        is_end_line = False

        if self.buffer[0] == END_LINE_STAMP:
            self.buffer.pop(0)
            is_end_line = True
        else:
            is_end_line = False
        return is_end_line

    def is_end_line_stamp(self):
        """ determina si es end line de la linea 1 """
        if self.is_end_line() is True:
            return True
        if self.is_end_frame() is True:
            return True
        return False

    def has_head(self):
        """ return true if has head """
        return self.get_len() > 3


class FrameSrt2(object):
    """ contiene la estructura de un fram de subtitulo"""
    def __init__(self):
        self.number = None
        self.init_time = FrameTime()
        self.end_time = FrameTime()
        self.l1_word = []
        self.l2_word = []

    def set_number(self, number):
        """ set number of frame"""
        self.number = int(number)

    def set_init_time(self, init_time):
        """ set init time of frame """
        self.init_time.set_time(init_time)

    def set_end_time(self, end_time):
        """ set end time of frame """
        self.end_time.set_time(end_time)

    def set_head(self, buffer_srt):
        """ obtiene la informacion de la cabeza del frame """
        if buffer_srt.has_head():
            self.set_number(buffer_srt.get_word())
            self.set_init_time(buffer_srt.get_word())
            self.set_end_time(buffer_srt.get_word())
            return True
        return False

    def get_line1(self, buffer_srt):
        """ obtiene la line 1"""
        while buffer_srt.is_end_line_stamp() is False:
            self.l1_word.append(buffer_srt.get_word())
            # se comprueba que no se sobrepase el maximo numero de palabras
            if len(self.l1_word) > NUM_WORD_BY_SUB:
                print "El Numero de palabras es mayor a %d total: %d" % \
                    (NUM_WORD_BY_SUB, len(self.l1_word))
                return False
        return True

    def get_line2(self, buffer_srt):
        """ obtiene la linea 2"""
        if buffer_srt.is_not_empty() is False:
            return False
        while buffer_srt.is_end_frame() is False:
            word = buffer_srt.get_word()
            self.l2_word.append(word)
            # se comprueba que no se sobrepase el maximo numero de palabras
            if len(self.l2_word) > NUM_WORD_BY_SUB:
                print "El Numero de palabras es mayor a %d total: %d" % \
                    (NUM_WORD_BY_SUB, len(self.l2_word))
                return False
        return True

    def get_frame(self, buffer_srt):
        """ obtitne toda la informacion del frame """
        if self.set_head(buffer_srt) is True:
            if self.get_line1(buffer_srt) is False:
                return False
            if self.get_line2(buffer_srt) is False:
                return False
        return True

    def __str__(self):
        """ imprime el frame """
        number_txt = "number = " + str(self.number)
        init_txt = "init time: " + str(self.init_time)
        end_txt = "end time: " + str(self.end_time)
        words_txt = str(self.l1_word) + "\n" + str(self.l2_word)
        next_txt = " ******************* \n"
        return number_txt + '\n' + init_txt + '\n' + end_txt + '\n' \
                + words_txt + '\n' + next_txt
        #return ""


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

    def get_init_time_milis(self):
        """ retorona el valor en miles del init time """
        return self.init_time.get_time_milis()

    def get_end_time_miles(self):
        """ retorna el valor en miles del end time """
        return self.end_time.get_time_milis()


class Subtitle2(object):
    """ contiene toda la estructura sobre los subtitulos """
    def __init__(self):
        self.buffer_srt = subBuffer2()
        self.buffer_frames = []
        self.num_frames = 0
        self.ready = False

    def open_srt(self, txt_srt):
        """ carga el archivo srt al buffer """
        return self.buffer_srt.process(txt_srt)

    def get_frame(self):
        """ obtiene un frame del buffer """
        frame = FrameSrt2()
        if frame.get_frame(self.buffer_srt) is True:
            return frame
        return None

    def get_frames(self):
        """ carga todos los frames dentro del buffer framess """
        while self.buffer_srt.is_not_empty():
            frame = self.get_frame()
            if frame is not None:
                self.buffer_frames.append(frame)
            else:
                return False
        self.ready = True
        self.num_frames = len(self.buffer_frames)
        return True

    def print_frames(self):
        """ imprime todos los frames """
        for i_element in self.buffer_frames:
            print i_element


class Subtitle(object):
    """ contitne toda la estructura sobre los subtitulos """
    def __init__(self):
        self.buffer_srt = SubBuffer()
        self.buffer_frames = []
        self.num_frames = 0
        self.ready = False
        self.index = 0
        self.index_time = 0

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

    def get_init_time(self):
        """ obtiene el init time y el end time """
        if self.num_frames < 2:
            print "No es posible iniciar los tiempos inicales"
            return None, None
        # devuelve los valores iniciales
        init_time = self.buffer_frames[0].get_init_time_milis()
        end_time = self.buffer_frames[1].get_end_time_miles()
        return init_time, end_time

    def next_frame_time(self):
        """ retorna el next frame time """
        if self.index_time < self.num_frames:
            n_frames = self.num_frames - self.index_time
            if n_frames >= 2:
                self.index_time += 2
                init_time = self.buffer_frames[self.index_time].get_init_time_milis()
                end_time = self.buffer_frames[self.index_time + 1].get_end_time_miles()
            elif n_frames == 1:
                self.index_time += 1
                init_time = self.buffer_frames[self.index_time].get_init_time_milis()
                end_time = self.buffer_frames[self.index_time].get_end_time_miles()
            else:
                print "n_frames es igual 1"
            return init_time, end_time
        else:
            print "no se puede tomar time frames"

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
    # test = Subtitle()
    # test.open_srt("sub.srt")
    # test.get_frames()
    # test.print_frames()

    # convert = convertSrt()
    # convert.process("sub.srt")

    subtitle = Subtitle2()
    subtitle.open_srt(OUT_SRT_FILE)
    subtitle.get_frames()
    subtitle.print_frames()

    # sub_frames = FrameSrt2()

