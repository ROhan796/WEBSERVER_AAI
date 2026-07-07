# Web Server - Complete Documentation

## Compatible With

This server is designed to work with `main.py` from the hardware team:
- **Sensors:** DHT22 (Pin 15) + MQ135 (GP26)
- **Features:** WHI calculation with penalty breakdown, dual readings, averaging
- **Device ID:** Auto-generated from Pico W unique ID

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [File Documentation](#file-documentation)
- [API Reference](#api-reference)
- [Data Format](#data-format)
- [Hardware Setup](#hardware-setup)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing)

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
2. Calculates NH3, H2S, WHI values with penalty breakdown
3. Sends JSON data to laptop via WiFi
4. Server saves data to `raw_dump.jsonl`

---

## Quick Start

### 1. Edit main.py on Pico W

```python
# Configuration section in main.py
WIFI_SSID     = "YourWiFiName"
WIFI_PASSWORD = "YourPassword"
SERVER_IP     = "YOUR_LAPTOP_IP"      # e.g., "192.168.1.105"
SERVER_PORT   = 5000                   # Must match server.py PORT
SERVER_URL    = "http://{}:{}/api/sensor-data".format(SERVER_IP, SERVER_PORT)
```

**To find your laptop IP:**
- Windows: Open Command Prompt, type `ipconfig`
- Look for "IPv4 Address" under WiFi adapter (e.g., `192.168.1.105`)

### 2. Start Server on Laptop

```bash
cd C:\INTERNSHIP_TASK\TASK16\web_server
python server.py
```

### 3. Run main.py on Pico W

Data will start appearing in the server window!

---

## Configuration

### Port Configuration (Change in One Place)

Both `server.py` and `main.py` use a PORT variable. To change the port:

1. **server.py** - Change `PORT = 5000` to your desired port
2. **main.py** - Change `SERVER_PORT = 5000` to match

This avoids hardcoding the port in multiple places.

```python
# server.py
HOST = "0.0.0.0"
PORT = 5000

# main.py
SERVER_IP     = "YOUR_LAPTOP_IP"
SERVER_PORT   = 5000
SERVER_URL    = "http://{}:{}/api/sensor-data".format(SERVER_IP, SERVER_PORT)
```

---

## File Documentation

### server.py - Flask Web Server

**Path:** `C:\INTERNSHIP_TASK\TASK16\web_server\server.py`

**Purpose:** Receives sensor data from Pico W and saves to file

**Configuration Variables:**
```python
HOST = "0.0.0.0"    # Listen on all interfaces
PORT = 5000          # Change here, update main.py SERVER_PORT too
```

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sensor-data` | Main endpoint (used by main.py) |
| POST | `/upload` | Alternative endpoint (backward compat) |
| GET | `/ping` | Health check |
| GET | `/data` | View all received readings |
| GET | `/` | Server status |

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
Penalty NH3  : 10
Penalty H2S  : 8
Penalty Temp : 0
Penalty Hum  : 5
Throughput   : 0
Occupancy    : 0
Received at  : 2026-07-01T12:30:05
==================================================
```

---

### main.py - Pico W Script

**Path:** Your `main.py` on Pico W

**Configuration Variables:**
```python
WIFI_SSID     = "YourWiFiName"
WIFI_PASSWORD = "YourPassword"
SERVER_IP     = "YOUR_LAPTOP_IP"
SERVER_PORT   = 5000
SERVER_URL    = "http://{}:{}/api/sensor-data".format(SERVER_IP, SERVER_PORT)
```

**Key functions in main.py:**

| Function | Purpose |
|----------|---------|
| `connect_wifi()` | Connects Pico W to WiFi + NTP time sync |
| `send_to_server(record)` | Sends JSON to laptop server |
| `read_dht()` | Reads DHT22 sensor |
| `read_mq135()` | Reads MQ135 sensor |
| `ammonia_ppm(ratio)` | Calculates NH3 from MQ135 |
| `h2s_ppm(ratio)` | Calculates H2S from MQ135 |
| `calculate_whi_breakdown()` | Calculates WHI with penalty breakdown |
| `get_average_readings()` | Takes 2 readings, 30s apart |
| `create_record(avg_data)` | Creates JSON record |
| `process_cycle()` | Main cycle - reads, calculates, sends |

---

### test_server.py - Test Script

**Path:** `C:\INTERNSHIP_TASK\TASK16\web_server\test_server.py`

**Purpose:** Test server without Pico W hardware

**Configuration Variables:**
```python
HOST = "localhost"
PORT = 5000         # Must match server.py PORT
```

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
    "penalty_nh3": 10,
    "penalty_h2s": 8,
    "penalty_temperature": 0,
    "penalty_humidity": 5,
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
| `device_id` | string | Device identifier (auto-generated) | "PICO2W_AABBCCDD" |
| `timestamp` | string | ISO 8601 timestamp (IST) | "2026-07-01T12:30:00" |
| `avg_nh3_ppm` | float | Average NH3 (ammonia) | 5.5 |
| `peak_nh3_ppm` | float | Peak NH3 reading | 6.2 |
| `avg_h2s_ppm` | float | Average H2S (hydrogen sulfide) | 2.1 |
| `avg_temperature_c` | float | Average temperature (Celsius) | 28.5 |
| `avg_humidity_percent` | float | Average humidity (%) | 65.0 |
| `raw_whi` | integer | Waste Health Index (0-100) | 85 |
| `penalty_nh3` | integer | NH3 penalty score | 10 |
| `penalty_h2s` | integer | H2S penalty score | 8 |
| `penalty_temperature` | integer | Temperature penalty score | 0 |
| `penalty_humidity` | integer | Humidity penalty score | 5 |
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
   SERVER_IP     = "CORRECT_IP"
   SERVER_PORT   = 5000
   SERVER_URL    = "http://{}:{}/api/sensor-data".format(SERVER_IP, SERVER_PORT)
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
curl -X POST http://localhost:5000/api/sensor-data -H "Content-Type: application/json" -d '{"device_id":"PICO2W_001","timestamp":"2026-07-01T12:30:00","avg_nh3_ppm":5.5,"peak_nh3_ppm":6.2,"avg_h2s_ppm":2.1,"avg_temperature_c":28.5,"avg_humidity_percent":65.0,"raw_whi":85,"penalty_nh3":10,"penalty_h2s":8,"penalty_temperature":0,"penalty_humidity":5,"throughput":0,"occupancy_inside":0}'
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
| `test_server.py` | Test script (no hardware needed) |
| `main.py` | Pico W script (reference copy) |
| `QUICK_START.md` | Simple getting started guide |
| `README.md` | This documentation |
| `requirements.txt` | Python packages needed |
| `raw_dump.jsonl` | Data file (auto-created) |

---

**Last Updated:** July 2026
**Compatible with:** main.py (DHT22 + MQ135 + WHI)
