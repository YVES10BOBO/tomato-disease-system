# 🍅 TomatoGuard - Complete IoT Devices Guide

## 📁 Available IoT Device Codes

### 1. **ESP32-CAM (Production Hardware)**
- **File**: `esp32-cam-production.ino`
- **Hardware**: AI-THINKER ESP32-CAM module
- **Status**: ✅ Complete & Tested
- **Features**:
  - Built-in 2MP OV2640 camera
  - WiFi connectivity
  - Real sensor readings (DHT11/DHT22)
  - Web dashboard (port 80)
  - LED status indicators
  - Buzzer alerts
  - SPIFFS file system
  - Automatic sensor polling every 10 seconds
  - Automatic image capture every 60 seconds
  - Health monitoring
  - System logging

---

### 2. **ESP32-CAM (Wokwi Simulator)**
- **File**: `wokwi-simulation-sketch.cpp`
- **Platform**: Wokwi online simulator
- **Status**: ✅ Complete
- **Features**:
  - Virtual testing environment
  - Simulated sensor data
  - Realistic sensor variations
  - No hardware needed
  - Same API integration as real hardware
  - Button for manual capture
  - Debug output for all operations

**Wokwi Configuration**:
- **Diagram**: `wokwi-diagram.json`
- **Components**:
  - ESP32 microcontroller
  - DHT22 sensor (simulated)
  - Analog joystick (soil moisture simulation)
  - Red LED (risk indicator)
  - Green LED (status indicator)
  - Buzzer (alerts)
  - Push button (manual trigger)
  - OLED display (status)

---

### 3. **Raspberry Pi Camera Module**
- **File**: `raspberry-pi-camera.py`
- **Hardware**: Raspberry Pi 4 + Camera Module v2
- **Status**: ✅ Complete (requires Raspberry Pi setup)
- **Features**:
  - Native Raspberry Pi camera integration
  - Threaded sensor reading
  - Background image capture
  - Python-based system
  - Logging to file
  - Hardware fallback to simulation
  - ADS1115 ADC support for analog sensors
  - GPIO control for indicators
  - Structured JSON logging

---

## 🔧 Hardware Configurations

### ESP32-CAM Pinout

| Component | GPIO Pin | Type | Purpose |
|-----------|----------|------|---------|
| DHT11/DHT22 | GPIO 14 | Digital | Temperature & Humidity |
| Soil Moisture | GPIO 33 | Analog | Soil moisture percentage |
| Green LED | GPIO 12 | Digital | Status (healthy) |
| Red LED | GPIO 13 | Digital | Status (warning/error) |
| Buzzer | GPIO 18 | Digital | Audible alerts |
| Button | GPIO 4 | Digital | Manual capture trigger |
| Camera Data | GPIO 5,18,19,21-27,32-36,39 | SPI | Camera interface |

### Raspberry Pi GPIO Pinout

| Component | GPIO Pin | Type | Purpose |
|-----------|----------|------|---------|
| DHT11/DHT22 | GPIO 17 | Digital | Temperature & Humidity |
| Soil Moisture | ADC Ch 0 | Analog | Via ADS1115 module |
| Green LED | GPIO 24 | Digital | Status (healthy) |
| Red LED | GPIO 23 | Digital | Status (warning) |
| Buzzer | GPIO 27 | Digital | Audible alerts |
| Button | GPIO 22 | Digital | Manual trigger |
| Camera | CSI | Camera | Raspberry Pi camera module |

---

## 📊 Sensor Specifications

### DHT11 vs DHT22 Comparison

| Feature | DHT11 | DHT22 |
|---------|-------|-------|
| Temperature Range | 0-50°C | -40-80°C |
| Humidity Range | 20-80% | 0-100% |
| Accuracy (Temp) | ±2°C | ±0.5°C |
| Accuracy (Humidity) | ±5% | ±2% |
| Cost | Low | Moderate |
| Wokwi Support | No | ✅ Yes |

**Recommendation**: Use DHT22 for better accuracy in production

### Soil Moisture Sensor

- **Type**: Capacitive soil moisture sensor
- **Output**: 0-4095 ADC value
- **Conversion**: `percentage = map(0-4095 to 0-100)`
- **Dry Soil**: ~100 ADC (0%)
- **Wet Soil**: ~0 ADC (100%)
- **ADC Module**: ADS1115 (for Raspberry Pi)

---

## 🌐 Backend Endpoints (All No Auth Required)

### IoT Sensor Endpoints

