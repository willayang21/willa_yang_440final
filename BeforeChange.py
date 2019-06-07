"""
Python MQTT Subscription client
Thomas Varnish (https://github.com/tvarnish), (https://www.instructables.com/member/Tango172)
Written for my Instructable - "How to use MQTT with the Raspberry Pi and ESP8266"
"""

# USE TERMINAL TO RUN THIS FILE
# Plug in breadboard, run arduino, and press the button!!
from __future__ import division
import paho.mqtt.client as mqtt
import io
import os
import json

import re
import sys

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/Desktop/key.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/Desktop/natural-lang-key.json"

# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud.language import enums as l_enums
from google.cloud.language import types as l_types

# Imports the Google Cloud client library
from google.cloud import speech
import pyaudio
import wave
from playsound import playsound
from pydub import AudioSegment
from pydub.playback import play
from six.moves import queue

# Don't forget to change the variables for the MQTT broker!
mqtt_username = "hcdeiot"
mqtt_password = "esp8266"
mqtt_topic = "Button"
mqtt_broker_ip = "mediatedspaces.net"
mqtt_topic2 = "TreeWeather/Temp"
mqtt_topic3 = "TreeWeather/Humd"

##finalResult = 'initial value'

##client.username_pw_set(mqtt_username, mqtt_password)
##client = mqtt.Client()

mqtt_client = mqtt.Client()
# Set the username and password for the MQTT client
mqtt_client.username_pw_set(mqtt_username, mqtt_password)


print("start")

# These functions handle what happens when the MQTT client connects
# to the broker, and what happens then the topic receives a message
def on_connect(mqtt_client, userdata, rc):
    print("enter on_connect")
    # rc is the error code returned when connecting to the broker
    print ("Connected!", str(rc))
    
    # Once the client has connected to the broker, subscribe to the topic
    client.subscribe(mqtt_topic)
    client.subscribe(mqtt_topic2)

# Audio recording parameters
RATE = 44100
CHUNK = int(RATE / 10)  # 100ms


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


def listen_print_loop(responses):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
##    ######
    myTranscript = ""
    transcript =""
    overwrite_chars = ""
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)
            
            myTranscript += transcript
            
            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Exiting..')
                break

            num_chars_printed = 0
            ##    myTranscript = myTranscript[0,-4]
    return myTranscript      

        
     

def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = 'en-US'  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        final = listen_print_loop(responses)
    return final
  
        
 

def sentiment(finalResult):
##    print ('last part')

    # Instantiates a client
    client = language.LanguageServiceClient()
    
##    print('before doc')
    # The text to analyze
##    finalResult="i am hnappy"
    text = finalResult
    print("What's the finalResult? ")
    print(finalResult)
        
    document = l_types.Document(
        content=text,
        type=l_enums.Document.Type.PLAIN_TEXT)

    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(document=document).document_sentiment

    print('Text: {}'.format(text))
    print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude)) 
    print("DONE")
    play_audio(sentiment.score)
    if (sentiment.score > 0.05):
        mqtt_client.publish("Sentiment","Positive")
    elif (sentiment.score < -0.05):
        mqtt_client.publish("Sentiment","Negative")
    else:
        mqtt_client.publish("Sentiment","Neutral")
##    

def play_audio(score):
    print("start playing1")
    if (score > 0.05):
        talking = AudioSegment.from_wav("positive.wav")
        play(talking)
    elif (score < -0.05):
        talking = AudioSegment.from_wav("negative.wav")
        play(talking)
    else :
        talking = AudioSegment.from_wav("neutral.wav")
        play(talking) 

def play_audio2(temp, humd):
    print("start playing2")

    if (temp > 30):
        mqtt_client.publish("WeatherLow","Low")
        talking = AudioSegment.from_wav("hotter.wav")
        play(talking)
    elif (temp < 10):
        mqtt_client.publish("WeatherLow","Low")
        talking = AudioSegment.from_wav("coldbutcantakeit.wav")
        play(talking)
    else:
        mqtt_client.publish("WeatheHigh","High")
        talking = AudioSegment.from_wav("perfect.wav")
        play(talking)
    if (humd < 20):
        mqtt_client.publish("WeatherLow","Low")
        talking = AudioSegment.from_wav("dry.wav")
        play(talking)
    
        
    
def on_message(mqtt_client, userdata, msg):
    print ("enter on_message")
    # This function is called everytime the topic is published to.
    # If you want to check each message, and do something depending on
    # the content, the code to do this should be run in this function
    
    print ("Topic: ")
    print (msg.topic) 
    print ("\nMessage: ")
    print (str(msg.payload))
    temp = 1.02
    humd = 1.01
    if (msg.topic == "TreeWeather/Temp"):
        temp = msg.payload
    elif msg.topic == "TreeWeather/Humd":
        humd = msg.payload            
##    main()
    final = main()
    if "weather" in final:
        play_audio2(temp, humd)
    else:
        sentiment(final)

    
    
    # The message itself is stored in the msg variable
    # and details about who sent it are stored in userdata
########## ADD A CALLBACK FUNCTION SO THAT TREE CAN HEAR
# Here, we are telling the client which functions are to be run
# on connecting, and on receiving a message
print('start connecting')
mqtt_client.on_connect = on_connect
print('start messaging')
mqtt_client.on_message = on_message

# Once everything has been set up, we can (finally) connect to the broker
# 1883 is the listener port that the MQTT broker is using
mqtt_client.connect(mqtt_broker_ip, 1883)
print(mqtt_broker_ip)
mqtt_client.subscribe(mqtt_topic)
mqtt_client.subscribe(mqtt_topic2)
mqtt_client.subscribe(mqtt_topic3)

# Once we have told the client to connect, let the client object run itself
mqtt_client.loop_forever()
mqtt_client.disconnect()

