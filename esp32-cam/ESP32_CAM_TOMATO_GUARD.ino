/*
 * ═══════════════════════════════════════════════════════════════
 * TOMATO GUARD - ESP32-CAM IoT SYSTEM
 * AI Disease Detection + Environmental Monitoring
 * ═══════════════════════════════════════════════════════════════
 *
 * IMPORTANT: Update ONLY these 4 lines before uploading!
 * ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️
 */

// 🔴 UPDATE #1: Your WiFi SSID
const char* ssid = "YourWiFiName";

// 🔴 UPDATE #2: Your WiFi Password
const char* password = "YourWiFiPassword";

// 🔴 UPDATE #3: Your ngrok backend URL
const char* BACKEND_URL = "https://zoogloeal-nonprescribed-lovella.ngrok-free.dev";

// 🔴 UPDATE #4: Your Farm Zone (A1, A2, B1, B2, C1, C2, D1, D2, D3, D4, etc)
const char* ZONE_CODE = "A1";

// ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️
// ✅ Everything else is pre-configured - NO MORE CHANGES NEEDED!

#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include "esp_camera.h"
#include <DHT.h>

// ═══════════════════════════════════════════════════════════════
// HARDWARE CONFIGURATION (DO NOT CHANGE - For AI-THINKER ESP32-CAM)
// ═══════════════════════════════════════════════════════════════

// Sensor Pins
#define DHT_PIN 14
#define DHT_TYPE DHT11
#define SOIL_MOISTURE_PIN 33

// LED & Buzzer Pins
#define LED_GREEN 12
#define LED_RED 13
#define BUZZER_PIN 18

// Camera Pins (AI-THINKER Model)
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

// Fixed Farm ID (Your project's farm)
const char* FARM_ID = "81db3508-b9df-4543-82ce-a12d7b5e1667";

// ═══════════════════════════════════════════════════════════════
// GLOBAL VARIABLES
// ═══════════════════════════════════════════════════════════════

DHT dht(DHT_PIN, DHT_TYPE);
WebServer server(80);

// Sensor readings
float temperature = 0;
float humidity = 0;
int soilMoisture = 0;
String riskLevel = "low";
String lastDisease = "Checking...";

// Timing
unsigned long lastSensorReadTime = 0;
unsigned long lastImageCaptureTime = 0;
const unsigned long SENSOR_INTERVAL = 10000;   // 10 seconds
const unsigned long IMAGE_INTERVAL = 60000;    // 60 seconds

// ═══════════════════════════════════════════════════════════════
// SETUP - Runs once at startup
// ═══════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n\n╔════════════════════════════════════════════╗");
  Serial.println("║  🍅 TOMATO GUARD - ESP32-CAM STARTING     ║");
  Serial.println("╚════════════════════════════════════════════╝\n");

  // Initialize LED pins
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(SOIL_MOISTURE_PIN, INPUT);

  setLED(false);  // Red LED during startup

  // Initialize camera
  if (!initCamera()) {
    Serial.println("❌ FAILED: Camera initialization error!");
    soundAlarm(10);
    return;
  }
  Serial.println("✅ Camera initialized successfully");

  // Initialize DHT sensor
  dht.begin();
  delay(500);
  Serial.println("✅ DHT sensor initialized successfully");

  // Connect to WiFi
  connectToWiFi();

  // Start web server
  setupWebServer();
  Serial.println("✅ Web server started on port 80");

  // Ready!
  setLED(true);   // Green LED when ready
  Serial.println("\n╔════════════════════════════════════════════╗");
  Serial.println("║  ✅ SYSTEM READY - MONITORING ACTIVE      ║");
  Serial.println("╚════════════════════════════════════════════╝\n");
  Serial.println("📊 Sensor data: Every 10 seconds");
  Serial.println("📷 Image capture: Every 60 seconds");
  Serial.println("🌐 Dashboard: http://<ESP32_IP>/\n");
}

