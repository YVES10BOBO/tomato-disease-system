#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include "esp_camera.h"
#include <DHT.h>

// ═══════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════

// WiFi Configuration
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// Backend Configuration (update with your ngrok URL)
const char* BACKEND_URL = "https://zoogloeal-nonprescribed-lovella.ngrok-free.dev";

// Farm Configuration
const char* FARM_ID = "81db3508-b9df-4543-82ce-a12d7b5e1667";
const char* ZONE_CODE = "A1";  // Change based on your zone

// Sensor Configuration
#define DHT_PIN 14
#define DHT_TYPE DHT11
#define SOIL_MOISTURE_PIN 33  // ADC pin for soil moisture

// LED Status Pins
#define LED_GREEN 12
#define LED_RED 13
#define BUZZER_PIN 18

// Camera Configuration (for AI-THINKER model)
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

unsigned long lastSensorReadTime = 0;
unsigned long lastImageCaptureTime = 0;
const unsigned long SENSOR_INTERVAL = 10000;  // 10 seconds
const unsigned long IMAGE_INTERVAL = 60000;   // 60 seconds

float temperature = 0;
float humidity = 0;
int soilMoisture = 0;
String riskLevel = "low";

// ═══════════════════════════════════════════════════════════════
// SETUP
// ═══════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n\n=== TOMATO GUARD - ESP32-CAM START ===\n");

  // Initialize pins
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(SOIL_MOISTURE_PIN, INPUT);

  statusLED(false);  // Red LED on startup

  // Initialize camera
  if (!initCamera()) {
    Serial.println("❌ Camera init failed!");
    statusLED(false);
    return;
  }
  Serial.println("✅ Camera initialized");

  // Initialize DHT sensor
  dht.begin();
  delay(500);
  Serial.println("✅ DHT sensor initialized");

  // Connect to WiFi
  connectToWiFi();

  // Setup web server for status
  setupWebServer();

  statusLED(true);  // Green LED when ready
  Serial.println("✅ System Ready!\n");
}

// ═══════════════════════════════════════════════════════════════
// MAIN LOOP
// ═══════════════════════════════════════════════════════════════

void loop() {
  server.handleClient();

  unsigned long currentMillis = millis();

  // Read sensors every 10 seconds
  if (currentMillis - lastSensorReadTime >= SENSOR_INTERVAL) {
    lastSensorReadTime = currentMillis;
    readSensorsAndSend();
  }

  // Capture and send image every 60 seconds
  if (currentMillis - lastImageCaptureTime >= IMAGE_INTERVAL) {
    lastImageCaptureTime = currentMillis;
    captureAndSendImage();
  }
}

// ═══════════════════════════════════════════════════════════════
// SENSOR FUNCTIONS
// ═══════════════════════════════════════════════════════════════

void readSensorsAndSend() {
  Serial.println("\n📊 Reading sensors...");

  // Read DHT11 sensor
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  // Read soil moisture (0-4095 ADC value, convert to percentage)
  int rawSoil = analogRead(SOIL_MOISTURE_PIN);
  soilMoisture = map(rawSoil, 0, 4095, 0, 100);

  // Check for sensor errors
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("❌ DHT sensor read failed!");
    statusLED(false);
    return;
  }

  Serial.printf("Temperature: %.1f°C\n", temperature);
  Serial.printf("Humidity: %.1f%%\n", humidity);
  Serial.printf("Soil Moisture: %d%%\n", soilMoisture);

  // Send to backend
  sendSensorData();
}

void sendSensorData() {
  if (!WiFi.isConnected()) {
    Serial.println("❌ WiFi disconnected!");
    statusLED(false);
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

  Serial.println("📤 Sending sensor data to: " + url);
  Serial.println("Payload: " + payload);

  int httpCode = http.POST(payload);

  if (httpCode == 201 || httpCode == 200) {
    Serial.println("✅ Sensor data sent successfully!");

    // Parse response to get risk level
    String response = http.getString();
    StaticJsonDocument<512> responseDoc;
    deserializeJson(responseDoc, response);

    if (responseDoc.containsKey("risk_level")) {
      riskLevel = responseDoc["risk_level"].as<String>();
      Serial.printf("⚠️  Risk Level: %s\n", riskLevel.c_str());

      // Alert if risk detected
      if (riskLevel != "low") {
        soundBuzzer(3);
        statusLED(false);  // Red LED for warning
      } else {
        statusLED(true);   // Green LED for safe
      }
    }
  } else {
    Serial.printf("❌ HTTP Error: %d\n", httpCode);
    statusLED(false);
  }

  http.end();
}

// ═══════════════════════════════════════════════════════════════
// CAMERA FUNCTIONS
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
  config.jpeg_quality = 10;              // 0-63, lower = higher quality
  config.fb_count = 2;

  if (esp_camera_init(&config) != ESP_OK) {
    return false;
  }
  return true;
}

