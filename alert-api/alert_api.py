import os
from datetime import datetime

import psycopg2
from flask import Flask, jsonify
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DATABASE", "sensor_db")


def fetch_data(device_id, order):
    db = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASS,
        dbname=POSTGRES_DB,
    )
    cursor = db.cursor(cursor_factory=RealDictCursor)
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


# Latest reading (for gauge) - DESC
@app.route("/alert/<device_id>", methods=["GET"])
def alert_latest(device_id):
    return jsonify(fetch_data(device_id, "DESC"))


# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
