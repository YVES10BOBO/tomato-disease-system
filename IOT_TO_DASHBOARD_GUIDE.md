# IoT Data → Backend → Dashboard Integration Guide

## 🎯 YOUR SETUP
- ✅ ESP32-CAM (with camera)
- ✅ DHT11 (temperature + humidity)
- ✅ Soil Moisture Sensor
- ✅ LED Red & Green (status indicators)
- ✅ FastAPI Backend (already running)
- ✅ Web Dashboard (Next.js)
- ⚠️ NO Raspberry Pi (using ESP32-CAM directly)

---

## 📋 STEP-BY-STEP PROCESS

### **STEP 1: Verify Backend is Running** ✅
**Status:** Should already be running from earlier

```bash
# Check if backend is running on port 8000
curl http://localhost:8000/
# Should return: {"message": "Tomato Disease Detection System API", "status": "running"}
```

**If not running:**
```bash
cd C:\Final_Year_Project\tomato-disease-system\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

### **STEP 2: Upload Arduino Code to ESP32-CAM** 📤

**Use the code we created:** `ESP32_CAM_TOMATO_GUARD.ino`

**Just update 4 lines:**
```cpp
Line 13:  const char* ssid = "dtechel_hub";
Line 16:  const char* password = "6473@develisa";
Line 19:  const char* BACKEND_URL = "http://192.168.1.102:8000";
Line 22:  const char* ZONE_CODE = "A1";
```

**Upload Steps:**
1. Open Arduino IDE
2. File → Open → Select `ESP32_CAM_TOMATO_GUARD.ino`
3. Tools → Board → Select "AI-THINKER ESP32-CAM"
4. Connect ESP32-CAM to USB
5. Press **IO0 button** on ESP32
6. Click **Upload** ▶️
7. Release **IO0 button** when upload starts
8. Wait for "Upload complete" ✅

**Verify Success:**
- Open Serial Monitor (115200 baud)
- Should show:
  ```
  === TOMATO GUARD - ESP32-CAM STARTING ===
  ✅ Camera initialized
  ✅ DHT sensor initialized
  ✅ WiFi connected!
  ✅ SYSTEM READY
  ```

---

### **STEP 3: Verify IoT Device is Sending Data** 📤

**Check Serial Monitor Output:**
```
📊 Reading sensors...
Temperature: 25.5°C
Humidity: 72.1%
Soil Moisture: 65%
📤 Sending to: http://192.168.1.102:8000/iot/sensors
✅ Sensor data sent successfully!
⚠️ Risk Level: medium
```

**If NOT sending:**
- ❌ Check WiFi SSID & password correct
- ❌ Check backend URL correct (192.168.1.102:8000)
- ❌ Check ESP32 can reach PC with `ping 192.168.1.102`

---

### **STEP 4: Verify Backend is Receiving Data** 🔍

**Check Backend Logs:**

Open a PowerShell window in the backend directory:
```bash
# Watch backend logs in real-time
# You should see every 10 seconds:

INFO:     127.0.0.1:xxxxx - "POST /iot/sensors HTTP/1.1" 201 Created
INFO:     127.0.0.1:xxxxx - "POST /iot/sensors HTTP/1.1" 201 Created
```

**If you see 201 status → Data is being saved!** ✅

---

### **STEP 5: Check Data in Database** 🗄️

**Option A: Use Supabase UI**
1. Go to: https://app.supabase.com
2. Login with your credentials
3. Select your project
4. Go to Tables → `sensor_logs`
5. Should see new rows with:
   - farm_id: 81db3508-...
   - temperature: 25.5
   - humidity: 72.1
   - soil_moisture: 65
   - risk_level: medium
   - recorded_at: [timestamp]

**If data is there → Backend is saving!** ✅

---

### **STEP 6: Test Backend API Endpoints** 📡

**Test in PowerShell or Postman:**

```bash
# GET latest sensor reading
curl http://localhost:8000/iot/sensors/81db3508-b9df-4543-82ce-a12d7b5e1667/latest
```

**Should return:**
```json
{
  "id": "sensor-log-123",
  "farm_id": "81db3508-b9df-4543-82ce-a12d7b5e1667",
  "temperature": 25.5,
  "humidity": 72.1,
  "soil_moisture": 65,
  "risk_level": "medium",
  "recorded_at": "2026-06-20T14:30:00Z"
}
```

**If you get this → API is working!** ✅

---

### **STEP 7: Start Web Dashboard Server** 🖥️

**Navigate to web dashboard:**
```bash
cd C:\Final_Year_Project\tomato-disease-system\web
npm install  # (only first time)
npm run dev
```

**Should show:**
```
> next dev
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Environments: .env.local