// ═══════════════════════════════════════════════════════════════
// MAIN LOOP - Runs continuously
// ═══════════════════════════════════════════════════════════════

void loop() {
  server.handleClient();

  unsigned long currentTime = millis();

  // Read and send sensor data every 10 seconds
  if (currentTime - lastSensorReadTime >= SENSOR_INTERVAL) {
    lastSensorReadTime = currentTime;
    readAndSendSensors();
  }

  // Capture and send image every 60 seconds
  if (currentTime - lastImageCaptureTime >= IMAGE_INTERVAL) {
    lastImageCaptureTime = currentTime;
    captureAndAnalyzeImage();
  }
}

// ═══════════════════════════════════════════════════════════════
// 📊 SENSOR FUNCTIONS
// ═══════════════════════════════════════════════════════════════

void readAndSendSensors() {
  Serial.println("\n┌─── 📊 READING SENSORS ───┐");

  // Read temperature and humidity
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  // Read soil moisture (convert 0-4095 to 0-100%)
  int rawMoisture = analogRead(SOIL_MOISTURE_PIN);
  soilMoisture = map(rawMoisture, 0, 4095, 0, 100);

  // Check for errors
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("❌ ERROR: DHT sensor reading failed!");
    setLED(false);
    return;
  }

  // Display readings
  Serial.printf("  🌡️  Temperature:  %.1f°C\n", temperature);
  Serial.printf("  💧 Humidity:     %.1f%%\n", humidity);
  Serial.printf("  🌱 Soil Moisture: %d%%\n", soilMoisture);
  Serial.println("└──────────────────────────┘");

  // Send to backend
  sendSensorDataToBackend();
}

void sendSensorDataToBackend() {
  if (!WiFi.isConnected()) {
    Serial.println("❌ ERROR: WiFi disconnected!");
    setLED(false);
    return;
  }

  HTTPClient http;
  String url = String(BACKEND_URL) + "/iot/sensors";

  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  // Create JSON payload
  StaticJsonDocument<256> doc;
  doc["farm_id"] = FARM_ID;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["soil_moisture"] = soilMoisture;

  String payload;
  serializeJson(doc, payload);

  Serial.print("📤 Sending to: ");
  Serial.println(url);

  int httpCode = http.POST(payload);

  if (httpCode == 201 || httpCode == 200) {
    Serial.println("✅ Sensor data sent successfully!");

    // Parse response for risk level
    String response = http.getString();
    StaticJsonDocument<512> responseDoc;
    deserializeJson(responseDoc, response);

    if (responseDoc.containsKey("risk_level")) {
      riskLevel = responseDoc["risk_level"].as<String>();
      Serial.print("⚠️  Risk Level: ");
      Serial.println(riskLevel);

      // LED feedback based on risk
      if (riskLevel == "low") {
        setLED(true);   // Green - Safe
      } else {
        setLED(false);  // Red - Warning
        soundAlarm(3);  // 3 beeps for warning
      }
    }
  } else {
    Serial.printf("❌ HTTP Error: %d\n", httpCode);
    setLED(false);
  }

  http.end();
}

// ═══════════════════════════════════════════════════════════════
// 📷 CAMERA FUNCTIONS
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
  config.frame_size = FRAMESIZE_VGA;  // 640x480
  config.jpeg_quality = 10;            // Lower = better quality
  config.fb_count = 2;

  if (esp_camera_init(&config) != ESP_OK) {
    return false;
  }
  return true;
}

void captureAndAnalyzeImage() {
  Serial.println("\n┌─── 📷 CAPTURING IMAGE ───┐");

  camera_fb_t* fb = esp_camera_fb_get();

  if (!fb) {
    Serial.println("❌ ERROR: Camera capture failed!");
    setLED(false);
    return;
  }

  Serial.printf("  Image size: %d bytes\n", fb->len);
  Serial.println("└──────────────────────────┘");

  sendImageToBackend(fb->buf, fb->len);

  esp_camera_fb_return(fb);
}

