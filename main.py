from machine import Pin, ADC
import dht
import time
import json
import network
import urequests

# =====================================================
# [OUR PLACEHOLDER] WiFi + Server Config
# =====================================================
WIFI_SSID     = "Aree Gareeb"           # <-- CHANGE THIS
WIFI_PASSWORD = "12345678"       # <-- CHANGE THIS
SERVER_URL    = "http://172.27.78.169:5000/api/sensor-data" # <-- CHANGE THIS

# =====================================================
# [OUR PLACEHOLDER] Connect to WiFi
# =====================================================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi:", WIFI_SSID)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
            print(".", end="")
        print()
    print("WiFi connected! IP:", wlan.ifconfig()[0])

# =====================================================
# [OUR PLACEHOLDER] Send record to server
# =====================================================
def send_to_server(record):
    try:
        headers = {"Content-Type": "application/json"}
        response = urequests.post(SERVER_URL, data=json.dumps(record), headers=headers)
        print("Server:", response.status_code, response.text)
        response.close()
    except Exception as e:
        print("Send error:", e)

# =====================================================
# HARDWARE TEAM CODE — UNTOUCHED BELOW THIS LINE
# =====================================================

DEVICE_ID = "PICO2W_001"
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



# NH3

def ammonia_ppm(ratio):

    try:
        ppm = 116.602 * (ratio ** -2.769)

        if ppm < 0:
            ppm = 0

        return round(ppm, 2)

    except:
        return 0



# H2S

def h2s_ppm(ratio):

    try:
        ppm = 25.0 * (ratio ** -1.5)

        if ppm < 0:
            ppm = 0

        return round(ppm, 2)

    except:
        return 0



# NH3 PENALTY

def nh3_penalty(ppm):

    if ppm <= 2:
        return 0

    elif ppm <= 4:
        return 10

    elif ppm <= 6:
        return 20

    elif ppm <= 8:
        return 30

    else:
        return 40


# H2S PENALTY
def h2s_penalty(ppm):

    if ppm <= 1:
        return 0

    elif ppm <= 3:
        return 8

    elif ppm <= 5:
        return 15

    elif ppm <= 8:
        return 20

    else:
        return 25


# HUMIDITY PENALTY
def humidity_penalty(h):

    if h <= 70:
        return 0

    elif h <= 80:
        return 5

    else:
        return 10


# TEMPERATURE PENALTY
def temperature_penalty(t):

    if t <= 28:
        return 0

    elif t <= 32:
        return 10

    else:
        return 20


# TIME PENALTY
# (No degradation tracking yet)
def time_penalty():
    return 0


# CALCULATE WHI
def calculate_whi(avg_nh3,
                  avg_h2s,
                  avg_temp,
                  avg_hum):

    penalty = (
        nh3_penalty(avg_nh3)
        + h2s_penalty(avg_h2s)
        + humidity_penalty(avg_hum)
        + temperature_penalty(avg_temp)
        + time_penalty()
    )

    whi = 100 - penalty

    if whi < 0:
        whi = 0

    if whi > 100:
        whi = 100

    return whi

# TAKE ONE COMPLETE SENSOR READING

def get_sensor_reading():

    temp, hum = read_dht()

    if temp is None:
        return None

    adc, voltage, rs, ratio = read_mq135()

    nh3 = ammonia_ppm(ratio)
    h2s = h2s_ppm(ratio)

    return {
        "temperature": temp,
        "humidity": hum,
        "nh3": nh3,
        "h2s": h2s
    }



# AVERAGE TWO READINGS (30 SECONDS APART)

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

    
    # Calculate averages
    
    avg_temp = round(
        (reading1["temperature"] + reading2["temperature"]) / 2,
        2
    )

    avg_hum = round(
        (reading1["humidity"] + reading2["humidity"]) / 2,
        2
    )

    avg_nh3 = round(
        (reading1["nh3"] + reading2["nh3"]) / 2,
        2
    )

    avg_h2s = round(
        (reading1["h2s"] + reading2["h2s"]) / 2,
        2
    )

   
    # Peak NH3
    
    peak_nh3 = max(
        reading1["nh3"],
        reading2["nh3"]
    )

    
    # WHI
    
    raw_whi = calculate_whi(
        avg_nh3,
        avg_h2s,
        avg_temp,
        avg_hum
    )

    
    # Return complete result
    
    return {

        "avg_temperature_c": avg_temp,

        "avg_humidity_percent": avg_hum,

        "avg_nh3_ppm": avg_nh3,

        "peak_nh3_ppm": peak_nh3,

        "avg_h2s_ppm": avg_h2s,

        "raw_whi": raw_whi,

        "throughput": 0,

        "occupancy_inside": 0

    }

# JSON FUNCTIONS


def load_json():

    try:
        with open(JSON_FILE, "r") as file:
            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except:
        return []


def save_json(record):

    data = load_json()

    data.append(record)

    try:
        with open(JSON_FILE, "w") as file:
            json.dump(data, file)

    except Exception as e:
        print("JSON Save Error:", e)



# CREATE TELEMETRY RECORD


def create_record(avg_data):

    # Current local time
    t = time.localtime()

    timestamp = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2],
        t[3], t[4], t[5]
    )

    record = {

        "device_id": DEVICE_ID,

        "timestamp": timestamp,

        "avg_nh3_ppm": round(avg_data["avg_nh3_ppm"], 2),

        "peak_nh3_ppm": round(avg_data["peak_nh3_ppm"], 2),

        "avg_h2s_ppm": round(avg_data["avg_h2s_ppm"], 2),

        "avg_temperature_c": round(avg_data["avg_temperature_c"], 2),

        "avg_humidity_percent": round(avg_data["avg_humidity_percent"], 2),

        "raw_whi": avg_data["raw_whi"],

        # Required values
        "throughput": 0,

        "occupancy_inside": 0
    }

    return record



# SAVE ONE COMPLETE CYCLE


def process_cycle():

    avg_data = get_average_readings()

    if avg_data is None:

        print("Sensor Read Failed")

        return

    record = create_record(avg_data)

    save_json(record)

    print("\n========== FINAL DATA ==========")

    print("Timestamp :", record["timestamp"])

    print("Avg Temp  :", record["avg_temperature_c"], "°C")

    print("Avg Hum   :", record["avg_humidity_percent"], "%")

    print("Avg NH3   :", record["avg_nh3_ppm"], "ppm")

    print("Peak NH3  :", record["peak_nh3_ppm"], "ppm")

    print("Avg H2S   :", record["avg_h2s_ppm"], "ppm")

    print("WHI       :", record["raw_whi"])

    print("Throughput:", record["throughput"])

    print("Occupancy :", record["occupancy_inside"])

    print("Saved to :", JSON_FILE)

    print("===============================\n")

    # [OUR PLACEHOLDER] Send to server after JSON is fully saved
    send_to_server(record)

# STARTUP


print("========================================")
print(" Intelligent Washroom Monitoring")
print(" Raspberry Pi Pico 2 W")
print(" DHT22 + MQ135")
print("========================================")
print("Sampling Rate : 30 Seconds")
print("Publish Rate  : 60 Seconds")
print("Storage       :", JSON_FILE)
print("WHI Enabled")
print("========================================")

time.sleep(2)

# [OUR PLACEHOLDER] Connect WiFi before main loop
connect_wifi()

# MAIN LOOP


while True:

    try:

        process_cycle()

        print("Waiting for next cycle...\n")

    except KeyboardInterrupt:

        print("Program Stopped")

        break

    except Exception as e:

        print("Unexpected Error:", e)

        time.sleep(5)