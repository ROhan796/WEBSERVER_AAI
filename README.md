# Web Server - Complete Documentation

## Compatible With

This server is designed to work with `main.py` from the hardware team:
- **Sensors:** DHT22 (Pin 15) + MQ135 (GP26)
- **Features:** WHI calculation, dual readings, averaging
- **Device ID:** PICO2W_001

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [File Documentation](#file-documentation)
- [API Reference](#api-reference)
- [Data Format](#data-format)
- [Hardware Setup](#hardware-setup)
- [Troubleshooting](#troubleshooting)

---

## Overview

```
┌─────────────────────┐         ┌─────────────────────┐
│     PICO W          │  WiFi   │     LAPTOP          │
│   (main.py)         │ ──────> │   (server.py)       │
│                     │         │                     │
│  DHT22 (Pin 15)     │         │  Receives JSON      │
│  MQ135 (GP26)       │         │  Saves to file      │
│  WHI Calculation    │         │  Shows on screen    │
└─────────────────────┘         └─────────────────────┘
```

**How it works:**
1. Pico W reads sensors (DHT22 + MQ135)
2. Calculates NH3, H2S, WHI values
3. Sends JSON data to laptop via WiFi
4. Server saves data to `raw_dump.jsonl`

---

## Quick Start

### 1. Edit main.py on Pico W

```python
# Line 11-13 in main.py
WIFI_SSID     = "YourWiFiName"
WIFI_PASSWORD = "YourPassword"
SERVER_URL    = "http://YOUR_LAPTOP_IP:5000/api/sensor-data"
```

### 2. Start Server on Laptop

```bash
cd C:\INTERNSHIP_TASK\TASK16\web_server
python server.py
```

### 3. Run main.py on Pico W

Data will start appearing in the server window!

---

## File Documentation

### server.py - Flask Web Server

**Path:** `C:\INTERNSHIP_TASK\TASK16\web_server\server.py`

**Purpose:** Receives sensor data from Pico W and saves to file

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sensor-data` | Main endpoint (used by main.py) |
| POST | `/upload` | Alternative endpoint (same function) |
| GET | `/ping` | Health check |
| GET | `/data` | View all received readings |
| GET | `/` | Server status |

**Key Functions:**

```python
@app.route("/api/sensor-data", methods=["POST"])
def receive_data():
    # Receives JSON from main.py
    # Saves to raw_dump.jsonl
    # Shows on screen
```

**Output Format (on screen):**
```
==================================================
RECEIVED FROM: PICO2W_001
==================================================
Timestamp    : 2026-07-01T12:30:00
Avg Temp     : 28.5 C
Avg Humidity : 65.0 %
Avg NH3      : 5.5 ppm
Peak NH3     : 6.2 ppm
Avg H2S      : 2.1 ppm
WHI          : 85
==================================================
```

---

### main.py - Pico W Script (Hardware Team's Code)

**Path:** Your existing `main.py` on Pico W

**What it does:**

1. **Connects to WiFi**
2. **Reads sensors:**
   - DHT22 on Pin 15 (temperature, humidity)
   - MQ135 on GP26 (air quality)
3. **Calculates values:**
   - NH3 ppm (ammonia)
   - H2S ppm (hydrogen sulfide)
   - WHI (Waste Health Index)
4. **Takes two readings** (30 seconds apart)
5. **Averages them**
6. **Sends to server** via HTTP POST

**Data sent to server:**
```json
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
```

**Key functions in main.py:**

| Function | Purpose |
|----------|---------|
| `connect_wifi()` | Connects Pico W to WiFi |
| `send_to_server(record)` | Sends JSON to laptop server |
| `read_dht()` | Reads DHT22 sensor |
| `read_mq135()` | Reads MQ135 sensor |
| `ammonia_ppm(ratio)` | Calculates NH3 from MQ135 |
| `h2s_ppm(ratio)` | Calculates H2S from MQ135 |
| `calculate_whi()` | Calculates WHI score |
| `get_average_readings()` | Takes 2 readings, 30s apart |
| `create_record(avg_data)` | Creates JSON record |
| `process_cycle()` | Main cycle - reads, calculates, sends |

---

### test_server.py - Test Script

**Path:** `C:\INTERNSHIP_TASK\TASK16\web_server\test_server.py`

**Purpose:** Test server without Pico W hardware

**Usage:**
```bash
# Start server first, then:
python test_server.py
```

**Tests performed:**
1. Ping test (health check)
2. Upload test to `/api/sensor-data`
3. Upload test to `/upload` (backward compatibility)
4. Get data test
5. Status test

---

### raw_dump.jsonl - Data File

**Path:** `C:\INTERNSHIP_TASK\TASK16\web_server\raw_dump.jsonl`

**Created:** Automatically when data is received

**Format:** One JSON object per line

**Example:**
```json
{"device_id":"PICO2W_001","timestamp":"2026-07-01T12:30:00","avg_nh3_ppm":5.5,"peak_nh3_ppm":6.2,"avg_h2s_ppm":2.1,"avg_temperature_c":28.5,"avg_humidity_percent":65.0,"raw_whi":85,"throughput":0,"occupancy_inside":0,"_received_at":"2026-07-01T12:30:05"}
```

---

## API Reference

### POST /api/sensor-data

**Purpose:** Receive sensor data from Pico W

**Request Body:**
```json
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
```

**Response (200 OK):**
```json
{
    "status": "ok",
    "message": "Data received successfully"
}
```

---

### GET /ping

**Purpose:** Health check

**Response:**
```json
{
    "status": "ok",
    "message": "Server is running",
    "timestamp": "2026-07-01T12:30:00",
    "readings_count": 15
}
```

---

### GET /data

**Purpose:** View all received readings

**Response:**
```json
{
    "status": "ok",
    "count": 15,
    "readings": [...]
}
```

---

## Data Format

### Fields Sent by main.py

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `device_id` | string | Device identifier | "PICO2W_001" |
| `timestamp` | string | ISO 8601 timestamp | "2026-07-01T12:30:00" |
| `avg_nh3_ppm` | float | Average NH3 (ammonia) | 5.5 |
| `peak_nh3_ppm` | float | Peak NH3 reading | 6.2 |
| `avg_h2s_ppm` | float | Average H2S (hydrogen sulfide) | 2.1 |
| `avg_temperature_c` | float | Average temperature (Celsius) | 28.5 |
| `avg_humidity_percent` | float | Average humidity (%) | 65.0 |
| `raw_whi` | integer | Waste Health Index (0-100) | 85 |
| `throughput` | integer | Throughput (currently 0) | 0 |
| `occupancy_inside` | integer | Occupancy count (currently 0) | 0 |

### WHI Score Interpretation

| WHI Range | Status | Action |
|-----------|--------|--------|
| 90-100 | Excellent | No action |
| 75-89 | Good | Monitor |
| 50-74 | Warning | Cleaning scheduled |
| 25-49 | Poor | Cleaning team dispatched |
| 0-24 | Critical | Immediate escalation |

---

## Hardware Setup

### Pin Connections

```
Raspberry Pi Pico W:
┌─────────────────────────────────────────┐
│           RASPBERRY PI PICO W           │
│                                         │
│  3V3  (Pin 36) ──────── VCC (sensors)   │
│  GND  (Pin 38) ──────── GND (sensors)   │
│  GP26 (Pin 31) ──────── MQ135 ADC       │
│  Pin15 (Pin 20) ──────── DHT22 Data     │
│                                         │
└─────────────────────────────────────────┘
```

### Sensors

| Sensor | Pin | Purpose |
|--------|-----|---------|
| DHT22 | Pin 15 | Temperature + Humidity |
| MQ135 | GP26 | Air quality (NH3, H2S) |

---

## Troubleshooting

### Server not receiving data

1. **Check server is running:**
   ```bash
   curl http://localhost:5000/ping
   ```

2. **Check main.py SERVER_URL:**
   ```python
   SERVER_URL = "http://CORRECT_IP:5000/api/sensor-data"
   ```

3. **Check both devices on same WiFi**

4. **Check firewall** - allow Python through Windows Firewall

### Sensor errors

- Check wiring matches your original setup
- DHT22 on Pin 15, MQ135 on GP26
- Make sure sensors have power (3.3V)

### WiFi connection fails

- Make sure you're on 2.4GHz WiFi (not 5GHz)
- Check WiFi name and password (case-sensitive)

---

## Testing

### Test 1: Server Health Check

```bash
curl http://localhost:5000/ping
```

### Test 2: Manual Data Upload

```bash
curl -X POST http://localhost:5000/api/sensor-data -H "Content-Type: application/json" -d '{"device_id":"PICO2W_001","timestamp":"2026-07-01T12:30:00","avg_nh3_ppm":5.5,"peak_nh3_ppm":6.2,"avg_h2s_ppm":2.1,"avg_temperature_c":28.5,"avg_humidity_percent":65.0,"raw_whi":85,"throughput":0,"occupancy_inside":0}'
```

### Test 3: Automated Test

```bash
python test_server.py
```

---

## Files in This Folder

| File | Purpose |
|------|---------|
| `server.py` | Flask server (run on laptop) |
| `test_server.py` | Test script |
| `main.py` | Your Pico W script (hardware team's code) |
| `QUICK_START.md` | Simple getting started guide |
| `README.md` | This documentation |
| `requirements.txt` | Python packages needed |
| `setup.bat` | Windows setup script |
| `raw_dump.jsonl` | Data file (auto-created) |

---

**Last Updated:** July 2026
**Compatible with:** main.py (DHT22 + MQ135 + WHI)
#   W E B S E R V E R _ A A I  
 #   W E B S E R V E R _ A A I  
 