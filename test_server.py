"""
test_server.py - Test the Flask server without Pico W

This script sends fake sensor data to your server to verify everything
works before connecting the actual Pico W.

Compatible with main.py from hardware team:
- DHT22 temperature/humidity sensor on Pin 15
- MQ135 air quality sensor on GP26
- WHI (Waste Health Index) calculation with penalty breakdown

Usage:
    1. Start the server: python server.py
    2. Run this test: python test_server.py

Configuration:
    Edit PORT below to match your server.py PORT setting.
"""

import requests
import json
import time
from datetime import datetime

# Server Configuration (must match server.py)
HOST = "localhost"
PORT = 5000
SERVER_URL = f"http://{HOST}:{PORT}"


def test_ping():
    """Test the /ping endpoint."""
    print("Testing /ping endpoint...")
    try:
        response = requests.get(f"{SERVER_URL}/ping", timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def test_upload():
    """Test the /api/sensor-data endpoint with fake sensor data."""
    print("\nTesting /api/sensor-data endpoint...")
    
    # Create fake sensor data (matches main.py create_record() output)
    fake_data = {
        "device_id": "PICO2W_001",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
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
    
    print(f"  Sending: {json.dumps(fake_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{SERVER_URL}/api/sensor-data",
            json=fake_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def test_upload_alt():
    """Test the /upload endpoint (backward compatibility)."""
    print("\nTesting /upload endpoint (backward compatibility)...")
    
    fake_data = {
        "device_id": "PICO2W_001",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        "avg_nh3_ppm": 4.0,
        "peak_nh3_ppm": 5.0,
        "avg_h2s_ppm": 1.5,
        "avg_temperature_c": 27.0,
        "avg_humidity_percent": 60.0,
        "raw_whi": 90,
        "penalty_nh3": 10,
        "penalty_h2s": 0,
        "penalty_temperature": 0,
        "penalty_humidity": 0,
        "throughput": 0,
        "occupancy_inside": 0
    }
    
    try:
        response = requests.post(
            f"{SERVER_URL}/upload",
            json=fake_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def test_get_data():
    """Test the /data endpoint."""
    print("\nTesting /data endpoint...")
    try:
        response = requests.get(f"{SERVER_URL}/data", timeout=5)
        print(f"  Status: {response.status_code}")
        data = response.json()
        print(f"  Readings count: {data.get('count', 0)}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def test_status():
    """Test the / (root) endpoint."""
    print("\nTesting / (status) endpoint...")
    try:
        response = requests.get(f"{SERVER_URL}/", timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Pico W Server Test Script")
    print("Compatible with: main.py (DHT22 + MQ135 + WHI)")
    print("=" * 60)
    print(f"Server URL: {SERVER_URL}")
    print(f"Port: {PORT}")
    print("Make sure the server is running first!")
    print("Start it with: python server.py")
    print("=" * 60)
    
    # Run tests
    results = []
    results.append(("Ping", test_ping()))
    results.append(("Upload (/api/sensor-data)", test_upload()))
    results.append(("Upload (/upload)", test_upload_alt()))
    results.append(("Get Data", test_get_data()))
    results.append(("Status", test_status()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("All tests passed! Server is working correctly.")
        print("\nNext steps:")
        print("1. Keep the server running")
        print("2. Update SERVER_URL in main.py on Pico W")
        print("3. main.py will send data to this server")
    else:
        print("Some tests failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure server.py is running")
        print("2. Check if port", PORT, "is not blocked by firewall")
        print(f"3. Try running: curl http://localhost:{PORT}/ping")
    print("=" * 60)


if __name__ == "__main__":
    main()
