from machine import Pin, ADC, RTC
import dht
import time
import json
import network
import urequests
import machine
import ntptime
import gc

# =====================================================
# [OUR PLACEHOLDER] WiFi + Server Config
# =====================================================
WIFI_SSID     = "Aree Gareeb"         # <-- CHANGE THIS
WIFI_PASSWORD = "12345678"            # <-- CHANGE THIS
SERVER_IP     = "172.27.78.169"       # <-- CHANGE THIS (laptop IP)
SERVER_PORT   = 8000                  # <-- Change in one place, update server.py PORT too
SERVER_URL    = "http://{}:{}/api/sensor-data".format(SERVER_IP, SERVER_PORT)

# =====================================================
# [OUR PLACEHOLDER] Connect to WiFi & Sync to IST
# =====================================================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi:", WIFI_SSID)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        retries = 30
        while not wlan.isconnected() and retries > 0:
            time.sleep(0.5)
            print(".", end="")
            retries -= 1
        print()

    if wlan.isconnected():
        print("WiFi connected! IP:", wlan.ifconfig()[0])
        try:
            print("Syncing time with NTP server...")
            ntptime.settime()

            IST_OFFSET = (5 * 3600) + (30 * 60)
            ist_seconds = time.time() + IST_OFFSET
            tm = time.localtime(ist_seconds)

            RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))

            print("Time successfully calibrated to IST!")
        except Exception as e:
            print("NTP Time Sync Failed:", e)
    else:
        print("Failed to connect to WiFi. Proceeding offline...")

# =====================================================
# [OUR PLACEHOLDER] Send record to server
# =====================================================
def send_to_server(record):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("Offline: Cannot send data to server.")
        return

    try:
        headers = {"Content-Type": "application/json"}
        response = urequests.post(SERVER_URL, data=json.dumps(record), headers=headers)
        print("Server Response:", response.status_code, response.text)
        response.close()
    except Exception as e:
        print("Send error:", e)

# =====================================================
# HARDWARE TEAM CODE — UNTOUCHED BELOW THIS LINE
# =====================================================

raw_id = machine.unique_id()
DEVICE_ID = "PICO2W_" + "".join("{:02x}".format(b) for b in raw_id).upper()

JSON_FILE = "sensor_data.json"
dht_sensor = dht.DHT22(Pin(15))
mq135 = ADC(26)

VCC = 3.3
RL = 10.0
R0 = 3.6

# DHT22 READ
def read_dht():
    for _ in range(5):
        try:
            dht_sensor.measure()
            t = dht_sensor.temperature()
            h = dht_sensor.humidity()
            if -40 <= t <= 80 and 0 <= h <= 100:
                return t, h
        except:
            pass
        time.sleep(2)
    return None, None

# MQ135 READ
def read_mq135(samples=20):
    total = 0
    for _ in range(samples):
        total += mq135.read_u16()
        time.sleep_ms(50)
    adc = total / samples
    voltage = (adc / 65535) * VCC
    if voltage < 0.01:
        voltage = 0.01
    rs = ((VCC - voltage) * RL) / voltage
    ratio = rs / R0
    return adc, voltage, rs, ratio

# Gas Formulations
def ammonia_ppm(ratio):
    try:
        ppm = 116.602 * (ratio ** -2.769)
        return round(max(0, ppm), 2)
    except:
        return 0

def h2s_ppm(ratio):
    try:
        ppm = 25.0 * (ratio ** -1.5)
        return round(max(0, ppm), 2)
    except:
        return 0

# Penalty Mappings
def nh3_penalty(ppm):
    if ppm <= 2: return 0
    elif ppm <= 4: return 10
    elif ppm <= 6: return 20
    elif ppm <= 8: return 30
    return 40

def h2s_penalty(ppm):
    if ppm <= 1: return 0
    elif ppm <= 3: return 8
    elif ppm <= 5: return 15
    elif ppm <= 8: return 20
    return 25

def humidity_penalty(h):
    if h <= 70: return 0
    elif h <= 80: return 5
    return 10

def temperature_penalty(t):
    if t <= 28: return 0
    elif t <= 32: return 10
    return 20

def calculate_whi_breakdown(avg_nh3, avg_h2s, avg_temp, avg_hum):
    p_nh3 = nh3_penalty(avg_nh3)
    p_h2s = h2s_penalty(avg_h2s)
    p_hum = humidity_penalty(avg_hum)
    p_temp = temperature_penalty(avg_temp)

    penalty = p_nh3 + p_h2s + p_hum + p_temp
    whi = max(0, min(100, 100 - penalty))

    return whi, p_nh3, p_h2s, p_temp, p_hum