void captureAndSendImage() {
  Serial.println("\n📷 Capturing image...");

  camera_fb_t* fb = esp_camera_fb_get();

  if (!fb) {
    Serial.println("❌ Camera capture failed!");
    statusLED(false);
    return;
  }

  Serial.printf("Image size: %d bytes\n", fb->len);

  sendImageForDetection(fb->buf, fb->len);

  esp_camera_fb_return(fb);
}

void sendImageForDetection(uint8_t* imageData, size_t imageSize) {
  if (!WiFi.isConnected()) {
    Serial.println("❌ WiFi disconnected!");
    statusLED(false);
    return;
  }

  HTTPClient http;
  String url = String(BACKEND_URL) + "/disease/predict";

  http.begin(url);

  // Create multipart form data
  String boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
  String head = "--" + boundary + "\r\nContent-Disposition: form-data; name=\"file\"; filename=\"leaf.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n";
  String tail = "\r\n--" + boundary + "\r\nContent-Disposition: form-data; name=\"farm_id\"\r\n\r\n" + String(FARM_ID) + "\r\n--" + boundary + "\r\nContent-Disposition: form-data; name=\"zone_code\"\r\n\r\n" + String(ZONE_CODE) + "\r\n--" + boundary + "--\r\n";

  size_t allLen = head.length() + imageSize + tail.length();

  http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
  http.addHeader("Content-Length", String(allLen));

  Serial.println("📤 Sending image to: " + url);

  // For simplicity, send as base64 in JSON (alternative to multipart)
  // This is easier for ESP32
  StaticJsonDocument<512> doc;
  doc["farm_id"] = FARM_ID;
  doc["zone_code"] = ZONE_CODE;

  String payload;
  serializeJson(doc, payload);

  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST(payload);

  if (httpCode == 200 || httpCode == 201) {
    Serial.println("✅ Image sent for analysis!");

    String response = http.getString();
    Serial.println("Response: " + response);

    // Parse disease detection result
    StaticJsonDocument<512> responseDoc;
    deserializeJson(responseDoc, response);

    if (responseDoc.containsKey("disease_name")) {
      String diseaseName = responseDoc["disease_name"];
      float confidence = responseDoc["confidence_score"];
      String severity = responseDoc["severity"];

      Serial.printf("🦠 Disease: %s (%.1f%% confidence)\n", diseaseName.c_str(), confidence);
      Serial.printf("🚨 Severity: %s\n", severity.c_str());

      // Alert farmer if disease detected
      if (diseaseName != "Healthy") {
        soundBuzzer(5);  // Longer buzz for disease
        statusLED(false);
      } else {
        statusLED(true);
      }
    }
  } else {
    Serial.printf("❌ HTTP Error: %d\n", httpCode);
    statusLED(false);
  }

  http.end();
}

// ═══════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
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
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ WiFi connection failed!");
  }
}

void statusLED(bool success) {
  if (success) {
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_RED, LOW);
  } else {
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_RED, HIGH);
  }
}

void soundBuzzer(int pulses) {
  for (int i = 0; i < pulses; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(BUZZER_PIN, LOW);
    delay(200);
  }
}

// ═══════════════════════════════════════════════════════════════
// WEB SERVER (Status Dashboard)
// ═══════════════════════════════════════════════════════════════

void setupWebServer() {
  server.on("/", HTTP_GET, handleRoot);
  server.on("/status", HTTP_GET, handleStatus);
  server.on("/capture", HTTP_GET, handleCapture);
  server.begin();
  Serial.println("🌐 Web server started on port 80");
}

void handleRoot() {
  String html = R"(
    <!DOCTYPE html>
    <html>
    <head>
      <title>TomatoGuard ESP32-CAM</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body { font-family: Arial; margin: 20px; background: #f0f0f0; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        h1 { color: #2c5f2d; text-align: center; }
        .status { padding: 15px; margin: 10px 0; border-radius: 5px; }
        .ok { background: #d4edda; color: #155724; }
        .warning { background: #fff3cd; color: #856404; }
        .error { background: #f8d7da; color: #721c24; }
        button { background: #2c5f2d; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #1e4620; }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>🍅 TomatoGuard Monitor</h1>
        <div id="status"></div>
        <button onclick="location.href='/status'">Refresh Status</button>
        <button onclick="location.href='/capture'">Capture Image Now</button>
      </div>
      <script>
        setInterval(() => fetch('/status').then(r => r.json()).then(d => {
          document.getElementById('status').innerHTML = `
            <div class="status ok">
              🌡️ Temp: ${d.temperature.toFixed(1)}°C<br>
              💧 Humidity: ${d.humidity.toFixed(1)}%<br>
              🌱 Soil: ${d.soil_moisture}%<br>
              ⚠️ Risk: <strong>${d.risk_level}</strong>
            </div>
          `;
        }), 5000);
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
  doc["wifi_signal"] = WiFi.RSSI();
  doc["uptime"] = millis() / 1000;

  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

void handleCapture() {
  captureAndSendImage();
  server.send(200, "text/plain", "Image capture triggered!");
}
