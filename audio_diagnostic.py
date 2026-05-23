import pyttsx3, tempfile, os
try:
    import winsound
except Exception:
    winsound = None

print('pyttsx3 version:', getattr(pyttsx3, '__version__', 'unknown'))
engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

wav = os.path.join(tempfile.gettempdir(), 'jarvis_tts_test.wav')
if os.path.exists(wav):
    try:
        os.remove(wav)
        print('removed existing', wav)
    except Exception as e:
        print('could not remove existing', e)

phrase = 'This is a playback test from Jarvis. If you hear this, playback worked.'
print('saving to', wav)
engine.save_to_file(phrase, wav)
engine.runAndWait()
print('saved exists?', os.path.exists(wav))
if winsound:
    try:
        print('attempting winsound playback')
        winsound.PlaySound(wav, winsound.SND_FILENAME)
        print('winsound finished')
    except Exception as e:
        print('winsound failed', type(e).__name__, e)
else:
    print('winsound not available on this platform')
print('done')
