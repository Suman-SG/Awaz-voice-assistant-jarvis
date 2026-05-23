# import speech_recognition as sr
# import pyttsx3

# recognizer = sr.Recognizer()
# engine = pyttsx3.init()

# def speak(text):
#     engine.say(text)
#     engine.runAndWait()

# def listen(timeout=8, phrase_time_limit=8):
#     try:
#         with sr.Microphone() as source:
#             print("Listening...")
#             recognizer.adjust_for_ambient_noise(source, duration=0.8)
#             audio = recognizer.listen(
#                 source,
#                 timeout=timeout,
#                 phrase_time_limit=phrase_time_limit
#             )
#         text = recognizer.recognize_google(audio)
#         print("You said:", text)
#         return text.lower()


#     except sr.WaitTimeoutError:
#         print("Listening timeout")
#         return ""

#     except sr.UnknownValueError:
#         print("Could not understand audio")
#         return ""

#     except sr.RequestError:
#         print("Speech service error")
#         return ""
import time

import speech_recognition as sr
import pyttsx3

import config

recognizer = sr.Recognizer()
engine = pyttsx3.init("sapi5")

def speak(text):
    print("Jarvis says:", text)
    engine.setProperty("rate", config.SPEECH_RATE)
    engine.setProperty("volume", config.SPEECH_VOLUME)

    voices = engine.getProperty("voices")
    if voices:
        voice_index = min(max(config.SPEECH_VOICE_INDEX, 0), len(voices) - 1)
        engine.setProperty("voice", voices[voice_index].id)

    engine.say(text)
    engine.runAndWait()
    time.sleep(config.SPEAK_BUFFER_DELAY)

def listen(timeout=8, phrase_time_limit=8):
    try:
        # Small pause to ensure any recent TTS playback has finished
        time.sleep(0.25)
        with sr.Microphone() as source:
            print("Listening...")
            # Shorter ambient calibration so we don't re-capture the assistant's own speech
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text.lower()


    except sr.WaitTimeoutError:
        print("Listening timeout")
        return ""

    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""

    except sr.RequestError:
        print("Speech service error")
        return ""
    except Exception as e:
        print("Error during listening:", str(e))
        return ""
