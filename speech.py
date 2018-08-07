# export GOOGLE_APPLICATION_CREDENTIALS=~/Documentos/Hirvin/Proyectos/Ted_Test/NuevoTed/claves/key.json
# pip install --upgrade google-api-python-client

import speech_recognition as sr

# obtain audio from the microphone
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)


# try:
#     # for testing purposes, we're just using the default API key
#     # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
#     # instead of `r.recognize_google(audio)`
#     print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
# except sr.UnknownValueError:
#     print("Google Speech Recognition could not understand audio")
# except sr.RequestError as e:
#     print("Could not request results from Google Speech Recognition service; {0}".format(e))


# recognize speech using Google Cloud Speech
with open(r"/home/hirvin/Documentos/Hirvin/Proyectos/Ted_Test/NuevoTed/claves/key.json", "r") as f:
    credentials_json = f.read()
try:
    print("Google Cloud Speech thinks you said " + r.recognize_google_cloud(audio, credentials_json=credentials_json))
except sr.UnknownValueError:
    print("Google Cloud Speech could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Cloud Speech service; {0}".format(e))