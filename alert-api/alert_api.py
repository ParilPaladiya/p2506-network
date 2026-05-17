import os
from flask import Flask, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASS = os.getenv("MYSQL_ROOT_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DATABASE", "sensor_db")


def fetch_data(device_id, order):
    db = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB
    )
    cursor = db.cursor(dictionary=True)
    query = f"""
    SELECT device_id, temperature, alert_level, timestamp
    FROM temperature_alerts
    WHERE device_id = %s
    ORDER BY timestamp {order}
    """
    cursor.execute(query, (device_id,))
    rows = cursor.fetchall()

    for row in rows:
        if isinstance(row["timestamp"], datetime):
            row["timestamp"] = row["timestamp"].strftime("%Y-%m-%dT%H:%M:%S")

    cursor.close()
    db.close()
    return rows


# Grafana root health check connection
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "running", "message": "Grafana JSON API is ready"})


# Latest reading (for gauge) — DESC
@app.route("/alert/<device_id>", methods=["GET"])
def alert_latest(device_id):
    return jsonify(fetch_data(device_id, "DESC"))


# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
