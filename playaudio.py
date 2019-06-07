

##import pyaudio
##import wave
##from playsound import playsound
##import gi
##gi.require_version('Gst', '1.0')
##from gi.repository import Gst, GLib
##
##Gst.init(None)
##
##playsound("/home/pi/Desktop/test1.wav")



from pydub import AudioSegment
from pydub.playback import play

song = AudioSegment.from_wav("test1.wav")
play(song)

