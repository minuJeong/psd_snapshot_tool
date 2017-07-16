
import wave
from pyaudio import PyAudio


CHUNK = 1024
wf = wave.open("sample.wav", 'rb')

audio = PyAudio()
stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)


# read data
data = wf.readframes(CHUNK)
# play stream (3)
while len(data) > 0:
    print(data, len(data))
    stream.write(data)
    data = wf.readframes(CHUNK)

# stop stream (4)
stream.stop_stream()
stream.close()

# close PyAudio (5)
audio.terminate()
