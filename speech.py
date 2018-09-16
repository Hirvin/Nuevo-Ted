# export GOOGLE_APPLICATION_CREDENTIALS=~/Documentos/Hirvin/Proyectos/Ted_Test/NuevoTed/claves/key.json
# pip install --upgrade google-api-python-client

import speech_recognition as sr
from diff import diff_match_patch


def get_speech(sub_text=""):
    """ get the speech """
    you_said = None
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)

    print "Procesing audio"

    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use,
        # r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")
        # instead of `r.recognize_google(audio)
        you_said = str(r.recognize_google(audio))
        print "Google Speech Recognition thinks you said: " + you_said
    except sr.UnknownValueError:
        print "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        print "Could not request results from Google Speech Recognition service; {0}".format(e)


    # recognize speech using Google Cloud Speech
    # with open(r"/home/hirvin/Documentos/Hirvin/Proyectos/Ted_Test/NuevoTed/claves/key.json", "r") as f:
    #     credentials_json = f.read()
    # try:
    #     print("Google Cloud Speech thinks you said " + r.recognize_google_cloud(audio, credentials_json=credentials_json))
    # except sr.UnknownValueError:
    #     print("Google Cloud Speech could not understand audio")
    # except sr.RequestError as e:
    #     print("Could not request results from Google Cloud Speech service; {0}".format(e))
    if you_said is None:
        return None

    dmp = diff_match_patch()
    diff = dmp.diff_main(sub_text.lower(), you_said.lower())
    dmp.diff_cleanupSemantic(diff)
    return diff, you_said


def get_audio():
    """ get audio from microphone """
    # obtain audio from the microphone
    record = sr.Recognizer()
    with sr.Microphone() as source:
        print "Say something!"
        audio = record.listen(source)
        return audio
    return None


def get_differences(audio=None, sub_text=""):
    """ get diferences """
    you_said = None
    if audio is None:
        return None, None

    record = sr.Recognizer()
    print "Procesing audio"

    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use,
        # r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")
        # instead of `r.recognize_google(audio)
        you_said = str(record.recognize_google(audio))
        print "Google Speech Recognition thinks you said: " + you_said
    except sr.UnknownValueError:
        print "Google Speech Recognition could not understand audio"
    except sr.RequestError as error:
        print "Could not request results from Google Speech Recognition service; {0}".format(error)

    if you_said is None:
        return None, None

    dmp = diff_match_patch()
    diff = dmp.diff_main(sub_text.lower(), you_said.lower())
    dmp.diff_cleanupSemantic(diff)
    return diff, you_said




# get_speech()