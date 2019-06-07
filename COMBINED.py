"""
Python MQTT Subscription client
Thomas Varnish (https://github.com/tvarnish), (https://www.instructables.com/member/Tango172)
Written for my Instructable - "How to use MQTT with the Raspberry Pi and ESP8266"
"""

# USE TERMINAL TO RUN THIS FILE
# Plug in breadboard, run arduino, and press the button!!

import paho.mqtt.client as mqtt
import io
import os
import json

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

# Don't forget to change the variables for the MQTT broker!
mqtt_username = "hcdeiot"
mqtt_password = "esp8266"
mqtt_topic = "Button"
mqtt_broker_ip = "mediatedspaces.net"

response = ''

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

def recording():
    print ("entering recording")
    form_1 = pyaudio.paInt16 # 16-bit resolution
    chans = 1 # 1 channel
    samp_rate = 44100 # 44.1kHz sampling rate
    chunk = 4096 # 2^12 samples for buffer
    record_secs = 5 # seconds to record
    dev_index = 1 # device index found by p.get_device_info_by_index(ii)
    wav_output_filename = 'test1.wav' # name of .wav file
    
    audio = pyaudio.PyAudio() # create pyaudio instantiation
    print('after audio')
##    client = speech.SpeechClient()

    print('before stream')
    # create pyaudio stream
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=chunk)
    print("recording")
    frames = []

    # loop through stream and append audio chunks to frame array
    for ii in range(0,int((samp_rate/chunk)*record_secs)):
        data = stream.read(chunk)
        frames.append(data)

    print("finished recording")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    wavefile = wave.open(wav_output_filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

def googlevoice():
    print('haha3')
    # The name of the audio file to transcribe
    file_name = os.path.join(
    ##    os.path.dirname(__file__),
    ##    'resources',
        'test1.wav')

    print(file_name)

    # Loads the audio into memory
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    print('haha4')

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        # sample_rate_hertz=16000,
        language_code='en-US')

    print('haha5')
    client = speech.SpeechClient()
    # Detects speech in the audio file
    response = client.recognize(config, audio)
    print('haha6')
    print(response)

    for result in response.results:
        print('Transcript: {}'.format(result.alternatives[0].transcript))




def sentiment():
    print ('last part')

    # Instantiates a client
    client = language.LanguageServiceClient()
    
    print('before doc')
    # The text to analyze
    text = response
    
    ###### TESTING LINE
##    text = "I am so stressful"
    
    document = l_types.Document(
        content=text,
        type=l_enums.Document.Type.PLAIN_TEXT)

    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(document=document).document_sentiment

    print('Text: {}'.format(text))
    print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude)) 
    print("DONE")
    play_audio(sentiment.score)
    if (sentiment.score >-2):
        mqtt_client.publish("Sentiment","on") 
    

def play_audio(score):
    print("start playing")
    if (score > -2):
        saying = AudioSegment.from_wav("test1.wav")
        play(saying)
    
    
def on_message(mqtt_client, userdata, msg):
    print ("enter on_message")
    # This function is called everytime the topic is published to.
    # If you want to check each message, and do something depending on
    # the content, the code to do this should be run in this function
    
    print ("Topic: ")
    print (msg.topic) 
    print ("\nMessage: ")
    print (str(msg.payload))
    print("calling google voice")

    recording()
    googlevoice()
    sentiment()
##    mqtt_client.publish("LAB", "testing")

    
    
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


# Once we have told the client to connect, let the client object run itself
mqtt_client.loop_forever()
mqtt_client.disconnect()

##############


