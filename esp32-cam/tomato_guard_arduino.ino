#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"
#include <ArduinoJson.h>

// ═════════════════════════════════════════════════════════════
// 🔴 UPDATE ONLY THESE 4 VALUES
// ═════════════════════════════════════════════════════════════

const char* ssid = "dtechel_hub";
const char* password = "6473@develisa";
const char* BACKEND_URL = "http://192.168.1.102:8000";  // Your local backend
const char* FARM_ID = "81db3508-b9df-4543-82ce-a12d7b5e1667";

// ═════════════════════════════════════════════════════════════
// DHT11 SENSOR
// ═════════════════════════════════════════════════════════════

#define DHTPIN 14
#define DHTTYPE DHT11
#define SOIL_MOISTURE_PIN 33  // Add soil moisture if available

DHT dht(DHTPIN, DHTTYPE);

// ═════════════════════════════════════════════════════════════
// CAMERA PINS (AI Thinker)
// ═════════════════════════════════════════════════════════════

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

#define LED_RED 12
#define LED_GREEN 13

// ═════════════════════════════════════════════════════════════
// GLOBALS
// ═════════════════════════════════════════════════════════════

unsigned long lastSensorTime = 0;
unsigned long lastImageTime = 0;
const unsigned long SENSOR_INTERVAL = 10000;   // 10 seconds
const unsigned long IMAGE_INTERVAL = 60000;    // 60 seconds
const char* ZONE_CODE = "A1";

// ═════════════════════════════════════════════════════════════
// SETUP CAMERA
// ═════════════════════════════════════════════════════════════

void startCamera() {
  camera_config_t config;

  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;

  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size   = FRAMESIZE_VGA;
  config.jpeg_quality = 10;
  config.fb_count     = 1;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("❌ Camera init failed");
    digitalWrite(LED_RED, HIGH);
    return;
  }
  Serial.println("✅ Camera initialized");
}

// ═════════════════════════════════════════════════════════════
// SEND SENSOR DATA TO BACKEND
// ═════════════════════════════════════════════════════════════

void sendSensorData() {
  // Read DHT11
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("❌ Failed to read DHT11!");
    humidity = 0;
    temperature = 0;
  }

  // Read soil moisture (optional)
  int soilMoisture = 0;
  soilMoisture = map(analogRead(SOIL_MOISTURE_PIN), 0, 4095, 0, 100);

  Serial.println("\n📊 SENSOR DATA:");
  Serial.print("   Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");
  Serial.print("   Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");
  Serial.print("   Soil Moisture: ");
  Serial.print(soilMoisture);
  Serial.println(" %");

  // Create JSON
  StaticJsonDocument<256> doc;
  doc["farm_id"] = FARM_ID;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["soil_moisture"] = soilMoisture;

  String jsonData;
  serializeJson(doc, jsonData);

  // Send to backend
  WiFiClient client;
  HTTPClient http;

  String url = String(BACKEND_URL) + "/iot/sensors";
  http.begin(client, url);
  http.addHeader("Content-Type", "application/json");

  Serial.print("📤 Sending to: ");
  Serial.println(url);

  int httpCode = http.POST(jsonData);

  if (httpCode == 200 || httpCode == 201) {
    Serial.println("✅ Sensor data sent successfully!");

    // Parse response
    String response = http.getString();
    StaticJsonDocument<512> responseDoc;
    deserializeJson(responseDoc, response);

    if (responseDoc.containsKey("risk_level")) {
      String riskLevel = responseDoc["risk_level"].as<String>();
      Serial.print("⚠️  Risk Level: ");
      Serial.println(riskLevel);

      // LED feedback
      if (riskLevel == "low") {
        digitalWrite(LED_GREEN, HIGH);
        digitalWrite(LED_RED, LOW);
      } else {
        digitalWrite(LED_GREEN, LOW);
        digitalWrite(LED_RED, HIGH);
      }
    }
  } else {
    Serial.print("❌ HTTP Error: ");
    Serial.println(httpCode);
    digitalWrite(LED_RED, HIGH);
    digitalWrite(LED_GREEN, LOW);
  }

  http.end();
}

// ═════════════════════════════════════════════════════════════
// SEND IMAGE FOR DISEASE DETECTION
// ═════════════════════════════════════════════════════════════

