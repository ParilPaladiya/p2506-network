import json
import os
import time
from collections import deque
from statistics import mean, stdev
import paho.mqtt.client as mqtt
import mysql.connector
from datetime import datetime

# MQTT Config 
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT   = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC  = "sensor/+/temperature"

# MySQL Config
MYSQL_HOST  = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER  = os.getenv("MYSQL_USER", "root")
MYSQL_PASS  = os.getenv("MYSQL_ROOT_PASSWORD")
MYSQL_DB    = os.getenv("MYSQL_DATABASE", "sensor_db")

# Thresholds config
TEMP_NORMAL_MAX   = float(os.getenv("TEMP_NORMAL_MAX", 22))   
TEMP_WARNING_MAX  = float(os.getenv("TEMP_WARNING_MAX", 25))  
ANOMALY_STD_MULT  = float(os.getenv("ANOMALY_STD_MULT", 2.5)) 
ANOMALY_REPEAT    = int(os.getenv("ANOMALY_REPEAT", 3))       
WINDOW_SIZE       = int(os.getenv("WINDOW_SIZE", 25))         

# MySQL connection with retry
def get_db():
    while True:
        try:
            db = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASS,
                database=MYSQL_DB
            )
            print("Connected to MySQL")
            return db
        except Exception as e:
            print(f"Waiting for MySQL... ({e})")
            time.sleep(5)

db     = get_db()
cursor = db.cursor()

# State Tracking
device_history  = {}
anomaly_counter = {}

# Alert Logic
def get_base_state(temp: float) -> str:
    if temp > TEMP_WARNING_MAX:
        return "CRITICAL"
    elif TEMP_NORMAL_MAX <= temp <= TEMP_WARNING_MAX:
        return "WARNING"
    else:
        return "NORMAL"

def detect_anomaly(values: list[float]) -> bool:
    if len(values) < WINDOW_SIZE:
        return False
    avg = mean(values)
    sd  = stdev(values)
    latest = values[-1]
    return latest > (avg + ANOMALY_STD_MULT * sd)

def evaluate_alert(device_id: str, temperature: float, history: deque) -> str:
    # Append new reading
    history.append(temperature)
    last_values = list(history)

    base_state = get_base_state(temperature)
    anomaly    = detect_anomaly(last_values)

    # Update anomaly counter
    if anomaly:
        anomaly_counter[device_id] += 1
    else:
        anomaly_counter[device_id] = 0

    # Escalate if anomalies persist
    if anomaly_counter[device_id] >= ANOMALY_REPEAT:
        return f"ANOMALY DETECTED : {last_values}"
    else:
        return base_state

# MQTT Callbacks 
def on_connect(client, userdata, flags, rc):
    print("System started.....")
    print("Connected to MQTT broker")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global db, cursor
    try:
        payload     = json.loads(msg.payload.decode())
        device_id   = payload["device_id"]
        temperature = float(payload["temperature"])

        # Initialize history + anomaly counter if first time
        if device_id not in device_history:
            device_history[device_id]  = deque(maxlen=WINDOW_SIZE)
            anomaly_counter[device_id] = 0

        # Evaluate alert state
        alert_state = evaluate_alert(device_id, temperature, device_history[device_id])

        # Insert alert into MySQL
        sql = """
        INSERT INTO temperature_alerts
            (timestamp, device_id, temperature, alert_level)
        VALUES (%s, %s, %s, %s)
        """
        values = (datetime.now(), device_id, temperature, alert_state)

        # Reconnect if MySQL dropped
        try:
            cursor.execute(sql, values)
            db.commit()
        except mysql.connector.Error:
            db     = get_db()
            cursor = db.cursor()
            cursor.execute(sql, values)
            db.commit()

        # Console output
        print(f"\n{'='*36}")
        print(f"Device ID       : {device_id}")
        print(f"Temperature     : {temperature} °C")
        print(f"Alert State     : {alert_state}")
        print(f"Anomaly Counter : {anomaly_counter[device_id]}")
        print(f"{'='*36}")

    except Exception as e:
        print("Error:", e)

# Start MQTT 
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

while True:
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        break
    except Exception as e:
        print(f"Waiting for MQTT broker... ({e})")
        time.sleep(3)

client.loop_forever()
