"""
server.py - Flask web server that runs on your laptop

This server receives sensor data from Pico W devices on your LAN.
The Pico W acts as a client and POSTs data to this server.

Compatible with main.py from hardware team:
- DHT22 temperature/humidity sensor on Pin 15
- MQ135 air quality sensor on GP26
- WHI (Waste Health Index) calculation with penalty breakdown

Configuration:
    Edit HOST and PORT variables below. Change PORT in one place
    and update SERVER_URL in main.py accordingly.

Usage:
    python server.py

Endpoints:
    POST /api/sensor-data  - Receive sensor data from Pico W
    POST /upload           - Alternative endpoint (backward compat)
    GET  /ping             - Health check
    GET  /data             - View all received data
    GET  /                 - Server status page
"""

from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# Server Configuration (change PORT here if needed)
HOST = "0.0.0.0"
PORT = 5000

# File to store raw sensor data (JSONL format)
RAW_DUMP_FILE = "raw_dump.jsonl"

# In-memory storage for recent readings (for /data endpoint)
recent_readings = []
MAX_READINGS = 100  # Keep last 100 readings in memory


@app.route("/api/sensor-data", methods=["POST"])
def receive_data():
    """
    Receive sensor data from Pico W.
    
    Compatible with main.py create_record() output:
    {
        "device_id": "PICO2W_001",
        "timestamp": "2026-07-01T12:30:00",
        "avg_nh3_ppm": 5.5,
        "peak_nh3_ppm": 6.2,
        "avg_h2s_ppm": 2.1,
        "avg_temperature_c": 28.5,
        "avg_humidity_percent": 65.0,
        "raw_whi": 85,
        "penalty_nh3": 10,
        "penalty_h2s": 8,
        "penalty_temperature": 0,
        "penalty_humidity": 5,
        "throughput": 0,
        "occupancy_inside": 0
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "No JSON data received"}), 400
        
        # Add server receive timestamp
        data["_received_at"] = datetime.utcnow().isoformat()
        
        # Save raw data to file (JSONL format - one JSON object per line)
        with open(RAW_DUMP_FILE, "a") as f:
            f.write(json.dumps(data) + "\n")
        
        # Keep in memory for /data endpoint
        recent_readings.append(data)
        if len(recent_readings) > MAX_READINGS:
            recent_readings.pop(0)  # Remove oldest
        
        # Print to console (matches main.py display format)
        print("\n" + "=" * 50)
        print("RECEIVED FROM:", data.get("device_id", "Unknown"))
        print("=" * 50)
        print("Timestamp    :", data.get("timestamp", "N/A"))
        print("Avg Temp     :", data.get("avg_temperature_c", "N/A"), "C")
        print("Avg Humidity :", data.get("avg_humidity_percent", "N/A"), "%")
        print("Avg NH3      :", data.get("avg_nh3_ppm", "N/A"), "ppm")
        print("Peak NH3     :", data.get("peak_nh3_ppm", "N/A"), "ppm")
        print("Avg H2S      :", data.get("avg_h2s_ppm", "N/A"), "ppm")
        print("WHI          :", data.get("raw_whi", "N/A"))
        print("Penalty NH3  :", data.get("penalty_nh3", "N/A"))
        print("Penalty H2S  :", data.get("penalty_h2s", "N/A"))
        print("Penalty Temp :", data.get("penalty_temperature", "N/A"))
        print("Penalty Hum  :", data.get("penalty_humidity", "N/A"))
        print("Throughput   :", data.get("throughput", "N/A"))
        print("Occupancy    :", data.get("occupancy_inside", "N/A"))
        print("Received at  :", data["_received_at"])
        print("=" * 50)
        
        return jsonify({"status": "ok", "message": "Data received successfully"}), 200
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# Also support /upload endpoint for backward compatibility
@app.route("/upload", methods=["POST"])
def receive_data_upload():
    """Alternative endpoint - same as /api/sensor-data"""
    return receive_data()


@app.route("/ping", methods=["GET"])
def ping():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "message": "Server is running",
        "timestamp": datetime.utcnow().isoformat(),
        "readings_count": len(recent_readings)
    }), 200


@app.route("/data", methods=["GET"])
def get_data():
    """Get all recent sensor readings."""
    return jsonify({
        "status": "ok",
        "count": len(recent_readings),
        "readings": recent_readings
    }), 200


@app.route("/", methods=["GET"])
def index():
    """Server status page."""
    return jsonify({
        "server": "Pico W Sensor Data Receiver",
        "status": "running",
        "host": HOST,
        "port": PORT,
        "compatible_with": "main.py (DHT22 + MQ135 + WHI)",
        "endpoints": {
            "POST /api/sensor-data": "Receive sensor data from Pico W (main endpoint)",
            "POST /upload": "Alternative endpoint (same function)",
            "GET /ping": "Health check",
            "GET /data": "View all received data",
            "GET /": "This status page"
        },
        "total_readings": len(recent_readings),
        "data_file": RAW_DUMP_FILE
    }), 200


if __name__ == "__main__":
    print("=" * 60)
    print("Pico W Sensor Data Server")
    print("Compatible with: main.py (DHT22 + MQ135 + WHI)")
    print("=" * 60)
    print(f"Data file : {RAW_DUMP_FILE}")
    print(f"Server    : http://{HOST}:{PORT}")
    print("=" * 60)
    print("Endpoints:")
    print(f"  POST http://localhost:{PORT}/api/sensor-data  - Receive data")
    print(f"  POST http://localhost:{PORT}/upload            - Receive data (alt)")
    print(f"  GET  http://localhost:{PORT}/ping              - Health check")
    print(f"  GET  http://localhost:{PORT}/data              - View data")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print("=" * 60)

    # Run server on all interfaces so Pico W can reach it
    app.run(host=HOST, port=PORT, debug=True)