✓ Ready in 1500ms
```

---

### **STEP 8: View Data on Dashboard** 📊

**Open browser:**
```
http://localhost:3000
```

**Should see:**
- 🟡 Dashboard Page
- 📊 Real-time sensor values (Temp/Humidity/Soil)
- 📈 24-hour graphs
- ⚠️ Risk level indicator
- 🟢/🔴 LED status

**If data appears → Everything working!** ✅

---

### **STEP 9: Test Image Capture & Disease Detection** 📸

**ESP32-CAM will auto-capture every 60 seconds:**

1. Watch Serial Monitor
2. Should see every 60 seconds:
   ```
   📷 Capturing image...
   Image size: 8492 bytes
   📤 Sending to: http://192.168.1.102:8000/disease/predict
   ✅ Image sent for analysis!
   🦠 Disease: Healthy (92.3% confidence)
   ```

3. Check backend logs for POST /disease/predict
4. Data should appear in database → `detections` table
5. Dashboard should show disease results

---

### **STEP 10: Verify LED Feedback** 💡

**Green LED (GPIO 12):**
- ✅ Lights up when risk level is LOW
- Means: Farm is healthy

**Red LED (GPIO 13):**
- ❌ Lights up when risk level is MEDIUM/HIGH/CRITICAL
- Means: Action needed

**Test by:**
1. Monitor Serial Monitor
2. When `Risk Level: low` → Green LED should be ON
3. When `Risk Level: medium/high/critical` → Red LED should be ON

---

## 🔄 COMPLETE DATA FLOW

```
┌──────────────────────────────┐
│    ESP32-CAM IoT Device      │
├──────────────────────────────┤
│ • Reads DHT11 every 10s      │
│ • Reads soil moisture every 10s
│ • Captures image every 60s   │
│ • Updates LED status         │
└────────────┬─────────────────┘
             │
      Every 10 seconds:
      POST /iot/sensors
      {
        "farm_id": "81db3508-...",
        "temperature": 25.5,
        "humidity": 72.1,
        "soil_moisture": 65
      }
      
      Every 60 seconds:
      POST /disease/predict
      {
        "file": [image],
        "farm_id": "81db3508-...",
        "zone_code": "A1"
      }
             │
             ▼
    ┌─────────────────────┐
    │  FastAPI Backend    │
    ├─────────────────────┤
    │ • Receives sensor data
    │ • Runs AI on image  │
    │ • Calculates risk   │
    │ • Creates alerts    │
    └────────┬────────────┘
             │
             ▼ Saves to Database
    ┌─────────────────────┐
    │ Supabase PostgreSQL │
    ├─────────────────────┤
    │ • sensor_logs       │
    │ • detections        │
    │ • alerts            │
    └────────┬────────────┘
             │
             ▼ Reads from Database
    ┌─────────────────────┐
    │  Web Dashboard      │
    ├─────────────────────┤
    │ • Shows sensor data │
    │ • Shows graphs      │
    │ • Shows detections  │
    │ • Shows alerts      │
    │ • Shows risk level  │
    └─────────────────────┘
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] ESP32-CAM code uploaded successfully
- [ ] Serial Monitor shows sensor readings
- [ ] Backend logs show POST /iot/sensors 201 responses
- [ ] Data appears in Supabase sensor_logs table
- [ ] GET /iot/sensors/latest returns current data
- [ ] Web dashboard starts without errors
- [ ] Dashboard shows sensor values (Temp/Humidity/Soil)
- [ ] Dashboard shows risk level
- [ ] Dashboard shows graphs
- [ ] ESP32-CAM captures images every 60s
- [ ] Backend logs show POST /disease/predict
- [ ] Disease detections appear in dashboard
- [ ] LED indicators working (Green/Red)
- [ ] Alerts appear when disease detected

