import requests

BACKEND_URL = "http://localhost:8000"
FARM_ID = "81db3508-b9df-4543-82ce-a12d7b5e1667"

tests = [
    ("CRITICAL - Late Blight",  {"farm_id": FARM_ID, "temperature": 22.0, "humidity": 93.0, "soil_moisture": 70.0}),
    ("HIGH    - Early Blight",  {"farm_id": FARM_ID, "temperature": 26.0, "humidity": 85.0, "soil_moisture": 55.0}),
    ("MEDIUM  - Septoria",      {"farm_id": FARM_ID, "temperature": 23.0, "humidity": 75.0, "soil_moisture": 50.0}),
    ("LOW     - Safe",          {"farm_id": FARM_ID, "temperature": 28.0, "humidity": 45.0, "soil_moisture": 40.0}),
]

print("=" * 55)
print("  TOMATOGUARD ESP32 SIMULATION - FULL TEST")
print("  Backend: " + BACKEND_URL)
print("=" * 55)

all_ok = True
for label, data in tests:
    r = requests.post(f"{BACKEND_URL}/iot/sensors", json=data, timeout=5)
    res = r.json()
    risk = res.get("risk_level", "?").upper()
    diseases = [d["disease"] for d in res.get("analysis", {}).get("risks", [])]
    action = res.get("analysis", {}).get("risks", [{}])[0].get("action", "") if diseases else "Conditions normal"

    print(f"\n  [{label}]")
    print(f"  Sensor : T={data['temperature']}C  H={data['humidity']}%  Soil={data['soil_moisture']}%")
    print(f"  Risk   : {risk}")
    if diseases:
        print(f"  Disease: {' + '.join(diseases)}")
    print(f"  Action : {action}")

    expected = label.split("-")[0].strip().split()[0].lower()
    if expected not in risk.lower():
        print(f"  [FAIL] Expected {expected} but got {risk}")
        all_ok = False
    else:
        print(f"  [PASS]")

print("\n" + "=" * 55)
if all_ok:
    print("  ALL 4 RISK LEVELS PASSED")
    print("  ESP32 <-> Backend communication: WORKING")
else:
    print("  SOME TESTS FAILED - check thresholds")
print("=" * 55)
