#include "Adafruit_Si7021.h"
#include <ESP8266WiFi.h>    //Requisite Libraries . . .
#include <PubSubClient.h>   //
#include <ArduinoJson.h>    //


const char* wifi_ssid = "University of Washington";
const char* wifi_password = "";

// MQTT
// Make sure to update this for your own MQTT Broker!
const char* mqtt_server = "mediatedspaces.net";
const char* mqtt_topic = "TreeWeather";
const char* mqtt_user = "hcdeiot";
const char* mqtt_password = "esp8266";
// The client id identifies the ESP8266 device. Think of it a bit like a hostname (Or just a name, like Greg).
const char* clientID = "f00b7d5027ca4a809c5ccf0fd10fd3dd";

Adafruit_Si7021 sensor = Adafruit_Si7021();

WiFiClient espClient;             //blah blah blah, espClient
PubSubClient mqtt(espClient);     //blah blah blah, tie PubSub (mqtt) client to WiFi client
char mac[6]; //A MAC address is a 'truly' unique ID for each device
char message[201]; // 201, as last character in the array is the NULL character, denoting the end of the array

// set up wifi
void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(wifi_ssid);
  WiFi.begin(wifi_ssid, wifi_password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected.");  //get the unique MAC address to use as MQTT client ID, a 'truly' unique ID.
  Serial.println(WiFi.macAddress());  //.macAddress returns a byte array 6 bytes representing the MAC address
}                                     //5C:CF:7F:F0:B0:C1 for example

// Monitor the connection to MQTT server, if down, reconnect
void reconnect() {
  // Loop until we're reconnected
  while (!mqtt.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (mqtt.connect(mac, mqtt_user, mqtt_password)) { //<<---using MAC as client ID, always unique!!!
      Serial.println("connected");
      mqtt.subscribe("Button"); //we are subscribing to 'theTopic' and all subtopics below that topic
    } else {                        //please change 'theTopic' to reflect your topic you are subscribing to
      Serial.print("failed, rc=");
      Serial.print(mqtt.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  // This is just for debugging purposes
  Serial.begin(115200);

  // Connect to the WiFi
  setup_wifi();
  mqtt.setServer(mqtt_server, 1883);
  mqtt.setCallback(callback); //register the callback function

  // wait for serial port to open
  while (!Serial) {
    delay(10);
  }

  Serial.println("Si7021 test!");
  
  if (!sensor.begin()) {
    Serial.println("Did not find Si7021 sensor!");
    while (true);
  }  
  mqtt.subscribe("Button");
}

void loop() {
  delay(1000); 
  if (!mqtt.connected()) {
    reconnect();
  }
 
  mqtt.loop(); //this keeps the mqtt connection 'active'
}


//By subscribing to a specific channel or topic, we can listen to those topics we wish to hear.
//We place the callback in a separate tab so we can edit it easier
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.println();
  Serial.print("Message arrived [");
  Serial.print(topic); //'topic' refers to the incoming topic name, the 1st argument of the callback function
  Serial.println("] ");

  DynamicJsonBuffer  jsonBuffer; // create the buffer
  JsonObject& root = jsonBuffer.parseObject(payload); //parse it!

  if (String(topic) == "Button" ) {
    Serial.println("Printing Messages...");
    String message = root["Button"];
    Serial.print("Button: ");
    Serial.println(message); 
    float tem = sensor.readTemperature();
    float hum = sensor.readHumidity();
    Serial.print("Humidity:    "); Serial.print(hum, 2);
    Serial.print("\tTemperature: "); Serial.println(tem, 2);

    char new_message[201];
    char str_temp[6]; //a temp array of size 6 to hold "XX.XX" + the terminating character
    //take temp, format it into 5 char array with a decimal precision of 2, and store it in str_temp
    char str_humd[6];
    
//    dtostrf(tem, 4, 2, str_temp);
//    dtostrf(hum, 4, 2, str_humd);
////    sprintf(new_message, "{\"temp\": \"%s\", \"humidity\": \"%s\"}", str_temp, str_humd);
//    sprintf(new_message, "{\"temp\":\"%s\"}", str_temp);
//    char str_temp[6]; //a temp array of size 6 to hold "XX.XX" + the terminating character
    //take temp, format it into 5 char array with a decimal precision of 2, and store it in str_temp

    dtostrf(sensor.readHumidity(), 5, 2, str_humd);       
    dtostrf(sensor.readTemperature(), 5, 2, str_temp);
    sprintf(new_message, "{\"temp\":\"%s\",\"humd\":\"%s\"}", str_temp, str_humd);//    
    Serial.print(new_message);
    mqtt.publish("TreeWeather", new_message);   // publishing data to MQTT

    
//    dtostrf(sensor.readTemperature(), 5, 2, str_temp);
//    char str_humd[6]; //a temp array of size 6 to hold "XX.XX" + the terminating character
//    dtostrf(sensor.readHumidity(), 5, 2, str_humd);        
//    sprintf(new_message, "{\"temp\":\"%s\",\"humd\":\"%s\"}", str_temp, str_humd);
//    Serial.print(new_message);
//    mqtt.publish("TreeWeather", new_message); 
  
  }
  if (!root.success()) { // well?
    Serial.println("parseObject() failed, are you sure this message is JSON formatted.");
    return;
  }   
  root.printTo(Serial); //print out the parsed message
  Serial.println(); //give us some space on the serial monitor read out
  
}