```
POST /iot/sensors
  - Temperature (float)
  - Humidity (float)
  - Soil Moisture (int 0-100)
  
Response:
  - risk_level: low|medium|high|critical
  - analysis: detailed risk factors
```

```
GET /iot/sensors/{farm_id}/latest
  - Returns latest sensor reading
  
GET /iot/sensors/{farm_id}/history?limit=50
  - Returns historical readings
```

### Disease Detection Endpoints

```
POST /disease/predict
  - Image file (multipart)
  - farm_id
  - zone_code
  
Response:
  - disease_name
  - confidence_score (0-100)
  - severity: low|medium|high|critical
  - treatment recommendations
```

### Alert Endpoints

```
GET /alerts?limit=100
  - Returns all alerts
  
GET /alerts/farm/{farm_id}?limit=20
  - Returns farm-specific alerts
```

---

## 🚀 Quick Start Guides

### Option 1: ESP32-CAM (Real Hardware)

**Step 1: Hardware Setup**
```
1. Connect DHT11 to GPIO 14
2. Connect Soil Sensor to GPIO 33
3. Connect Green LED to GPIO 12
4. Connect Red LED to GPIO 13
5. Connect Buzzer to GPIO 18
6. Connect Button to GPIO 4
```

**Step 2: Code Upload**
```
1. Open esp32-cam-production.ino in Arduino IDE
2. Update WiFi credentials (line 21-22)
3. Update BACKEND_URL (line 25)
4. Update FARM_ID (line 28)
5. Select Board: AI-THINKER ESP32-CAM
6. Upload
```

**Step 3: Verify**
- Check Serial Monitor for startup messages
- Access web dashboard at `http://<ESP32_IP>/`
- See real-time sensor data

---

### Option 2: Wokwi Simulator (No Hardware Needed)

**Step 1: Online**
```
1. Go to https://wokwi.com
2. Create new Arduino project
3. Copy wokwi-simulation-sketch.cpp into editor
4. Load wokwi-diagram.json
5. Click Play to start simulation
```

**Step 2: Local (VS Code)**
```
1. Install Wokwi extension in VS Code
2. Copy files to VS Code workspace
3. Press Ctrl+Shift+P → "Wokwi: Start Simulator"
4. Simulation runs in VS Code panel
```

**Step 3: Monitor**
- Watch serial output
- Click button for manual capture
- See LED status changes

---

### Option 3: Raspberry Pi Camera

**Step 1: Setup**
```bash
# Install dependencies
sudo pip3 install requests adafruit-circuitpython-dht adafruit-circuitpython-ads1x15

# Create directories
mkdir -p ~/tomato-guard/{images,logs}

# Copy script
cp raspberry-pi-camera.py ~/tomato-guard/
chmod +x ~/tomato-guard/raspberry-pi-camera.py
```

**Step 2: Configure**
```bash
# Edit config in script
nano ~/tomato-guard/raspberry-pi-camera.py

# Update:
# - FARM_ID
# - ZONE_CODE
# - BACKEND_URL
```

**Step 3: Run**
```bash
# Test run
python3 ~/tomato-guard/raspberry-pi-camera.py

# Run as service (systemd)
sudo systemctl start tomato-guard
sudo systemctl status tomato-guard
```

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────┐
│              IoT DEVICE                          │
│ (ESP32-CAM / Wokwi / Raspberry Pi)              │
├─────────────────────────────────────────────────┤
│                                                  │
│  DHT Sensor ──────┐                             │
│                   ├──> Device Code              │
│  Soil Moisture ──┤                              │
│                   ├──> Buffer Data              │
│  Camera ─────────┘                              │
│                                                  │
│  Every 10s: Send Sensor Data                   │
│  Every 60s: Capture & Send Image               │
│                                                  │
└──────────────────┬──────────────────────────────┘
                   │ HTTP/HTTPS
                   │ (no auth headers)
                   ▼
        ┌──────────────────────────┐
        │  ngrok Tunnel            │
        │  (ngrok-free.dev)        │
        └──────────────┬───────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │  FastAPI Backend         │
        │  /iot/sensors            │
        │  /disease/predict        │
        │  /alerts                 │
        └──────────────┬───────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │  Supabase Database       │
        │  - sensor_logs           │
        │  - detections            │
        │  - alerts                │
        └──────────────────────────┘