void sendImage() {
  Serial.println("\n📷 CAPTURING IMAGE...");

  camera_fb_t *fb = esp_camera_fb_get();

  if (!fb) {
    Serial.println("❌ Camera capture failed");
    digitalWrite(LED_RED, HIGH);
    return;
  }

  Serial.print("   Image size: ");
  Serial.print(fb->len);
  Serial.println(" bytes");

  WiFiClient client;
  HTTPClient http;

  String url = String(BACKEND_URL) + "/disease/predict";
  http.begin(client, url);

  String boundary = "----ESP32FormBoundary";

  // Build form data
  String head = "--" + boundary + "\r\n";
  head += "Content-Disposition: form-data; name=\"farm_id\"\r\n\r\n";
  head += String(FARM_ID) + "\r\n";

  head += "--" + boundary + "\r\n";
  head += "Content-Disposition: form-data; name=\"zone_code\"\r\n\r\n";
  head += String(ZONE_CODE) + "\r\n";

  head += "--" + boundary + "\r\n";
  head += "Content-Disposition: form-data; name=\"file\"; filename=\"leaf.jpg\"\r\n";
  head += "Content-Type: image/jpeg\r\n\r\n";

  String tail = "\r\n--" + boundary + "--\r\n";

  int totalLen = head.length() + fb->len + tail.length();

  http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
  http.addHeader("Content-Length", String(totalLen));

  // Allocate memory for multipart data
  uint8_t *postData = (uint8_t *)malloc(totalLen);

  if (!postData) {
    Serial.println("❌ Memory allocation failed!");
    esp_camera_fb_return(fb);
    http.end();
    return;
  }

  // Copy data
  memcpy(postData, head.c_str(), head.length());
  memcpy(postData + head.length(), fb->buf, fb->len);
  memcpy(postData + head.length() + fb->len, tail.c_str(), tail.length());

  Serial.print("📤 Sending to: ");
  Serial.println(url);

  int httpResponseCode = http.POST(postData, totalLen);

  if (httpResponseCode == 200 || httpResponseCode == 201) {
    Serial.println("✅ Image sent for analysis!");

    String response = http.getString();
    Serial.println("📋 Response:");
    Serial.println(response);

    // ═══════════════════════════════════════════════════
    // PARSE DISEASE DETECTION RESULT
    // ═══════════════════════════════════════════════════

    StaticJsonDocument<512> responseDoc;
    deserializeJson(responseDoc, response);

    if (responseDoc.containsKey("disease_name")) {
      String diseaseName = responseDoc["disease_name"].as<String>();
      float confidence = responseDoc["confidence_score"] | 0.0;
      String severity = responseDoc["severity"].as<String>();

      Serial.println("\n🦠 DETECTION RESULT:");
      Serial.print("   Disease: ");
      Serial.println(diseaseName);
      Serial.print("   Confidence: ");
      Serial.print(confidence);
      Serial.println("%");
      Serial.print("   Severity: ");
      Serial.println(severity);

      // LED feedback based on result
      if (diseaseName == "Healthy") {
        Serial.println("   ✅ HEALTHY TOMATO");
        digitalWrite(LED_GREEN, HIGH);
        digitalWrite(LED_RED, LOW);
      } else {
        Serial.println("   ⚠️ DISEASE DETECTED");
        digitalWrite(LED_RED, HIGH);
        digitalWrite(LED_GREEN, LOW);
      }
    }

  } else {
    Serial.print("❌ HTTP Error: ");
    Serial.println(httpResponseCode);
    digitalWrite(LED_RED, HIGH);
    digitalWrite(LED_GREEN, LOW);
  }

  free(postData);
  http.end();
  esp_camera_fb_return(fb);
}

// ═════════════════════════════════════════════════════════════
// SETUP
// ═════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n╔═══════════════════════════════════════╗");
  Serial.println("║  🍅 TOMATO GUARD STARTING             ║");
  Serial.println("╚═══════════════════════════════════════╝\n");

  // Initialize pins
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(SOIL_MOISTURE_PIN, INPUT);

  digitalWrite(LED_RED, HIGH);   // Red = starting
  digitalWrite(LED_GREEN, LOW);

  // Initialize DHT
  dht.begin();
  delay(500);
  Serial.println("✅ DHT11 initialized");

  // Initialize camera
  startCamera();

  // Connect WiFi
  Serial.print("🔗 Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connected!");
    Serial.print("   IP: ");
    Serial.println(WiFi.localIP());

    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_RED, LOW);
  } else {
    Serial.println("\n❌ WiFi connection failed!");
    digitalWrite(LED_RED, HIGH);
  }

  Serial.println("\n╔═══════════════════════════════════════╗");
  Serial.println("║  ✅ SYSTEM READY - MONITORING ACTIVE  ║");
  Serial.println("╚═══════════════════════════════════════╝\n");
}

// ═════════════════════════════════════════════════════════════
// MAIN LOOP
// ═════════════════════════════════════════════════════════════

void loop() {
  unsigned long currentTime = millis();

  // Send sensor data every 10 seconds
  if (currentTime - lastSensorTime >= SENSOR_INTERVAL) {
    lastSensorTime = currentTime;
    sendSensorData();
  }

  // Send image every 60 seconds
  if (currentTime - lastImageTime >= IMAGE_INTERVAL) {
    lastImageTime = currentTime;
    sendImage();
  }

  delay(100);  // Small delay to prevent watchdog timeout
}
