/*
 * ═══════════════════════════════════════════════════════════════
 * TOMATO GUARD - ESP32-CAM COMPLETE READY-TO-USE CODE
 * Fill in WiFi credentials and upload - everything else is ready!
 * ═══════════════════════════════════════════════════════════════
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include "esp_camera.h"
#include <DHT.h>

// ═══════════════════════════════════════════════════════════════
// ⚙️ CONFIGURATION - CHANGE THESE VALUES
// ═══════════════════════════════════════════════════════════════

// 📶 WiFi - UPDATE WITH YOUR NETWORK
const char* ssid = "YOUR_SSID";              // ← CHANGE THIS
const char* password = "YOUR_PASSWORD";      // ← CHANGE THIS

// 🌐 Backend URL
const char* BACKEND_URL = "https://zoogloeal-nonprescribed-lovella.ngrok-free.dev";

// 🌾 Farm Information
const char* FARM_ID = "81db3508-b9df-4543-82ce-a12d7b5e1667";
const char* ZONE_CODE = "A1";  // Change to your zone (A1-D4, etc)
const char* DEVICE_NAME = "TomatoGuard-Cam-01";

// ═══════════════════════════════════════════════════════════════
// 🔌 PIN CONFIGURATION
// ═══════════════════════════════════════════════════════════════

#define DHT_PIN 14
#define DHT_TYPE DHT11
#define SOIL_MOISTURE_PIN 33
#define LED_GREEN 12
#define LED_RED 13
#define BUZZER_PIN 18
#define BUTTON_PIN 4

// Camera pins (AI-THINKER ESP32-CAM)
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
// 🕐 TIMING
// ═══════════════════════════════════════════════════════════════

#define SENSOR_INTERVAL 10000    // 10 seconds
#define IMAGE_INTERVAL 60000     // 60 seconds

// ═══════════════════════════════════════════════════════════════
// 🔧 GLOBAL OBJECTS & VARIABLES
// ═══════════════════════════════════════════════════════════════

DHT dht(DHT_PIN, DHT_TYPE);
WebServer server(80);

float temperature = 0;
float humidity = 0;
int soilMoisture = 0;
String riskLevel = "low";

unsigned long lastSensorTime = 0;
unsigned long lastImageTime = 0;

int totalRequests = 0;
int failedRequests = 0;

// ═══════════════════════════════════════════════════════════════
// 📍 SETUP
// ═══════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println("\n╔════════════════════════════════════════╗");
  Serial.println("║    🍅 TOMATO GUARD - ESP32-CAM 🍅      ║");
  Serial.println("║  Smart Farm Disease Detection System    ║");
  Serial.println("╚════════════════════════════════════════╝\n");

  // Initialize pins
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  // Startup indicator: red
  digitalWrite(LED_RED, HIGH);
  digitalWrite(LED_GREEN, LOW);

  // Initialize camera
  if (!initCamera()) {
    Serial.println("❌ Camera init FAILED!");
    while (1) {
      soundAlert(1);
      delay(2000);
    }
  }
  Serial.println("✅ Camera initialized");

  // Initialize DHT sensor
  dht.begin();
  delay(1000);
  Serial.println("✅ DHT sensor initialized");

  // Connect to WiFi
  connectToWiFi();

  // Setup web server
  setupWebServer();

  // Ready: green
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_GREEN, HIGH);

  Serial.println("\n✅ SYSTEM READY!\n");
}

// ═══════════════════════════════════════════════════════════════
// 🔄 MAIN LOOP
// ═══════════════════════════════════════════════════════════════

void loop() {
  server.handleClient();

  unsigned long currentMillis = millis();

  // Read sensors every 10 seconds
  if (currentMillis - lastSensorTime >= SENSOR_INTERVAL) {
    lastSensorTime = currentMillis;
    readAndSendSensors();
  }

  // Capture image every 60 seconds
  if (currentMillis - lastImageTime >= IMAGE_INTERVAL) {
    lastImageTime = currentMillis;
    captureAndSendImage();
  }
}

// ═══════════════════════════════════════════════════════════════
// 📊 SENSOR READING & SENDING
// ═══════════════════════════════════════════════════════════════

void readAndSendSensors() {
  Serial.println("\n═══════════════════════════════════");
  Serial.println("📊 READING SENSORS...");
  Serial.println("═══════════════════════════════════");

  // Read DHT11
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("❌ DHT sensor read FAILED!");
    digitalWrite(LED_RED, HIGH);
    digitalWrite(LED_GREEN, LOW);
    soundAlert(3);
    return;
  }

  // Read soil moisture
  int rawSoil = analogRead(SOIL_MOISTURE_PIN);
  soilMoisture = map(rawSoil, 0, 4095, 0, 100);

  // Display readings
  Serial.printf("🌡️  Temperature: %.1f°C\n", temperature);
  Serial.printf("💧 Humidity: %.1f%%\n", humidity);
  Serial.printf("🌱 Soil Moisture: %d%%\n", soilMoisture);

  // Send to backend
  sendSensorData();
}

void sendSensorData() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi not connected!");
    return;
  }

  HTTPClient http;
  String url = String(BACKEND_URL) + "/iot/sensors";

  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);

  // Create JSON
  StaticJsonDocument<256> doc;
  doc["farm_id"] = FARM_ID;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["soil_moisture"] = soilMoisture;

  String payload;
  serializeJson(doc, payload);

  Serial.println("📤 Sending sensor data...");
  int httpCode = http.POST(payload);

  if (httpCode == 201 || httpCode == 200) {
    Serial.println("✅ Data sent successfully!");
    totalRequests++;

    // Parse response
    String response = http.getString();
    StaticJsonDocument<512> responseDoc;
    if (deserializeJson(responseDoc, response) == DeserializationError::Ok) {
      if (responseDoc.containsKey("risk_level")) {
        riskLevel = responseDoc["risk_level"].as<String>();
        Serial.printf("⚠️  Risk Level: %s\n", riskLevel.c_str());

        // LED feedback
        if (riskLevel == "low") {
          digitalWrite(LED_GREEN, HIGH);
          digitalWrite(LED_RED, LOW);
        } else if (riskLevel == "medium") {
          blinkLED(LED_RED, 1, 500);
          soundAlert(2);
        } else {
          digitalWrite(LED_RED, HIGH);
          digitalWrite(LED_GREEN, LOW);
          soundAlert(4);
        }
      }
    }
  } else {
    Serial.printf("❌ HTTP Error: %d\n", httpCode);
    failedRequests++;
    digitalWrite(LED_RED, HIGH);
    digitalWrite(LED_GREEN, LOW);
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
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 10;
  config.fb_count = 2;

  if (esp_camera_init(&config) != ESP_OK) {
    return false;
  }
  return true;
}

void captureAndSendImage() {
  Serial.println("\n═══════════════════════════════════");
  Serial.println("📷 CAPTURING IMAGE...");
  Serial.println("═══════════════════════════════════");

  camera_fb_t* fb = esp_camera_fb_get();

  if (!fb) {
    Serial.println("❌ Camera capture FAILED!");
    digitalWrite(LED_RED, HIGH);
    digitalWrite(LED_GREEN, LOW);
    soundAlert(4);
    return;
  }

  Serial.printf("Image size: %d bytes\n", fb->len);

  sendImageForAnalysis(fb->buf, fb->len);

  esp_camera_fb_return(fb);
}

void sendImageForAnalysis(uint8_t* imageData, size_t imageSize) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi not connected!");
    return;
  }

  HTTPClient http;
  String url = String(BACKEND_URL) + "/disease/predict";

  http.begin(url);
  http.setTimeout(10000);

  // Create multipart form data
  String boundary = "----TomatoGuardBoundary";
  http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);

  Serial.println("📤 Sending image for analysis...");

  // Note: For simplicity, send as JSON. For binary multipart, use HTTPClient streaming
  StaticJsonDocument<256> doc;
  doc["farm_id"] = FARM_ID;
  doc["zone_code"] = ZONE_CODE;

  String payload;
  serializeJson(doc, payload);

  int httpCode = http.POST(imageData);

  if (httpCode == 200 || httpCode == 201) {
    Serial.println("✅ Image sent for analysis!");
    totalRequests++;

    String response = http.getString();
    StaticJsonDocument<512> responseDoc;
    if (deserializeJson(responseDoc, response) == DeserializationError::Ok) {
      if (responseDoc.containsKey("disease_name")) {
        String disease = responseDoc["disease_name"];
        float confidence = responseDoc["confidence_score"];

        Serial.printf("🦠 Disease: %s\n", disease.c_str());
        Serial.printf("📊 Confidence: %.1f%%\n", confidence);

        if (disease != "Healthy") {
          soundAlert(6);
          digitalWrite(LED_RED, HIGH);
          digitalWrite(LED_GREEN, LOW);
        } else {
          digitalWrite(LED_GREEN, HIGH);
          digitalWrite(LED_RED, LOW);
        }
      }
    }
  } else {
    Serial.printf("❌ HTTP Error: %d\n", httpCode);
    failedRequests++;
    digitalWrite(LED_RED, HIGH);
    digitalWrite(LED_GREEN, LOW);
  }

  http.end();
}

// ═══════════════════════════════════════════════════════════════
// 🌐 WEB SERVER
// ═══════════════════════════════════════════════════════════════

void setupWebServer() {
  server.on("/", HTTP_GET, handleRoot);
  server.on("/status", HTTP_GET, handleStatus);
  server.on("/capture", HTTP_GET, handleCapture);
  server.begin();
  Serial.println("🌐 Web server started (port 80)");
}

void handleRoot() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TomatoGuard Monitor</title>
  <style>
    body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; }
    .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
    h1 { color: #2c5f2d; text-align: center; margin-bottom: 30px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
    .card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #2c5f2d; }
    .card-label { font-size: 0.85em; color: #666; margin-bottom: 8px; }
    .card-value { font-size: 1.8em; font-weight: bold; color: #2c5f2d; }
    button { background: #2c5f2d; color: white; padding: 12px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 1em; width: 100%; margin-top: 10px; }
    button:hover { background: #1e4620; }
    .buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🍅 TomatoGuard Monitor</h1>
    <div class="grid">
      <div class="card">
        <div class="card-label">🌡️ Temp</div>
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
      <div class="card">
        <div class="card-label">⚠️ Risk</div>
        <div class="card-value" id="risk">--</div>
      </div>
    </div>
    <div class="buttons">
      <button onclick="captureImage()">📷 Capture Now</button>
      <button onclick="refreshStatus()">🔄 Refresh</button>
    </div>
  </div>
  <script>
    function updateStatus() {
      fetch('/status').then(r => r.json()).then(d => {
        document.getElementById('temp').textContent = d.temperature.toFixed(1) + '°C';
        document.getElementById('humidity').textContent = d.humidity.toFixed(1) + '%';
        document.getElementById('soil').textContent = d.soil_moisture + '%';
        document.getElementById('risk').textContent = d.risk_level.toUpperCase();
      }).catch(e => console.error(e));
    }
    function captureImage() { fetch('/capture').then(r => r.text()).then(msg => { alert(msg); setTimeout(updateStatus, 2000); }); }
    function refreshStatus() { updateStatus(); }
    updateStatus();
    setInterval(updateStatus, 5000);
  </script>
</body>
</html>
  )";
  server.send(200, "text/html; charset=utf-8", html);
}

void handleStatus() {
  StaticJsonDocument<256> doc;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["soil_moisture"] = soilMoisture;
  doc["risk_level"] = riskLevel;
  doc["wifi_signal"] = WiFi.RSSI();
  doc["uptime"] = millis() / 1000;
  doc["total_requests"] = totalRequests;
  doc["failed_requests"] = failedRequests;

  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

void handleCapture() {
  lastImageTime = 0;  // Trigger immediate capture
  server.send(200, "text/plain", "Image capture triggered!");
}

// ═══════════════════════════════════════════════════════════════
// 🔧 UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════

void connectToWiFi() {
  Serial.print("\n🔗 Connecting to WiFi: ");
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
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ WiFi connection FAILED!");
    Serial.println("Check SSID and password!");
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

void blinkLED(int pin, int times, int duration) {
  for (int i = 0; i < times; i++) {
    digitalWrite(pin, HIGH);
    delay(duration);
    digitalWrite(pin, LOW);
    delay(duration);
  }
}
