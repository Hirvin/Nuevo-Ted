import json
from datetime import datetime

NUM_WORD_BY_SUB = 15

SUB_HEADER = {"title": "", "is_completed": False,
              "num_frames": 0, "completed_frames": 0, "offset": 11600}

SUB_WORD = {"is_text_completed": False, "is_speech_completed": False,
            "word": None, "n_text": 0, "n_voice": 0}
SUB_FRAME = {"is_text_completed": False, "is_speech_completed": False,
             "words": [], "start_time": 0, "end_time": 0}
SUB_END_FRAME = None
SUB_DATA = {"header": SUB_HEADER, "frames": []}


def get_time_milis(tm_str=None):
    """ get time in milis """
    if tm_str is None:
        return 0
    tm = datetime.strptime(tm_str, "%H:%M:%S.%f")
    tm_milis = tm.hour * 60
    tm_milis = (tm_milis + tm.minute) * 60
    tm_milis = (tm_milis + tm.second) * 1000
    tm_milis = tm_milis + (tm.microsecond * 0.001)
    return int(tm_milis)


def set_word(word=None):
    """ set a word """
    if word is None:
        return None

    sub_word = dict(SUB_WORD)
    sub_word["word"] = word
    return sub_word


def get_words(lines=None):
    """ get all the words from a text """
    if lines is None:
        return None

    words = [set_word(word) for word in lines.split(" ")]
    n_words = len(words)
    none_words = NUM_WORD_BY_SUB - n_words
    inf = int(none_words / 2)
    sup = none_words - inf
    return [None] * inf + words + [None] * sup


def get_frame(lines=None):
    """ trasnforms lines into a frame """
    if lines is None:
        return None

    frame = dict(SUB_FRAME)
    if len(lines) == 4:
        frame["start_time"] = get_time_milis(lines[0].split(",")[0])
        frame["end_time"] = get_time_milis(lines[2].split(",")[1])
        frame["words"] = get_words(lines[1]) + get_words(lines[3])
    else:
        frame["start_time"] = get_time_milis(lines[0].split(",")[0])
        frame["end_time"] = get_time_milis(lines[0].split(",")[1])
        frame["words"] = get_words(lines[1])
    # print frame["words"]
    return frame


def sbv_to_subframe(f_sbv=None):
    """ conver a sbv file to a SUB_DATA diccionario """
    if f_sbv is None:
        return None

    with open(f_sbv, "r") as f_read:
        lines = f_read.readlines()
        lines = [line.replace('\r\n', '') for line in lines]
        lines = [line.replace('[br]', ' ') for line in lines]
        lines = [line for line in lines if line != '']

    data_frame = dict(SUB_DATA)
    while lines:
        # print str(lines[0:4])
        data_frame["frames"].append(get_frame(lines[0:4]))
        del lines[0:4]
    data_frame["frames"].append(SUB_END_FRAME)
    data_frame["header"]["title"] = f_sbv.split('.')[0]
    data_frame["header"]["num_frames"] = len(data_frame["frames"])

    return data_frame


def subframe_to_json(sub_data=None, out_json=None):
    """ save the subframe into a json file """
    if sub_data is None:
        return False
    if out_json is None:
        return False

    with open(out_json, "w") as f_write:
        json.dump(sub_data, f_write, ensure_ascii=False)
        return True
    return False


def json_to_subframe(in_json=None):
    """ from json to subframe """
    if in_json is None:
        return None
    with open(in_json, "r") as f_read:
        return json.load(f_read)
    return None


class DataFrame(object):
    """ data frame with the information of sub.sbv """
    def __init__(self, in_json=None):
        self.data = json_to_subframe(in_json)
        self.index = 0
        self.out_json = in_json

    def get_init(self):
        """ restar index am return the firts frame """
        self.index = 0
        # return self.data["frames"][self.index]
        for frame in self.data["frames"][:-1]:
            if frame["is_speech_completed"] is False:
                return frame
            self.index += 1
        return self.data["frames"][self.index]

    def get_header(self):
        """ return the header """
        return self.data["header"]

    def get_frame(self):
        """ get current frame """
        return self.data["frames"][self.index]

    def get_prev(self):
        """ return prev frame """
        print self.index
        if self.index > 0:
            self.index -= 1
        return self.data["frames"][self.index]

    def get_next(self):
        """ return next frame """
        if self.data["frames"][self.index + 1] is not None:
            self.index += 1
        return self.data["frames"][self.index]

    def is_current_frame_text_completed(self):
        """ return the current state of the frame """
        return self.data["frames"][self.index]["is_text_completed"]

    def get_nframes(self):
        """ return the number of frames"""
        return self.data["header"]["num_frames"]

    def save(self):
        """ save the json file """
        subframe_to_json(self.data, self.out_json)

    def get_text_words(self):
        """ return the text of the words """
        frame = self.get_frame()
        return ''.join(word["word"] + " " for word in frame["words"] if word is not None)[:-1]

    def update_completed_frames(self):
        """ update the counter of completed frames """
        self.data["header"]["completed_frames"] += 1

    def n_completed_frames(self):
        """ return number of completed frames """
        return self.data["header"]["completed_frames"]


if __name__ == '__main__':
    data = sbv_to_subframe("test.sbv")
    subframe_to_json(data, "test_json.txt")
# with open("test_json.txt", "w") as f:
#     SUB_FRAME["words"] = [SUB_WORD, SUB_WORD, SUB_WORD]
#     SUB_DATA["frames"] = [SUB_FRAME, SUB_END_FRAME]
#     json.dump(SUB_DATA, f, ensure_ascii=False)
