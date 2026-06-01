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
    
#--------- Simple dashboard in Flask ---------

# Displays the latest moisture readings realtime
# Auto-refreshes every 2 seconds to show new data from the SQLite database
@app.route("/dashboard")
def dashbaord():
    conn = get_db()
    rows = conn.execute("""
        SELECT id, sensor_name, moisture_value, protocol, created_at
        FROM moisture_readings
        ORDER BY id DESC
        LIMIT 30
    """).fetchall()
    conn.close()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Soil Moisture Dashboard</title>
        <meta http-equiv="refresh" content="2">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 30px;
                background: #f4f4f4;
            }
            h1 {
                color: #333;
            }
            table {
                border-collapse: collapse;
                width: 100%
                background: white;
            }
            th, td {
                padding: 10px;
                border: 1px solid #ccc;
                text-align: left;
            }
            th {
                background: #333;
                color: white;
            }
         </style>
     </head>
     <body>
         <h1>Soil Moisture Dashboard</h1>
         <p>Auto-refresh every 2 seconds</p>

         <table>
             <tr>
                 <th>ID</th>
                 <th>Sensor</th>
                 <th>Moisture</th>
                 <th>Protocol</th>
                 <th>Timestamp</th>
             </tr>
    """

    for row in rows:
        html += f"""
            <tr>
                <td>{row["id"]}</td>
                <td>{row["sensor_name"]}</td>
                <td>{row["moisture_value"]}</td>
                <td>{row["protocol"]}</td>
                <td>{row["created_at"]}</td>
            </tr>
        """


    html += """
        </table>
    </body>
    </html>
    """

    return html

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