```

---

## 📈 Operation Intervals

| Task | Interval | Duration | Purpose |
|------|----------|----------|---------|
| Sensor Read | 10 seconds | ~100ms | Continuous monitoring |
| Image Capture | 60 seconds | ~1-2s | Regular disease scanning |
| Health Check | 5 minutes | ~50ms | System status verification |
| Data Logging | Real-time | ~10ms | Event tracking |
| LED Update | On event | ~100ms | Status indication |

---

## 🔍 Debugging & Troubleshooting

### ESP32-CAM Issues

**Camera not initializing**
```
❌ Problem: Camera init failed
✅ Solution:
  - Check ribbon cable connection
  - Verify correct board (AI-THINKER)
  - Try different USB cable
  - Reset camera pin (GPIO 32)
```

**DHT sensor not reading**
```
❌ Problem: DHT read error
✅ Solution:
  - Add 4.7kΩ pull-up resistor
  - Check GPIO 14 connection
  - Replace sensor if old (>2 years)
  - Use shorter wires (<50cm)
```

**WiFi not connecting**
```
❌ Problem: WiFi connection failed
✅ Solution:
  - Check SSID and password
  - Ensure 2.4GHz band (not 5GHz only)
  - Verify router nearby
  - Check antenna condition
```

**Backend connection timeout**
```
❌ Problem: HTTP timeout
✅ Solution:
  - Verify ngrok URL is active
  - Check Internet connection
  - Monitor backend logs
  - Increase timeout (in code)
```

### Wokwi Issues

**Simulator won't start**
```
❌ Problem: Extension not found
✅ Solution:
  - Update Wokwi extension
  - Stop Extension Bisect
  - Restart VS Code
  - Check internet connection
```

**Simulated sensors not changing**
```
❌ Problem: Fixed values
✅ Solution:
  - Check sensor simulation code
  - Verify component connections
  - Enable WiFi simulation
  - Reset simulator
```

### Raspberry Pi Issues

**GPIO permission denied**
```
❌ Problem: PermissionError
✅ Solution:
  - Add user to gpio group: sudo usermod -a -G gpio $USER
  - Restart terminal
  - Or run as sudo
```

**Camera module not detected**
```
❌ Problem: Camera init failed
✅ Solution:
  - Enable camera in raspi-config
  - Check ribbon cable orientation
  - Run: vcgencmd get_camera
  - Check dmesg logs
```

**ADS1115 I2C not working**
```
❌ Problem: I2C communication error
✅ Solution:
  - Verify SDA/SCL connections
  - Check I2C is enabled: sudo raspi-config
  - List devices: i2cdetect -y 1
  - Check address (0x48)
```

---

## 📋 Checklist Before Deployment

### Pre-Flight Checks

- [ ] All sensor connections verified
- [ ] Camera lens clean and focused
- [ ] WiFi credentials correct
- [ ] Backend URL updated (ngrok)
- [ ] Farm ID and Zone Code set
- [ ] Power supply adequate (5V 2A minimum)
- [ ] All LEDs light up during startup
- [ ] Serial monitor shows ✅ messages
- [ ] Web dashboard accessible
- [ ] First sensor reading successful
- [ ] Image capture and analysis working

### Backend Verification

- [ ] Backend running and responsive
- [ ] ngrok tunnel active
- [ ] All endpoints accepting requests
- [ ] Database connected
- [ ] No 401 errors (auth removed)
- [ ] Response times acceptable (<5s)

---

## 📞 Support & Resources

**Documentation**
- Backend API: `/backend/docs` (Swagger UI)
- Database Schema: `/backend/database/schema.sql`
- Model Info: `/backend/app/disease/ai_model.py`

**Testing Tools**
- Postman collection included
- cURL examples in API guide
- Web dashboard for visual testing

**Logs**
- **ESP32**: Serial Monitor @ 115200 baud
- **Wokwi**: Console panel
- **Raspberry Pi**: `/home/pi/tomato-guard/logs/`

---

## 🎯 Next Steps

1. **Choose Hardware**: ESP32-CAM (easiest) or Raspberry Pi (more features)
2. **Upload Code**: Follow Quick Start for your device
3. **Test Sensors**: Verify readings in web dashboard
4. **Test Backend**: Use Postman to test endpoints
5. **Deploy**: Mount hardware on farm
6. **Monitor**: Check web dashboard daily

---

## 📝 License & Attribution

**TomatoGuard IoT System**
- University of Rwanda - Final Year Project
- AI & IoT Integration for Agriculture
- Open Source - Education Purpose

---

**Last Updated**: June 2026
**Version**: 1.0.0
**Status**: Production Ready ✅
