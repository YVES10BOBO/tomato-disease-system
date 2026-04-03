"""
IoT Simulator — Mimics ESP32 sending sensor data to backend
Simulates real farm conditions including disease-favorable weather
"""

import requests
import time
import random
import json
from datetime import datetime
from config import BACKEND_URL, FARM_ID, SEND_INTERVAL_SECONDS

# ─── FARM SCENARIOS ─────────────────────────────────────────
SCENARIOS = {
    "normal": {
        "description": "Normal farm conditions — no disease risk",
        "temp_range": (20, 26),
        "humidity_range": (50, 70),
        "soil_range": (35, 55)
    },
    "early_blight_risk": {
        "description": "Early Blight risk — warm + humid",
        "temp_range": (24, 29),
        "humidity_range": (80, 89),
        "soil_range": (40, 60)
    },
    "late_blight_risk": {
        "description": "Late Blight risk — cool + very humid",
        "temp_range": (10, 24),
        "humidity_range": (90, 98),
        "soil_range": (50, 70)
    },
    "bacterial_wilt_risk": {
        "description": "Bacterial Wilt risk — hot + waterlogged soil",
        "temp_range": (28, 35),
        "humidity_range": (65, 80),
        "soil_range": (80, 95)
    },
    "night_mode": {
        "description": "Night conditions — cooler + stable",
        "temp_range": (15, 19),
        "humidity_range": (60, 75),
        "soil_range": (30, 50)
    }
}


def get_sensor_reading(scenario_name: str) -> dict:
    """Generate realistic sensor readings based on scenario"""
    scenario = SCENARIOS[scenario_name]

    temp = round(random.uniform(*scenario["temp_range"]), 1)
    humidity = round(random.uniform(*scenario["humidity_range"]), 1)
    soil = round(random.uniform(*scenario["soil_range"]), 1)

    # Add small random variation to make it realistic
    temp += round(random.uniform(-0.5, 0.5), 1)
    humidity += round(random.uniform(-2, 2), 1)

    return {
        "farm_id": FARM_ID,
        "temperature": temp,
        "humidity": humidity,
        "soil_moisture": soil
    }


def send_sensor_data(reading: dict) -> dict:
    """Send sensor reading to FastAPI backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/iot/sensors",
            json=reading,
            timeout=5
        )
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is it running?"}
    except Exception as e:
        return {"error": str(e)}


def print_status(reading: dict, result: dict, scenario: str):
    """Print formatted status to terminal"""
    now = datetime.now().strftime("%H:%M:%S")
    risk = result.get("risk_level", "unknown")

    risk_colors = {
        "low": "\033[92m",       # Green
        "medium": "\033[93m",    # Yellow
        "high": "\033[91m",      # Red
        "critical": "\033[95m",  # Magenta
    }
    reset = "\033[0m"
    color = risk_colors.get(risk, "")

    print(f"\n[{now}] Scenario: {scenario.upper()}")
    print(f"  Temp: {reading['temperature']}C | Humidity: {reading['humidity']}% | Soil: {reading['soil_moisture']}%")
    print(f"  Risk Level: {color}{risk.upper()}{reset}")

    if result.get("analysis", {}).get("risks"):
        for r in result["analysis"]["risks"]:
            print(f"  WARNING: {r['disease']} detected risk!")
            print(f"  Action: {r['action']}")
    else:
        print(f"  Status: {result.get('analysis', {}).get('summary', 'OK')}")


def run_demo_cycle():
    """Run through all scenarios automatically for demo purposes"""
    print("\n" + "="*55)
    print("  TOMATO FARM IoT SIMULATOR")
    print("  Simulating ESP32 sensor node")
    print(f"  Backend: {BACKEND_URL}")
    print(f"  Farm ID: {FARM_ID}")
    print(f"  Interval: {SEND_INTERVAL_SECONDS}s")
    print("="*55)
    print("\nPress Ctrl+C to stop\n")

    scenario_list = list(SCENARIOS.keys())
    index = 0
    reading_count = 0

    while True:
        scenario_name = scenario_list[index % len(scenario_list)]
        reading = get_sensor_reading(scenario_name)
        result = send_sensor_data(reading)
        reading_count += 1

        print_status(reading, result, scenario_name)
        print(f"  Total readings sent: {reading_count}")

        index += 1
        time.sleep(SEND_INTERVAL_SECONDS)


def run_single_scenario(scenario_name: str, count: int = 5):
    """Run a specific scenario multiple times"""
    if scenario_name not in SCENARIOS:
        print(f"Unknown scenario. Choose from: {list(SCENARIOS.keys())}")
        return

    print(f"\nRunning scenario: {scenario_name}")
    print(f"Description: {SCENARIOS[scenario_name]['description']}\n")

    for i in range(count):
        reading = get_sensor_reading(scenario_name)
        result = send_sensor_data(reading)
        print_status(reading, result, scenario_name)
        if i < count - 1:
            time.sleep(2)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        scenario = sys.argv[1]
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        run_single_scenario(scenario, count)
    else:
        run_demo_cycle()
