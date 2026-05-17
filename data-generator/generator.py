import time
import random
import json
import os
import paho.mqtt.client as mqtt
from datetime import datetime

# Config (reads from environment variables set in docker-compose) 
BROKER   = os.getenv("MQTT_BROKER", "localhost")
PORT     = int(os.getenv("MQTT_PORT", 1883))
INTERVAL = int(os.getenv("DATA_INTERVAL", 5))

DEVICES = ["D001", "D002", "D003"]

# Retry connection until broker is ready 
client = mqtt.Client()

connected = False
while not connected:
    try:
        client.connect(BROKER, PORT, 60)
        connected = True
        print(f"Connected to MQTT broker at {BROKER}:{PORT}")
    except Exception as e:
        print(f"Waiting for broker... ({e})")
        time.sleep(3)

client.loop_start()
print("Multi-device generator started...")

while True:
    for device in DEVICES:
        temperature = round(random.uniform(20, 30), 2)
        topic = f"sensor/{device}/temperature"
        payload = {
            "device_id": device,
            "temperature": temperature,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        client.publish(topic, json.dumps(payload))
        print(f"Sent to {topic} → {payload}")

    time.sleep(INTERVAL)
