from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "moisture.db"

# Connect Flask to the database
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Initiate the database with table
def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS moisture_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_name TEXT NOT NULL,
            moisture_value INTEGER NOT NULL,
            protocol TEXT NOT NULL,
            created_at TEXT NOT NULL

        )
    """)
    conn.commit()
    conn.close()

# Home route to verify that the Flask server is running
# Accessible via browser at: http://<IP>:5000/
@app.route("/")
def home():
    return "Soil Moisture Flask Server is running"

# API endpoint to receive moisture data from IoT devices (Pico W)
# Method: POST
# Expects JSON with: sensor_name, moisture_value, protocol
# Saves the data into the SQLite database
@app.route("/api/moisture", methods=["POST"])
def add_moisture():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    sensor_name = data.get("sensor_name")
    moisture_value = data.get("moisture_value")
    protocol = data.get("protocol")

    if sensor_name is None or moisture_value is None or protocol is None:
        return jsonify({"error": "Missing sensor_name, moisture_value or protocol"})

    conn = get_db()
    conn.execute("""
        INSERT INTO moisture_readings
        (sensor_name, moisture_value, protocol, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        sensor_name,
        int(moisture_value),
        protocol,
        datetime.now().isoformat(timespec="seconds")
    ))
    conn.commit()
    conn.close()

    return jsonify({"message": "Reading saved"}), 201


@app.route("/api/moisture", methods=["GET"])
def get_moisture():
    conn = get_db()
    rows = conn.execute("""
        SELECT id, sensor_name, moisture_value, protocol, created_at
        FROM moisture_readings
        ORDER BY id DESC
        LIMIT 100
    """).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
