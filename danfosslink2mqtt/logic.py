import paho.mqtt.client as mqtt
import uuid
import time
import requests
import json
from decimal import Decimal
import urllib
import argparse
import danfosslink2mqtt.config as config 

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker.")
    else:
        print("Connection error. RC: ", rc)

def on_message(client, userdata, message):
    try:
        print("Setting room temperature")
        print(message.topic)

        room_name = ""
        for room in config.CONFIG["thermostats"]:
            if room["target_temperature"] == message.topic:
                print("inside if")
                print(message.topic)
                room_name = room["name"]

                break
        
        m = "set the temperature in {1} to {0}".format((((Decimal(message.payload.decode("UTF-8")) * 9/5) + 32)), room_name)
        print(m)
        x = urllib.parse.quote(m)
        u = "https://virtual-device.bespoken.io/process?user_id={0}&message=".format(config.CONFIG["bespoken_token"]) + x
        response = requests.get(u)
        print(response.text)
    except Exception as e:
        print(e)

def to_celsius(temperature):
    return ((Decimal(temperature) - 32) * 5/9).to_eng_string()

def do_logic():
    client = mqtt.Client("Danfoss2Mqtt")
    client.connect(config.CONFIG["mqtt"]["host"])
    client.on_message=on_message

    for room in config.CONFIG["thermostats"]:
        client.subscribe(room["target_temperature"])

    client.loop_start()
 
    while True:
        print("Looping")
        for room in config.CONFIG["thermostats"]:
            print(room["name"])

            url = "https://virtual-device.bespoken.io/process?user_id={0}&message=What%20is%20the%20temperature%20at%20{1}?".format(config.CONFIG["bespoken_token"], room["name"])
            response = requests.get(url)
            print(response.text)
            data = json.loads(response.text)
            print(data["transcript"])
   
            x = data["transcript"].split(" ")
            
            message = {}
            message["name"] = room["name"]
            message["temperature"] = to_celsius(x[5])

            print(json.dumps(message))

            client.publish("{0}".format(room["current_temperature"]),  to_celsius(x[5]))
    
        time.sleep(600)
