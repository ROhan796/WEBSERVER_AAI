# QUICK START - Hardware Team

## Your main.py → Server

Your `main.py` already has WiFi + server sending code built in! You just need to:
1. Set your WiFi credentials
2. Set your laptop's IP address
3. Run the server on your laptop

---

## Step 1: Edit main.py on Pico W

Open `main.py` and change these lines:

```python
WIFI_SSID     = "YourActualWiFiName"      # <-- YOUR WIFI NAME
WIFI_PASSWORD = "YourActualPassword"       # <-- YOUR WIFI PASSWORD
SERVER_IP     = "192.168.1.XX"             # <-- YOUR LAPTOP IP
SERVER_PORT   = 5000                       # <-- Must match server.py PORT
SERVER_URL    = "http://{}:{}/api/sensor-data".format(SERVER_IP, SERVER_PORT)
```

**To find your laptop IP:**
- Windows: Open Command Prompt, type `ipconfig`
- Look for "IPv4 Address" under WiFi adapter (e.g., `192.168.1.105`)

---

## Step 2: Start Server on Laptop

```bash
cd C:\INTERNSHIP_TASK\TASK16\web_server
python server.py
```

You'll see:
```
============================================================
Pico W Sensor Data Server
Compatible with: main.py (DHT22 + MQ135 + WHI)
============================================================
Data file : raw_dump.jsonl
Server    : http://0.0.0.0:5000
============================================================
```

**Keep this window open!**

---

## Step 3: Run main.py on Pico W

1. Connect Pico W via USB
2. Open Thonny IDE
3. Open your `main.py`
4. Click Run (green button)

You'll see:
```
========================================
 Intelligent Washroom Monitoring
 Raspberry Pi Pico 2 W
 DHT22 + MQ135
========================================
Connecting to WiFi: YourWiFiName
WiFi connected! IP: 192.168.1.110
------------------------------------
Reading 1...
Temperature : 28.5
Humidity    : 65.0
NH3         : 5.5
H2S         : 2.1
------------------------------------
```

---

## What You'll See

**In Server window (laptop):**
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

**Data is saved to:** `raw_dump.jsonl`

---

## Data Format (What main.py Sends)

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

---

## Troubleshooting

**"WiFi connection timeout"**
- Check WiFi name and password (case-sensitive)
- Make sure you're on 2.4GHz WiFi

**"Send error"**
- Make sure `python server.py` is running on laptop
- Check the IP address is correct
- Both devices must be on same WiFi

**"Sensor Read Failed"**
- Check wiring (DHT22 on Pin 15, MQ135 on GP26)
- Make sure sensors have power (3.3V)

---

## Your main.py is Already Ready!

Your `main.py` already has:
- WiFi connection code
- Server sending code
- WHI calculation
- All sensor reading logic

You just need to configure WiFi + server IP!
