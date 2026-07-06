"""
server.py - Flask web server that runs on your laptop

This server receives sensor data from Pico W devices on your LAN.
The Pico W acts as a client and POSTs data to this server.

Compatible with main.py from hardware team:
- DHT22 temperature/humidity sensor on Pin 15
- MQ135 air quality sensor on GP26
- WHI (Waste Health Index) calculation

Usage:
    python server.py

Endpoints:
    POST /api/sensor-data  - Receive sensor data from Pico W
    GET  /ping             - Health check
    GET  /data             - View all received data
    GET  /                 - Server status page
"""

from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

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
    print(f"Data file: {RAW_DUMP_FILE}")
    print("Endpoints:")
    print("  POST http://localhost:5000/api/sensor-data  - Receive data")
    print("  POST http://localhost:5000/upload            - Receive data (alt)")
    print("  GET  http://localhost:5000/ping              - Health check")
    print("  GET  http://localhost:5000/data              - View data")
    print("=" * 60)
    print("Starting server on http://0.0.0.0:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Run server on all interfaces (0.0.0.0) so Pico W can reach it
    app.run(host="0.0.0.0", port=5000, debug=True)