---

## 🔧 TROUBLESHOOTING

### **Issue: ESP32 won't connect to WiFi**
```
❌ WiFi connection FAILED!
Check SSID and Password
```
**Fix:**
- Verify WiFi name (SSID) exact spelling
- Verify WiFi password exact
- Check WiFi is 2.4GHz (not 5GHz)
- Move ESP32 closer to router

### **Issue: Backend shows 404 error**
```
❌ HTTP Error: 404
```
**Fix:**
- Verify backend URL is correct: `http://192.168.1.102:8000`
- Verify backend is running on port 8000
- Check if IP address changed (use `ipconfig` to verify)
- Try pinging: `ping 192.168.1.102`

### **Issue: No data in Supabase**
```
❌ Database empty
```
**Fix:**
- Check backend logs for errors
- Verify Supabase connection string in backend
- Check database credentials in `.env` file
- Restart backend after checking database

### **Issue: Dashboard shows no data**
```
❌ Dashboard empty
```
**Fix:**
- Verify backend is running
- Verify dashboard can reach backend (http://localhost:8000)
- Check browser console for errors (F12)
- Verify API endpoints are returning data (test with curl)

### **Issue: LEDs not lighting up**
```
❌ LEDs not responding
```
**Fix:**
- Check pin connections (GPIO 12 for green, GPIO 13 for red)
- Check LED polarity (longer leg = positive)
- Check wiring to resistor
- Verify Arduino code has correct GPIO pins

---

## 📱 MOBILE APP (Optional for Demo)

If you want to also show mobile app:

```bash
cd C:\Final_Year_Project\tomato-disease-system\mobile
flutter pub get
flutter run -d windows  # or -d chrome for web preview
```

---

## 🎯 FOR YOUR DEFENSE PRESENTATION

**Show This Flow:**

1. **Live ESP32-CAM on table**
   - Show Serial Monitor with live sensor data
   - Point to DHT11, Soil Moisture Sensor
   - Show LEDs changing color (Green/Red)

2. **Switch to Backend Logs**
   - Show POST /iot/sensors being received every 10 seconds
   - Show POST /disease/predict being received every 60 seconds
   - Explain: "Data coming from IoT is being saved to database"

3. **Switch to Supabase Database**
   - Show sensor_logs table with latest data
   - Show detections table with disease results
   - Explain: "All data is persisted in the database"

4. **Switch to Web Dashboard**
   - Show Dashboard page with live sensor values
   - Show graphs updating in real-time
   - Show risk level changing based on sensor data
   - Show disease detections appearing
   - Explain: "Dashboard reflects real-time IoT monitoring"

5. **Show Mobile App (if available)**
   - Take photo of leaf
   - Show AI analysis results
   - Explain: "Mobile app communicates with backend for AI analysis"

**Narrative:**
> "Our system works like this: The ESP32-CAM device continuously monitors the farm with three sensors - measuring temperature, humidity, and soil moisture. Every 10 seconds, this data is sent to our backend server, which calculates the risk level and stores it in the database. Our web dashboard then displays this real-time data with graphs and indicators. Additionally, every 60 seconds, the ESP32-CAM captures an image which is sent to our AI model (MobileNetV2) for disease detection. The results are shown on both the dashboard and mobile app, with LED indicators providing instant feedback to the farmer."

---

## 🚀 FINAL CHECKLIST FOR DEFENSE

- [x] IoT device sends sensor data every 10 seconds
- [x] IoT device captures image every 60 seconds
- [x] Backend receives and saves all data
- [x] Dashboard displays real-time sensor values
- [x] Dashboard shows graphs and trends
- [x] Dashboard shows risk level
- [x] Dashboard shows disease detections
- [x] Mobile app shows AI analysis results
- [x] LEDs indicate system status
- [x] All components communicating properly

---

**You're ready for your defense!** 🎉
Follow these steps exactly and everything will work smoothly.
