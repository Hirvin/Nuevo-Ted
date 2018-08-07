import xml.etree.ElementTree as ET
import re

NUM_WORD_BY_SUB = 15

# indexes
FRAME_TXT_WORD_INDEX = 0
FRAME_INDEX = 1
HEAD_INDEX = 0 

# regex expresion
REGEX_SPLIT_TIME_STAMP = r"([\d\:\.]+)\,([\d\:\.]+)"
REGEX_TIME_VALUES = r"(\d+)\:(\d+)\:(\d+)\.(\d+)"


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
        split_time = re.match(REGEX_TIME_VALUES, data).groups()
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


class SbvToXml(object):
    """ manejo del archivo sbv """
    def __init__(self):
        """ covierte un archivo sbv a FrameXml """
        self.in_buffer = []
        self.start_time = FrameTime()
        self.end_time = FrameTime()
        self.data_buffer = []

    def open_sbv(self, path):
        """ abre y porcesa el archivo sbv """
        with open(path, 'r') as f_read:
            read_data = f_read.read()
            self.in_buffer = read_data.replace("\r", "")
            self.in_buffer = self.in_buffer.replace("[br]", "")
            self.in_buffer = self.in_buffer.replace("\n", " ").split(" ")
            f_read.close()
            return True
        return False

    def print_buffer(self):
        """ print buffer """
        for line in self.in_buffer:
            print line

    def get_frames(self):
        """ get frames """
        while self.in_buffer != []:

            # line = self.in_buffer.pop(0)
            # print line
            print "Start Frame ##################"
            self.get_start_time()
            if self.get_data_frame() is False:
                return False
            print "---------------------------"
            self.get_end_time()
            if self.get_data_frame() is False:
                return False
            print "End Frame ####################\n"
            return True

    def get_start_time(self):
        """ get start time """
        if self.in_buffer == []:
            return False

        time_stamps = None

        while time_stamps is None:
            line = self.in_buffer.pop(0)
            time_stamps = re.match(REGEX_SPLIT_TIME_STAMP, line)

        self.start_time.set_time(time_stamps.groups()[0])
        self.end_time.set_time(time_stamps.groups()[1])
        print "start time: " + str(self.start_time)
        return True

    def get_end_time(self):
        """ get start time """
        if self.in_buffer == []:
            return False

        time_stamps = None

        while time_stamps is None:
            line = self.in_buffer.pop(0)
            time_stamps = re.match(REGEX_SPLIT_TIME_STAMP, line)

        self.end_time.set_time(time_stamps.groups()[1])
        print "end time: " + str(self.end_time)
        return True

    def get_data_frame(self):
        """ obtiene los datos del frame """
        if self.in_buffer == []:
            return False

        self.data_buffer = []

        word = self.in_buffer.pop(0)
        while word != "":
            print word
            self.data_buffer.append(word)
            word = self.in_buffer.pop(0)
        if len(self.data_buffer > NUM_WORD_BY_SUB):
            print "data buffes have more than 15 elements"
            return False
        return True

    def print_in_buffer(self):
        """ imprime el contenido de in_buffer """
        for line in self.in_buffer:
            print line


class FrameXml(object):
    """ manejo del Frame XML """
    def __init__(self):
        """ init method """
        self.root = ET.Element('Ted_Subtitle')
        self.head = None
        self.frame = None

    def create_head(self, parent):
        """ create Head """
        head = ET.SubElement(parent, "Head")
        head_title = ET.SubElement(head, "Title")
        head_number_frames = ET.SubElement(head, "Number_frames")
        head_number_completed_frames = ET.SubElement(head, "Number_completed_frames")
        head_title.text = "hola Mundo"
        head_number_frames.text = "0"
        head_number_completed_frames.text = "0"
        return head

    def create_frame(self, parent):
        """ creat one single frame """
        frame = self.init_frame(parent)
        return frame

    def init_frame(self, parent):
        """ create Frame """
        frame = ET.SubElement(parent, "Frame")
        frame.set('number', '1')

        frame_init_time = ET.SubElement(frame, "init_time")
        frame_end_time = ET.SubElement(frame, "end_time")
        text_line1 = ET.SubElement(frame, "text_line1")
        text_line2 = ET.SubElement(frame, "text_line2")
        self.create_text_line(text_line1, "text_line1")
        self.create_text_line(text_line2, "text_line2")

        frame_init_time.text = "0"
        frame_end_time.text = "0"

        return frame

    def create_text_line(self, parent, name):
        """ create text line """
        text_line = ET.SubElement(parent, name)
        self.create_words(text_line)
        return text_line

    def create_words(self, parent):
        """ create all words """
        lst_words = []
        for index in range(NUM_WORD_BY_SUB):
            word = self.init_word(parent)
            self.set_word(word, index, " ")
            lst_words.append(word)

    def init_word(self, parent):
        """ create word """
        word = ET.SubElement(parent, "word")
        word.set('is_completed', 'False')
        word.set('cnt_word', '0')
        word.set('index', '0')
        txt_word = ET.SubElement(word, "txt_word")
        txt_word.text = "hola"
        return word

    def set_word(self, element=None, index='0', word=" "):
        """ set word """
        if element is not None:
            element.attrib['index'] = str(index)
            element[FRAME_TXT_WORD_INDEX].text = word

    def create(self):
        self.head = self.create_head(self.root)
        self.frame = self.create_frame(self.root)

    def save(self, path):
        """ save the xml """
        tree = ET.ElementTree(self.root)
        tree.write("test.xml", xml_declaration=True, encoding='utf-8')


xml = FrameXml()
xml.create()
xml.save("test.xml")

# svb = SbvToXml()
# svb.open_sbv("test.sbv")
# svb.get_frames()