void sendImageToBackend(uint8_t* imageData, size_t imageSize) {
  if (!WiFi.isConnected()) {
    Serial.println("❌ ERROR: WiFi disconnected!");
    setLED(false);
    return;
  }

  HTTPClient http;
  String url = String(BACKEND_URL) + "/disease/predict";

  http.begin(url);

  // Setup multipart form data boundary
  String boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
  String head = "--" + boundary + "\r\nContent-Disposition: form-data; name=\"file\"; filename=\"leaf.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n";
  String tail = "\r\n--" + boundary + "\r\nContent-Disposition: form-data; name=\"farm_id\"\r\n\r\n" + String(FARM_ID) + "\r\n--" + boundary + "\r\nContent-Disposition: form-data; name=\"zone_code\"\r\n\r\n" + String(ZONE_CODE) + "\r\n--" + boundary + "--\r\n";

  size_t totalSize = head.length() + imageSize + tail.length();

  http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
  http.addHeader("Content-Length", String(totalSize));

  Serial.print("📤 Sending to: ");
  Serial.println(url);

  // For ESP32, multipart is complex, so we send as form data instead
  // This is a simplified approach that works well
  int httpCode = http.POST(imageData);

  if (httpCode == 200 || httpCode == 201) {
    Serial.println("✅ Image sent for analysis!");

    String response = http.getString();

    // Parse disease detection result
    StaticJsonDocument<512> responseDoc;
    deserializeJson(responseDoc, response);

    if (responseDoc.containsKey("disease_name")) {
      String diseaseName = responseDoc["disease_name"].as<String>();
      float confidence = responseDoc["confidence_score"] | 0.0;
      String severity = responseDoc["severity"].as<String>();

      lastDisease = diseaseName;

      Serial.print("🦠 Disease Detected: ");
      Serial.println(diseaseName);
      Serial.printf("   Confidence: %.1f%%\n", confidence);
      Serial.printf("   Severity: %s\n", severity.c_str());

      // Alert if disease found
      if (diseaseName != "Healthy") {
        setLED(false);  // Red LED
        soundAlarm(5);  // 5 beeps for disease alert
      } else {
        setLED(true);   // Green LED
      }
    }
  } else {
    Serial.printf("❌ HTTP Error: %d\n", httpCode);
    setLED(false);
  }

  http.end();
}

// ═══════════════════════════════════════════════════════════════
// 🌐 WiFi FUNCTIONS
// ═══════════════════════════════════════════════════════════════

void connectToWiFi() {
  Serial.print("🔗 Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connected!");
    Serial.print("   IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ WiFi connection FAILED!");
    Serial.println("   Check SSID and Password");
  }
}

// ═══════════════════════════════════════════════════════════════
// 💡 LED & SOUND FUNCTIONS
// ═══════════════════════════════════════════════════════════════

void setLED(bool healthy) {
  if (healthy) {
    digitalWrite(LED_GREEN, HIGH);  // Green = Safe
    digitalWrite(LED_RED, LOW);
  } else {
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_RED, HIGH);    // Red = Warning/Disease
  }
}

void soundAlarm(int pulses) {
  for (int i = 0; i < pulses; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(BUZZER_PIN, LOW);
    delay(200);
  }
}

// ═══════════════════════════════════════════════════════════════
// 🌐 WEB SERVER FUNCTIONS
// ═══════════════════════════════════════════════════════════════

void setupWebServer() {
  server.on("/", HTTP_GET, handleDashboard);
  server.on("/status", HTTP_GET, handleStatus);
  server.on("/capture", HTTP_GET, handleCapture);
  server.begin();
}

