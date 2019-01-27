import paho.mqtt.client as mqtt
import uuid
import time
import requests
import json
from decimal import Decimal
import urllib
from .configparser import ConfigParser
import argparse

CONFIG = {}

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
        for room in CONFIG["thermostats"]:
            if room["target_temperature"] == message.topic:
                print("inside if")
                print(message.topic)
                room_name = room["name"]

                break
        
        m = "set the temperature in {1} to {0}".format((((Decimal(message.payload.decode("UTF-8")) * 9/5) + 32)), room_name)
        print(m)
        x = urllib.parse.quote(m)
        u = "https://virtual-device.bespoken.io/process?user_id={0}&message=".format(CONFIG["bespoken_token"]) + x
        response = requests.get(u)
        print(response.text)
    except Exception as e:
        print(e)


def do_logic():
    client = mqtt.Client("Danfoss2Mqtt")
    client.connect(CONFIG["mqtt"]["host"])
    client.on_message=on_message

    for room in CONFIG["thermostats"]:
        client.subscribe(room["target_temperature"])

    client.loop_start()
 
    while True:
        print("Looping")
        for room_name in CONFIG["thermostats"]:
            print(room_name["name"])

            url = "https://virtual-device.bespoken.io/process?user_id={0}&message=What%20is%20the%20temperature%20at%20{1}?".format(CONFIG["bespoken_token"], room_name["name"])
            response = requests.get(url)
            print(response.text)
            data = json.loads(response.text)
            print(data["transcript"])
    
            x = data["transcript"].split(" ")
            client.publish("{0}".format(room_name["current_temperature"]),  ((Decimal(x[5]) - 32) * 5/9).to_eng_string())
    
        time.sleep(600)

def parse_config():
    global CONFIG
    
    parser = argparse.ArgumentParser("DanfossLink2MQTT")
    parser.add_argument("--config", action = "store", default = "/config.yaml")

    args = parser.parse_args()

    config = ConfigParser().parse_config(args.config)
    CONFIG = config

def main():
    parse_config()

    do_logic()

if __name__ == "__main__":
    main()