def get_sensor_reading():
    temp, hum = read_dht()
    if temp is None:
        return None
    adc, voltage, rs, ratio = read_mq135()
    nh3 = ammonia_ppm(ratio)
    h2s = h2s_ppm(ratio)
    return {"temperature": temp, "humidity": hum, "nh3": nh3, "h2s": h2s}

def get_average_readings():
    print("------------------------------------")
    print("Reading 1...")
    print("------------------------------------")
    reading1 = get_sensor_reading()
    if reading1 is None:
        print("Reading 1 Failed")
        return None

    print("Temperature :", reading1["temperature"])
    print("Humidity    :", reading1["humidity"])
    print("NH3         :", reading1["nh3"])
    print("H2S         :", reading1["h2s"])

    print("\nWaiting 30 seconds...\n")
    time.sleep(30)

    print("------------------------------------")
    print("Reading 2...")
    print("------------------------------------")
    reading2 = get_sensor_reading()
    if reading2 is None:
        print("Reading 2 Failed")
        return None

    print("Temperature :", reading2["temperature"])
    print("Humidity    :", reading2["humidity"])
    print("NH3         :", reading2["nh3"])
    print("H2S         :", reading2["h2s"])

    avg_temp = round((reading1["temperature"] + reading2["temperature"]) / 2, 2)
    avg_hum = round((reading1["humidity"] + reading2["humidity"]) / 2, 2)
    avg_nh3 = round((reading1["nh3"] + reading2["nh3"]) / 2, 2)
    avg_h2s = round((reading1["h2s"] + reading2["h2s"]) / 2, 2)
    peak_nh3 = max(reading1["nh3"], reading2["nh3"])

    raw_whi, p_nh3, p_h2s, p_temp, p_hum = calculate_whi_breakdown(avg_nh3, avg_h2s, avg_temp, avg_hum)

    return {
        "avg_temperature_c": avg_temp,
        "avg_humidity_percent": avg_hum,
        "avg_nh3_ppm": avg_nh3,
        "peak_nh3_ppm": peak_nh3,
        "avg_h2s_ppm": avg_h2s,
        "raw_whi": raw_whi,
        "penalty_nh3": p_nh3,
        "penalty_h2s": p_h2s,
        "penalty_temperature": p_temp,
        "penalty_humidity": p_hum,
        "throughput": 0,
        "occupancy_inside": 0
    }

def save_json(record):
    try:
        with open(JSON_FILE, "w") as file:
            json.dump(record, file)
    except Exception as e:
        print("JSON Save Error:", e)

def create_record(avg_data):
    t = time.localtime()
    timestamp = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4], t[5])

    return {
        "device_id": DEVICE_ID,
        "timestamp": timestamp,
        "avg_nh3_ppm": round(avg_data["avg_nh3_ppm"], 2),
        "peak_nh3_ppm": round(avg_data["peak_nh3_ppm"], 2),
        "avg_h2s_ppm": round(avg_data["avg_h2s_ppm"], 2),
        "avg_temperature_c": round(avg_data["avg_temperature_c"], 2),
        "avg_humidity_percent": round(avg_data["avg_humidity_percent"], 2),
        "raw_whi": avg_data["raw_whi"],
        "penalty_nh3": avg_data["penalty_nh3"],
        "penalty_h2s": avg_data["penalty_h2s"],
        "penalty_temperature": avg_data["penalty_temperature"],
        "penalty_humidity": avg_data["penalty_humidity"],
        "throughput": 0,
        "occupancy_inside": 0
    }

def process_cycle():
    avg_data = get_average_readings()
    if avg_data is None:
        print("Sensor Read Failed")
        return

    record = create_record(avg_data)
    save_json(record)

    print("\n========== FINAL DATA (IST) ==========")
    print("Device ID :", record["device_id"])
    print("Timestamp :", record["timestamp"])
    print("Avg Temp  :", record["avg_temperature_c"], "C")
    print("Avg Hum   :", record["avg_humidity_percent"], "%")
    print("Avg NH3   :", record["avg_nh3_ppm"], "ppm")
    print("WHI       :", record["raw_whi"])
    print("======================================\n")

    send_to_server(record)

# STARTUP
print("========================================")
print(" Intelligent Washroom Monitoring")
print(" Raspberry Pi Pico 2 W")
print(" Unique ID    :", DEVICE_ID)
print("========================================")

time.sleep(2)
connect_wifi()

# MAIN LOOP
while True:
    try:
        process_cycle()
        print("Waiting 30 seconds for next cycle...\n")
        time.sleep(30)
        gc.collect()
    except KeyboardInterrupt:
        print("Program Stopped")
        break
    except Exception as e:
        print("Unexpected Error:", e)
        time.sleep(5)
