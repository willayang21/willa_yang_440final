import paho.mqtt.client as paho
broker="mediatedspaces.net"
port=1883
def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    pass


client = mqtt.Client()
# Set the username and password for the MQTT client
client.username_pw_set(mqtt_username, mqtt_password)

client.on_publish = on_publish                          #assign function to callback
client.connect(broker,port)                                 #establish connection
ret= client.publish("house/bulb1","on")                   #publish
