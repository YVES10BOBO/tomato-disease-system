# TomatoGuard ESP32-CAM Setup Guide

## 📋 What Changed from Previous Code

### ✅ Removed
- Bearer token authentication headers
- `Authorization: Bearer` logic
- Token validation in requests
- All auth-related imports

### ✅ Added
- Simplified HTTP headers (Content-Type only)
- Dual sensor operation: Temperature/Humidity + Soil Moisture
- Web dashboard on port 80 for real-time monitoring
- Auto-capture every 60 seconds
- Auto-sensor-read every 10 seconds
- Risk level alerts with LED/Buzzer feedback
- Disease detection with automatic alerts

---

## 🔧 Configuration (IMPORTANT!)

Edit these values in `tomato_guard_final.ino`:

```cpp
// Line 21-22: WiFi
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// Line 25: Backend URL (update your ngrok)
const char* BACKEND_URL = "https://zoogloeal-nonprescribed-lovella.ngrok-free.dev";

// Line 28-29: Farm Details
const char* FARM_ID = "81db3508-b9df-4543-82ce-a12d7b5e1667";
const char* ZONE_CODE = "A1";  // Change to your zone (A1-D4)
```

---

## 📌 Hardware Pinouts (for AI-THINKER ESP32-CAM)

| Component | GPIO Pin | Notes |
|-----------|----------|-------|
| DHT11 (Temp/Humidity) | GPIO 14 | Data pin |
| Soil Moisture Sensor | GPIO 33 | Analog input (ADC) |
| Green LED (Status) | GPIO 12 | High = Healthy |
| Red LED (Status) | GPIO 13 | High = Warning |
| Buzzer | GPIO 18 | For alerts |

**Camera pins**: Configured automatically for AI-THINKER model (lines 46-60)

---

## 🚀 Installation

### Step 1: Install Libraries
In Arduino IDE → Sketch → Include Library → Manage Libraries
```
- ArduinoJson (by Benoit Blanchon) v6.x
- DHT sensor library (by Adafruit) v1.4.x
```

### Step 2: Board Configuration
1. Tools → Board → ESP32 → AI-THINKER ESP32-CAM
2. Upload Speed: 921600
3. Flash Mode: DIO
4. Flash Freq: 80MHz
5. Partition Scheme: Huge APP (1.9MB OTA 0.9MB SPIFFS)

### Step 3: Upload Code
1. Connect ESP32-CAM via USB
2. Press and hold **IO0** button
3. Click **Upload** in Arduino IDE
4. Release **IO0** when upload starts

### Step 4: Verify
- Open Serial Monitor (115200 baud)
- Should show:
  ```
  === TOMATO GUARD - ESP32-CAM START ===
  ✅ Camera initialized
  ✅ DHT sensor initialized
  ✅ System Ready!
  ```

---

## 📊 How It Works

### Every 10 seconds:
1. **Read sensors**
   - Temperature from DHT11
   - Humidity from DHT11
   - Soil Moisture from ADC pin 33
2. **Send to backend**
   ```json
   POST /iot/sensors
   {
     "farm_id": "81db3508-...",
     "temperature": 25.5,
     "humidity": 70.0,
     "soil_moisture": 65
   }
   ```
3. **Get risk assessment** → LED feedback
   - Green = Low risk (safe)
   - Red = Medium/High/Critical risk

### Every 60 seconds:
1. **Capture image** from camera
2. **Send to backend**
   ```
   POST /disease/predict
   (multipart: image + farm_id + zone_code)
   ```
3. **Get AI result** → LED/Buzzer alert
   - Healthy = Green LED
   - Disease detected = Red LED + Buzzer

---

## 🌐 Web Dashboard

Once connected, access at: `http://<ESP32_IP>/`

**Features:**
- ✅ Real-time sensor readings
- ✅ Current risk level
- ✅ Manual capture button
- ✅ Status refresh (5-second intervals)

**Endpoints:**
```
GET  http://<ESP32_IP>/status        → JSON sensor data
GET  http://<ESP32_IP>/capture       → Trigger image capture
GET  http://<ESP32_IP>/               → HTML dashboard
```

---

## 📱 Backend Communication (No Auth!)

### Sensor Data Endpoint
```
Endpoint: POST /iot/sensors
Headers:  Content-Type: application/json
Body:     {
  "farm_id": "string",
  "temperature": float,
  "humidity": float,
  "soil_moisture": int (0-100)
}
Response: {
  "message": "Sensor data received",
  "risk_level": "low|medium|high|critical",
  "analysis": {...}
}
```

### Disease Detection Endpoint
```
Endpoint: POST /disease/predict
Headers:  multipart/form-data
Form:     file (image), farm_id, zone_code
Response: {
  "disease_name": "string",
  "confidence_score": float (0-100),
  "severity": "low|medium|high|critical",
  "treatment": "string"
}
```

---

## 🔍 Troubleshooting

### Camera not initializing
- Check camera ribbon cable connection
- Verify correct board selected (AI-THINKER)
- Try different USB cable/port

### DHT sensor not reading
- Check DATA pin connection (GPIO 14)
- Try 4.7kΩ pull-up resistor on DATA line
- Replace sensor if old

### Not connecting to WiFi
- Verify SSID and password correct
- Check WiFi supports 2.4GHz (not 5GHz only)
- Check router range

### Backend not responding
- Verify ngrok URL is correct and active
- Check Internet connection on ESP32
- Monitor backend logs for errors

### Soil Moisture reading wrong
- Check ADC pin connection (GPIO 33)
- Verify sensor is properly powered (3.3V)
- Calibrate: Dry = ~0%, Wet = ~100%

---

## 📈 Monitoring & Testing

### Check Serial Output
```
📊 Reading sensors...
Temperature: 25.3°C
Humidity: 72.1%
Soil Moisture: 65%
📤 Sending sensor data to: https://...
✅ Sensor data sent successfully!
⚠️ Risk Level: medium
```

### Test with Postman
```
POST http://192.168.x.x/status
→ Get current sensor readings

POST http://192.168.x.x/capture
→ Manually trigger image capture
```

---

## 🎯 Key Differences from Old Code

| Feature | Old Code | New Code |
|---------|----------|----------|
| Authentication | Bearer Token | None (removed) |
| Sensor Interval | Manual trigger | Auto 10 seconds |
| Image Interval | Manual trigger | Auto 60 seconds |
| LED Feedback | Manual control | Automatic based on risk |
| Web Dashboard | Not included | Included on port 80 |
| Risk Assessment | Manual parsing | Automatic with alerts |
| Error Handling | Basic | Enhanced with buzzer/LED |

---

## ✅ Ready to Deploy!

Once configured and tested:
1. ✅ WiFi credentials set
2. ✅ Backend URL correct
3. ✅ Farm ID and Zone Code set
4. ✅ All sensors connected
5. ✅ Serial output shows success

**Your system is ready for production deployment!**

---

**Need help?** Check backend logs:
```bash
# Monitor backend in real-time
tail -f backend.log

# Or check the /alerts endpoint
curl http://localhost:8000/alerts/?limit=5
```
