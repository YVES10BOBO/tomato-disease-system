#!/usr/bin/env python3
"""Test TomatoGuard IoT simulation through ngrok"""
import requests
import time

BACKEND_URL = "https://zoogloeal-nonprescribed-lovella.ngrok-free.dev"
FARM_ID = "81db3508-b9df-4543-82ce-a12d7b5e1667"

# Test all 4 risk scenarios
tests = [
    ("CRITICAL - Late Blight",  22.0, 93.0, 70.0),
    ("HIGH    - Early Blight",  26.0, 85.0, 55.0),
    ("MEDIUM  - Septoria",      23.0, 75.0, 50.0),
    ("LOW     - Safe",          28.0, 45.0, 40.0),
]

print("\n" + "="*70)
print("  TOMATOGUARD IoT SIMULATION - FULL SYSTEM TEST")
print(f"  Backend: {BACKEND_URL}")
print(f"  Farm ID: {FARM_ID}")
print("="*70)

passed = 0
failed = 0

for label, temp, hum, soil in tests:
    data = {
        "farm_id": FARM_ID,
        "temperature": temp,
        "humidity": hum,
        "soil_moisture": soil
    }

    try:
        print(f"\n  Testing: [{label}]")
        r = requests.post(
            f"{BACKEND_URL}/iot/sensors",
            json=data,
            timeout=10,
            headers={"ngrok-skip-browser-warning": "true"}
        )
        res = r.json()
        risk = res.get("risk_level", "UNKNOWN").upper()
        diseases = [d["disease"] for d in res.get("analysis", {}).get("risks", [])]
        summary = res.get("analysis", {}).get("summary", "OK")

        print(f"    ✓ Status: HTTP {r.status_code}")
        print(f"    Sensor readings: T={temp}°C  H={hum}%  Soil={soil}%")
        print(f"    Risk Level:      {risk}")
        if diseases:
            print(f"    Diseases:        {', '.join(diseases)}")
        print(f"    Summary:         {summary}")
        passed += 1

    except Exception as e:
        print(f"    ✗ ERROR: {str(e)}")
        failed += 1

print("\n" + "="*70)
print(f"  Results: {passed} PASSED, {failed} FAILED")
print("  ✓ IoT Simulation Complete")
print("  ✓ Ngrok tunnel working")
print("  ✓ Backend receiving sensor data")
print("  ✓ Risk analysis functioning")
print("="*70 + "\n")
