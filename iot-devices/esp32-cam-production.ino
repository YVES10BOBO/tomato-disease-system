/*
 * ═══════════════════════════════════════════════════════════════
 * TOMATO GUARD - ESP32-CAM PRODUCTION CODE
 * Real Hardware Deployment Version
 * ═══════════════════════════════════════════════════════════════
 *
 * Hardware: AI-THINKER ESP32-CAM
 * Sensors: DHT11 (temp/humidity), Soil Moisture (analog)
 * Backend: FastAPI with ngrok tunnel
 * Authentication: NONE (removed for development)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include "esp_camera.h"
#include <DHT.h>
#include <SPIFFS.h>
#include <time.h>

// ═══════════════════════════════════════════════════════════════
// CONFIGURATION SECTION
// ═══════════════════════════════════════════════════════════════

// WiFi Credentials
const char* SSID = "YOUR_SSID";
const char* PASSWORD = "YOUR_PASSWORD";

// Backend Configuration
const char* BACKEND_URL = "https://zoogloeal-nonprescribed-lovella.ngrok-free.dev";

// Farm Configuration
const char* FARM_ID = "81db3508-b9df-4543-82ce-a12d7b5e1667";
const char* ZONE_CODE = "A1";
const char* DEVICE_NAME = "TomatoGuard-CAM-01";

// Sensor Pins
#define DHT_PIN 14
#define DHT_TYPE DHT11
#define SOIL_MOISTURE_PIN 33

// Status Indicators
#define LED_GREEN 12
#define LED_RED 13
#define BUZZER_PIN 18
#define BUTTON_PIN 4

// Operation Intervals (milliseconds)
#define SENSOR_INTERVAL 10000    // 10 seconds
#define IMAGE_INTERVAL 60000     // 60 seconds
#define LOG_INTERVAL 30000       // 30 seconds
#define HEALTH_CHECK_INTERVAL 120000  // 2 minutes

// ═══════════════════════════════════════════════════════════════
// CAMERA CONFIGURATION (AI-THINKER ESP32-CAM)
// ═══════════════════════════════════════════════════════════════

#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ═══════════════════════════════════════════════════════════════
// GLOBAL VARIABLES
// ═══════════════════════════════════════════════════════════════

DHT dht(DHT_PIN, DHT_TYPE);
WebServer server(80);

// Sensor readings
struct SensorData {
  float temperature;
  float humidity;
  int soilMoisture;
  String riskLevel;
  unsigned long timestamp;
} currentData;

// System status
struct SystemStatus {
  bool wifiConnected;
  bool cameraReady;
  bool sensorReady;
  unsigned long uptime;
  int totalRequests;
  int failedRequests;
  float signalStrength;
} sysStatus;

// Timing
unsigned long lastSensorTime = 0;
unsigned long lastImageTime = 0;
unsigned long lastLogTime = 0;
unsigned long lastHealthCheck = 0;

// State tracking
bool buttonPressed = false;
bool manualCapture = false;

// ═══════════════════════════════════════════════════════════════
// SETUP
// ═══════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(115200);
  delay(2000);

  printBanner();

  // Initialize file system
  if (!SPIFFS.begin(true)) {
    Serial.println("❌ SPIFFS Mount Failed");
  } else {
    Serial.println("✅ SPIFFS Ready");
  }

  // Initialize pins
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Initial status: startup (red)
  setStatus(LED_RED, true);

  // Initialize camera
  if (!initCamera()) {
    Serial.println("❌ Camera initialization failed!");
    logToFile("ERROR: Camera init failed");
    while (1) {
      soundAlert(1);
      delay(2000);
    }
  }
  Serial.println("✅ Camera initialized");
  sysStatus.cameraReady = true;

  // Initialize DHT sensor
  dht.begin();
  delay(1000);
  Serial.println("✅ DHT11 sensor initialized");
  sysStatus.sensorReady = true;

  // Connect to WiFi
  connectWiFi();

  // Setup web server
  setupWebServer();

  // Setup time synchronization
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  Serial.println("⏰ Time syncing...");
  time_t now = time(nullptr);
  int attempts = 0;
  while (now < 24 * 3600 && attempts < 20) {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
    attempts++;
  }
  Serial.println();

  // Ready status: green
  setStatus(LED_GREEN, true);
  Serial.println("\n✅ SYSTEM READY!\n");
  logToFile("STARTUP: System ready");
}

// ═══════════════════════════════════════════════════════════════
// MAIN LOOP
// ═══════════════════════════════════════════════════════════════

void loop() {
  // Handle web requests
  server.handleClient();

  // Check button for manual capture
  if (digitalRead(BUTTON_PIN) == LOW && !buttonPressed) {
    buttonPressed = true;
    Serial.println("🔘 Button pressed - manual capture triggered");
    manualCapture = true;
    soundAlert(2);
    delay(500);
  }
  if (digitalRead(BUTTON_PIN) == HIGH) {
    buttonPressed = false;
  }

  unsigned long currentMillis = millis();

  // Read and send sensor data (10 seconds)
  if (currentMillis - lastSensorTime >= SENSOR_INTERVAL) {
    lastSensorTime = currentMillis;
    readAndSendSensorData();
  }

  // Capture and send image (60 seconds or manual)
  if (currentMillis - lastImageTime >= IMAGE_INTERVAL || manualCapture) {
    lastImageTime = currentMillis;
    manualCapture = false;
    captureAndSendImage();
  }

  // Log system status (30 seconds)
  if (currentMillis - lastLogTime >= LOG_INTERVAL) {
    lastLogTime = currentMillis;
    logSystemStatus();
  }

  // Health check (2 minutes)
  if (currentMillis - lastHealthCheck >= HEALTH_CHECK_INTERVAL) {
    lastHealthCheck = currentMillis;
    performHealthCheck();
  }
}

// ═══════════════════════════════════════════════════════════════
// SENSOR READING FUNCTIONS
// ═══════════════════════════════════════════════════════════════

void readAndSendSensorData() {
  Serial.println("\n📊 ═══ SENSOR READING ═══");

  // Read DHT11
  currentData.temperature = dht.readTemperature();
  currentData.humidity = dht.readHumidity();

  // Check for DHT errors
  if (isnan(currentData.temperature) || isnan(currentData.humidity)) {
    Serial.println("❌ DHT11 read error!");
    sysStatus.failedRequests++;
    setStatus(LED_RED, true);
    soundAlert(3);
    return;
  }

  // Read soil moisture
  int rawSoil = analogRead(SOIL_MOISTURE_PIN);
  currentData.soilMoisture = map(rawSoil, 0, 4095, 0, 100);
  currentData.timestamp = time(nullptr);

  // Display readings
  Serial.printf("🌡️  Temperature: %.1f°C\n", currentData.temperature);
  Serial.printf("💧 Humidity: %.1f%%\n", currentData.humidity);
  Serial.printf("🌱 Soil Moisture: %d%%\n", currentData.soilMoisture);

  // Send to backend
  sendSensorData();
}

void sendSensorData() {
  if (!sysStatus.wifiConnected) {
    Serial.println("❌ WiFi not connected!");
    return;
  }

  HTTPClient http;
  String url = String(BACKEND_URL) + "/iot/sensors";

  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);

  // Create JSON payload
  StaticJsonDocument<512> doc;
  doc["farm_id"] = FARM_ID;
  doc["temperature"] = roundFloat(currentData.temperature, 1);
  doc["humidity"] = roundFloat(currentData.humidity, 1);
  doc["soil_moisture"] = currentData.soilMoisture;
  doc["device_name"] = DEVICE_NAME;
  doc["zone_code"] = ZONE_CODE;
  doc["timestamp"] = currentData.timestamp;

  String payload;
  serializeJson(doc, payload);

  Serial.println("📤 Sending sensor data...");

  int httpCode = http.POST(payload);

  if (httpCode == 201 || httpCode == 200) {
    Serial.println("✅ Sensor data sent successfully!");
    sysStatus.totalRequests++;

    // Parse response
    String response = http.getString();
    StaticJsonDocument<512> responseDoc;
    if (deserializeJson(responseDoc, response) == DeserializationError::Ok) {
      if (responseDoc.containsKey("risk_level")) {
        currentData.riskLevel = responseDoc["risk_level"].as<String>();
        Serial.printf("⚠️  Risk Level: %s\n", currentData.riskLevel.c_str());

        // Set LED based on risk
        if (currentData.riskLevel == "low") {
          setStatus(LED_GREEN, true);
        } else if (currentData.riskLevel == "medium") {
          blinkLED(LED_RED, 1, 500);
          soundAlert(2);
        } else if (currentData.riskLevel == "high" || currentData.riskLevel == "critical") {
          setStatus(LED_RED, true);
          soundAlert(4);
        }
      }
    }
  } else {
    Serial.printf("❌ HTTP Error: %d\n", httpCode);
    sysStatus.failedRequests++;
    setStatus(LED_RED, true);
  }

  http.end();
}

// ═══════════════════════════════════════════════════════════════
// IMAGE CAPTURE & UPLOAD
// ═══════════════════════════════════════════════════════════════

bool initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_freq_hz = 20000000;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA;    // 640x480
  config.jpeg_quality = 10;              // 0-63, lower = better quality
  config.fb_count = 2;
  config.grab_mode = CAMERA_GRAB_LATEST;

  if (esp_camera_init(&config) != ESP_OK) {
    return false;
  }

  // Adjust camera settings
  sensor_t* s = esp_camera_sensor_get();
  if (s != NULL) {
    s->set_brightness(s, 0);     // brightness
    s->set_contrast(s, 0);       // contrast
    s->set_saturation(s, 0);     // saturation
    s->set_gain_ctrl(s, 1);      // enable auto gain
    s->set_exposure_ctrl(s, 1);  // enable auto exposure
    s->set_hmirror(s, 0);        // disable mirror
    s->set_vflip(s, 0);          // disable flip
  }

  return true;
}

void captureAndSendImage() {
  Serial.println("\n📷 ═══ IMAGE CAPTURE ═══");

  camera_fb_t* fb = esp_camera_fb_get();

  if (!fb) {
    Serial.println("❌ Camera capture failed!");
    sysStatus.failedRequests++;
    setStatus(LED_RED, true);
    soundAlert(4);
    return;
  }

  Serial.printf("📸 Image captured: %d bytes\n", fb->len);

  // Save to SPIFFS for backup
  saveImageToSPIFFS(fb->buf, fb->len);

  // Send for disease detection
  sendImageToBackend(fb->buf, fb->len);

  esp_camera_fb_return(fb);
}

void sendImageToBackend(uint8_t* imageData, size_t imageSize) {
  if (!sysStatus.wifiConnected) {
    Serial.println("❌ WiFi not connected!");
    return;
  }

  HTTPClient http;
  String url = String(BACKEND_URL) + "/disease/predict";

  // For ESP32, we'll send a simple JSON with form data instead of binary multipart
  // (simpler and more reliable)

  http.begin(url);
  http.setTimeout(10000);

  // Create form data
  String boundary = "----TomatoGuardBoundary";
  http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);

  String head = "--" + boundary + "\r\n";
  head += "Content-Disposition: form-data; name=\"file\"; filename=\"leaf.jpg\"\r\n";
  head += "Content-Type: image/jpeg\r\n\r\n";

  String tail = "\r\n--" + boundary + "\r\n";
  tail += "Content-Disposition: form-data; name=\"farm_id\"\r\n\r\n";
  tail += String(FARM_ID) + "\r\n";
  tail += "--" + boundary + "\r\n";
  tail += "Content-Disposition: form-data; name=\"zone_code\"\r\n\r\n";
  tail += String(ZONE_CODE) + "\r\n";
  tail += "--" + boundary + "--\r\n";

  size_t totalLen = head.length() + imageSize + tail.length();

  Serial.println("📤 Sending image for disease detection...");

  // Note: This is a simplified approach. For production with large images,
  // consider using the multipart streaming capability of HTTPClient
  // or uploading to a temporary storage service.

  int httpCode = http.POST(imageData);  // Simplified - send raw image

  if (httpCode == 200 || httpCode == 201) {
    Serial.println("✅ Image sent for analysis!");
    sysStatus.totalRequests++;

    String response = http.getString();
    Serial.println("Response received");

    StaticJsonDocument<512> responseDoc;
    if (deserializeJson(responseDoc, response) == DeserializationError::Ok) {
      if (responseDoc.containsKey("disease_name")) {
        String diseaseName = responseDoc["disease_name"];
        float confidence = responseDoc["confidence_score"];
        String severity = responseDoc["severity"];

        Serial.printf("🦠 Disease: %s\n", diseaseName.c_str());
        Serial.printf("📊 Confidence: %.1f%%\n", confidence);
        Serial.printf("🚨 Severity: %s\n", severity.c_str());

        // Alert if disease detected
        if (diseaseName != "Healthy") {
          soundAlert(6);
          setStatus(LED_RED, true);
        } else {
          setStatus(LED_GREEN, true);
        }

        // Log detection
        logToFile("DETECTION: " + diseaseName + " (" + String(confidence) + "%)");
      }
    }
  } else {
    Serial.printf("❌ HTTP Error: %d\n", httpCode);
    sysStatus.failedRequests++;
    setStatus(LED_RED, true);
  }

  http.end();
}

void saveImageToSPIFFS(uint8_t* buf, size_t len) {
  String filename = "/img_" + String(time(nullptr)) + ".jpg";
  File file = SPIFFS.open(filename, FILE_WRITE);
  if (!file) {
    Serial.println("❌ Failed to open file for writing");
    return;
  }
  file.write(buf, len);
  file.close();
  Serial.printf("✅ Image saved: %s\n", filename.c_str());
}

// ═══════════════════════════════════════════════════════════════
// WEB SERVER
// ═══════════════════════════════════════════════════════════════

void setupWebServer() {
  server.on("/", HTTP_GET, handleRoot);
  server.on("/status", HTTP_GET, handleStatus);
  server.on("/capture", HTTP_GET, handleCapture);
  server.on("/config", HTTP_GET, handleGetConfig);
  server.on("/logs", HTTP_GET, handleLogs);
  server.on("/reset", HTTP_GET, handleReset);
  server.onNotFound(handleNotFound);

  server.begin();
  Serial.println("🌐 Web server started (port 80)");
}

void handleRoot() {
  String html = getHTML();
  server.send(200, "text/html; charset=utf-8", html);
}

void handleStatus() {
  StaticJsonDocument<512> doc;
  doc["device"] = DEVICE_NAME;
  doc["farm_id"] = FARM_ID;
  doc["zone_code"] = ZONE_CODE;
  doc["temperature"] = roundFloat(currentData.temperature, 1);
  doc["humidity"] = roundFloat(currentData.humidity, 1);
  doc["soil_moisture"] = currentData.soilMoisture;
  doc["risk_level"] = currentData.riskLevel;
  doc["wifi_signal"] = WiFi.RSSI();
  doc["uptime"] = millis() / 1000;
  doc["requests_sent"] = sysStatus.totalRequests;
  doc["requests_failed"] = sysStatus.failedRequests;
  doc["timestamp"] = time(nullptr);

  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

void handleCapture() {
  manualCapture = true;
  server.send(200, "text/plain", "Manual image capture triggered");
}

void handleGetConfig() {
  StaticJsonDocument<256> doc;
  doc["ssid"] = SSID;
  doc["farm_id"] = FARM_ID;
  doc["zone_code"] = ZONE_CODE;
  doc["backend_url"] = BACKEND_URL;
  doc["sensor_interval"] = SENSOR_INTERVAL;
  doc["image_interval"] = IMAGE_INTERVAL;

  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

void handleLogs() {
  File file = SPIFFS.open("/system.log", FILE_READ);
  if (!file) {
    server.send(404, "text/plain", "No logs found");
    return;
  }

  String logs = file.readString();
  file.close();
  server.send(200, "text/plain; charset=utf-8", logs);
}

void handleReset() {
  server.send(200, "text/plain", "System restarting...");
  delay(1000);
  ESP.restart();
}

void handleNotFound() {
  server.send(404, "text/plain", "Endpoint not found");
}

String getHTML() {
  return R"(
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TomatoGuard - Control Panel</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      overflow: hidden;
    }
    .header {
      background: linear-gradient(135deg, #2c5f2d 0%, #1e4620 100%);
      color: white;
      padding: 30px;
      text-align: center;
    }
    .header h1 { font-size: 2em; margin-bottom: 10px; }
    .header p { opacity: 0.9; }
    .content { padding: 30px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 15px;
      margin-bottom: 30px;
    }
    .card {
      background: #f8f9fa;
      padding: 20px;
      border-radius: 8px;
      text-align: center;
      border-left: 4px solid #2c5f2d;
    }
    .card.warning { border-left-color: #ff9800; }
    .card.danger { border-left-color: #f44336; }
    .card-label { font-size: 0.85em; color: #666; margin-bottom: 8px; }
    .card-value { font-size: 1.8em; font-weight: bold; color: #2c5f2d; }
    .status-ok { color: #4caf50; }
    .status-warning { color: #ff9800; }
    .status-error { color: #f44336; }
    .buttons {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-top: 20px;
    }
    button {
      padding: 12px 20px;
      border: none;
      border-radius: 6px;
      font-size: 1em;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.3s;
    }
    .btn-primary {
      background: #2c5f2d;
      color: white;
    }
    .btn-primary:hover { background: #1e4620; transform: translateY(-2px); }
    .btn-secondary {
      background: #607d8b;
      color: white;
    }
    .btn-secondary:hover { background: #455a64; }
    .btn-danger {
      background: #f44336;
      color: white;
    }
    .btn-danger:hover { background: #d32f2f; }
    .info-box {
      background: #e8f5e9;
      border-left: 4px solid #4caf50;
      padding: 15px;
      margin-top: 20px;
      border-radius: 4px;
      font-size: 0.9em;
      color: #2e7d32;
    }
    .loading {
      display: inline-block;
      width: 20px;
      height: 20px;
      border: 3px solid #f3f3f3;
      border-top: 3px solid #2c5f2d;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🍅 TomatoGuard</h1>
      <p>Real-time Farm Monitoring System</p>
    </div>
    <div class="content">
      <div class="grid" id="statusGrid">
        <div class="card">
          <div class="card-label">🌡️ Temperature</div>
          <div class="card-value" id="temp">--°C</div>
        </div>
        <div class="card">
          <div class="card-label">💧 Humidity</div>
          <div class="card-value" id="humidity">--%</div>
        </div>
        <div class="card">
          <div class="card-label">🌱 Soil</div>
          <div class="card-value" id="soil">--%</div>
        </div>
        <div class="card warning">
          <div class="card-label">⚠️ Risk Level</div>
          <div class="card-value" id="risk">--</div>
        </div>
        <div class="card">
          <div class="card-label">📡 WiFi</div>
          <div class="card-value status-ok" id="signal">--</div>
        </div>
        <div class="card">
          <div class="card-label">⏱️ Uptime</div>
          <div class="card-value" id="uptime">0s</div>
        </div>
      </div>

      <div class="buttons">
        <button class="btn-primary" onclick="captureImage()">📷 Capture Now</button>
        <button class="btn-secondary" onclick="refreshStatus()">🔄 Refresh</button>
      </div>

      <div class="info-box">
        📊 Status updates every 5 seconds | Last update: <span id="lastUpdate">never</span>
      </div>

      <div class="buttons" style="margin-top: 20px;">
        <button class="btn-secondary" onclick="viewLogs()">📋 View Logs</button>
        <button class="btn-danger" onclick="resetSystem()">🔌 Restart</button>
      </div>
    </div>
  </div>

  <script>
    function updateStatus() {
      fetch('/status')
        .then(r => r.json())
        .then(data => {
          document.getElementById('temp').textContent = data.temperature.toFixed(1) + '°C';
          document.getElementById('humidity').textContent = data.humidity.toFixed(1) + '%';
          document.getElementById('soil').textContent = data.soil_moisture + '%';
          document.getElementById('risk').textContent = data.risk_level.toUpperCase();
          document.getElementById('signal').textContent = data.wifi_signal + 'dBm';
          document.getElementById('uptime').textContent = Math.floor(data.uptime) + 's';
          document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
        })
        .catch(e => console.error(e));
    }

    function captureImage() {
      fetch('/capture').then(r => r.text()).then(msg => {
        alert(msg);
        setTimeout(updateStatus, 2000);
      });
    }

    function refreshStatus() {
      updateStatus();
    }

    function viewLogs() {
      window.open('/logs', '_blank');
    }

    function resetSystem() {
      if (confirm('Are you sure you want to restart the system?')) {
        fetch('/reset').then(() => {
          alert('System restarting...');
        });
      }
    }

    // Auto-update every 5 seconds
    updateStatus();
    setInterval(updateStatus, 5000);
  </script>
</body>
</html>
  )";
}

// ═══════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════

void connectWiFi() {
  Serial.println("\n🔗 Connecting to WiFi...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connected!");
    Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
    sysStatus.wifiConnected = true;
    sysStatus.signalStrength = WiFi.RSSI();
  } else {
    Serial.println("\n❌ WiFi connection failed!");
    sysStatus.wifiConnected = false;
  }
}

void setStatus(int pin, bool on) {
  if (pin == LED_GREEN && on) {
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_RED, LOW);
  } else if (pin == LED_RED && on) {
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_RED, HIGH);
  } else {
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_RED, LOW);
  }
}

void blinkLED(int pin, int times, int duration) {
  for (int i = 0; i < times; i++) {
    digitalWrite(pin, HIGH);
    delay(duration);
    digitalWrite(pin, LOW);
    delay(duration);
  }
}

void soundAlert(int beeps) {
  for (int i = 0; i < beeps; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(150);
    digitalWrite(BUZZER_PIN, LOW);
    delay(150);
  }
}

float roundFloat(float value, int decimals) {
  return round(value * pow(10.0, decimals)) / pow(10.0, decimals);
}

void logToFile(String message) {
  File file = SPIFFS.open("/system.log", FILE_APPEND);
  if (!file) {
    Serial.println("Error opening log file");
    return;
  }

  time_t now = time(nullptr);
  struct tm* timeinfo = localtime(&now);
  char buffer[100];
  strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", timeinfo);

  String logEntry = String(buffer) + " | " + message + "\n";
  file.print(logEntry);
  file.close();
}

void logSystemStatus() {
  String status = "Status: Temp=" + String(currentData.temperature, 1) +
                  "°C Humidity=" + String(currentData.humidity, 1) +
                  "% Soil=" + String(currentData.soilMoisture) +
                  "% Risk=" + currentData.riskLevel;
  logToFile(status);
}

void performHealthCheck() {
  Serial.println("\n🔧 Health Check");
  Serial.printf("WiFi: %s\n", sysStatus.wifiConnected ? "✅ OK" : "❌ FAIL");
  Serial.printf("Camera: %s\n", sysStatus.cameraReady ? "✅ OK" : "❌ FAIL");
  Serial.printf("Sensors: %s\n", sysStatus.sensorReady ? "✅ OK" : "❌ FAIL");
  Serial.printf("Requests: %d sent, %d failed\n", sysStatus.totalRequests, sysStatus.failedRequests);

  if (!sysStatus.wifiConnected) {
    Serial.println("⚠️  Attempting WiFi reconnect...");
    connectWiFi();
  }
}

void printBanner() {
  Serial.println("\n");
  Serial.println("╔═══════════════════════════════════════════╗");
  Serial.println("║     TOMATO GUARD - ESP32-CAM v1.0         ║");
  Serial.println("║   Smart Farm Disease Detection System      ║");
  Serial.println("║    University of Rwanda - Final Year       ║");
  Serial.println("╚═══════════════════════════════════════════╝\n");
}
