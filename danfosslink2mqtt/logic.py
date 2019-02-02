import json
import re
import time
import urllib
from decimal import Decimal

import paho.mqtt.client as mqtt
import requests

import danfosslink2mqtt.config as config

#pylint: disable=unused-argument
def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("Connected to MQTT broker.")
    else:
        print("Connection error. RC: ", return_code)

#pylint: disable=unused-argument
def on_message(client, userdata, message):
    try:
        print("Setting room temperature")
        print(message.topic)

        room_name = ""
        for room in config.CONFIG["thermostats"]:
            if room["target_temperature"] == message.topic:
                room_name = room["name"]

                break
 
        m = "set the temperature in {1} to {0}".format(to_fahrenheit(message.payload.decode("UTF-8")), room_name)
        x = urllib.parse.quote(m)
        u = "https://virtual-device.bespoken.io/process?user_id={0}&message=".format(config.CONFIG["bespoken_token"]) + x
        response = requests.get(u)
        print(response.text)

    except Exception as e:
        print(e)

def to_fahrenheit(temperature):
    return ((Decimal(temperature)) * 9/5) + 32

def to_celsius(temperature):
    return ((Decimal(temperature) - 32) * 5/9).to_eng_string()

def do_logic():
    client = mqtt.Client("Danfoss2Mqtt")
    client.connect(config.CONFIG["mqtt"]["host"])
    client.on_message = on_message

    for room in config.CONFIG["thermostats"]:
        client.subscribe(room["target_temperature"])

    client.loop_start()

    while True:
        print("Looping")
        for room in config.CONFIG["thermostats"]:
            url = "https://virtual-device.bespoken.io/process?user_id={0}&message=What%20is%20the%20temperature%20at%20{1}?".format(config.CONFIG["bespoken_token"], room["name"])
            response = requests.get(url)

            if response.status_code == requests.codes.ok:
                handle_response(response, room, client)
            else: 
                print("Bad status from request.")
                print(response)

        time.sleep(600)

def handle_response(response, room, client):
    data = json.loads(response.text)

    match = re.search(r"(\d*.?\d)( degrees)", data["transcript"])

    if match.group(1) is not None:
        print("Temperature in {0} is {1}".format(room["name"], match.group(1)))
        message = {}
        message["name"] = room["name"]
        message["temperature"] = to_celsius(match.group(1))

        client.publish("{0}".format(room["current_temperature"]), json.dumps(message))
    else:
        print("Could not read data from Alexa. Result: {0}".format(data))