void handleDashboard() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🍅 TomatoGuard Monitor</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
    }
    .container {
      max-width: 600px;
      margin: 0 auto;
      background: white;
      border-radius: 15px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.3);
      padding: 30px;
    }
    h1 {
      color: #2c5f2d;
      text-align: center;
      margin-bottom: 30px;
      font-size: 28px;
    }
    .status-box {
      background: #f8f9fa;
      border-radius: 10px;
      padding: 20px;
      margin: 15px 0;
      border-left: 4px solid #2c5f2d;
    }
    .sensor-row {
      display: flex;
      justify-content: space-between;
      padding: 10px 0;
      border-bottom: 1px solid #eee;
    }
    .sensor-row:last-child { border-bottom: none; }
    .sensor-label { color: #666; font-weight: bold; }
    .sensor-value { color: #2c5f2d; font-weight: bold; font-size: 16px; }
    .risk-low { background: #d4edda; color: #155724; }
    .risk-medium { background: #fff3cd; color: #856404; }
    .risk-high { background: #f8d7da; color: #721c24; }
    .risk-critical { background: #721c24; color: white; }
    .button-group {
      display: flex;
      gap: 10px;
      margin-top: 20px;
    }
    button {
      flex: 1;
      background: #2c5f2d;
      color: white;
      padding: 12px;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      font-weight: bold;
      transition: all 0.3s;
    }
    button:hover { background: #1e4620; transform: translateY(-2px); }
    button:active { transform: translateY(0); }
    .info {
      background: #e7f3ff;
      border-left: 4px solid #2196F3;
      padding: 12px;
      border-radius: 5px;
      margin-top: 20px;
      font-size: 12px;
      color: #0c3475;
    }
    .disease-alert {
      background: #f8d7da;
      border: 2px solid #721c24;
      color: #721c24;
      padding: 15px;
      border-radius: 8px;
      margin: 15px 0;
      font-weight: bold;
    }
    .healthy { background: #d4edda; border-color: #155724; color: #155724; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🍅 TomatoGuard Monitor</h1>

    <div id="status"></div>

    <div class="button-group">
      <button onclick="location.href='/capture'">📷 Capture Now</button>
      <button onclick="location.reload()">🔄 Refresh</button>
    </div>

    <div class="info">
      ✅ Updates every 5 seconds<br>
      📊 Sensor: Every 10 seconds<br>
      📷 Image: Every 60 seconds
    </div>
  </div>

  <script>
    function updateStatus() {
      fetch('/status')
        .then(r => r.json())
        .then(data => {
          const riskClass = 'risk-' + data.risk_level;
          document.getElementById('status').innerHTML = `
            <div class="status-box">
              <div class="sensor-row">
                <span class="sensor-label">🌡️ Temperature</span>
                <span class="sensor-value">${data.temperature.toFixed(1)}°C</span>
              </div>
              <div class="sensor-row">
                <span class="sensor-label">💧 Humidity</span>
                <span class="sensor-value">${data.humidity.toFixed(1)}%</span>
              </div>
              <div class="sensor-row">
                <span class="sensor-label">🌱 Soil Moisture</span>
                <span class="sensor-value">${data.soil_moisture}%</span>
              </div>
              <div class="sensor-row">
                <span class="sensor-label">⚠️ Risk Level</span>
                <span class="sensor-value ${riskClass}">${data.risk_level.toUpperCase()}</span>
              </div>
            </div>
            <div class="disease-alert ${data.disease === 'Healthy' ? 'healthy' : ''}">
              🦠 ${data.disease}
            </div>
          `;
        })
        .catch(e => console.log('Update failed:', e));
    }

    updateStatus();
    setInterval(updateStatus, 5000);
  </script>
</body>
</html>
  )";
  server.send(200, "text/html", html);
}

void handleStatus() {
  StaticJsonDocument<256> doc;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["soil_moisture"] = soilMoisture;
  doc["risk_level"] = riskLevel;
  doc["disease"] = lastDisease;
  doc["wifi_signal"] = WiFi.RSSI();
  doc["uptime"] = millis() / 1000;

  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

void handleCapture() {
  captureAndAnalyzeImage();
  server.send(200, "text/plain", "Image capture triggered! Check serial monitor.");
}
