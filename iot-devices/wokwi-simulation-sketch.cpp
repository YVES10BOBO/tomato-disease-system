/*
 * ═══════════════════════════════════════════════════════════════
 * TOMATO GUARD - WOKWI SIMULATOR CODE
 * Virtual Testing Environment
 * ═══════════════════════════════════════════════════════════════
 *
 * Simulates: ESP32-CAM + DHT11 + Soil Moisture Sensor
 * Backend: ngrok tunnel to FastAPI
 * Use this to test without physical hardware
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <math.h>

// ═══════════════════════════════════════════════════════════════
// WOKWI CONFIGURATION
// ═══════════════════════════════════════════════════════════════

// WiFi (use Wokwi's virtual network)
const char* SSID = "Wokwi-GUEST";
const char* PASSWORD = "";

// Backend URL
const char* BACKEND_URL = "https://zoogloeal-nonprescribed-lovella.ngrok-free.dev";

// Farm Configuration
const char* FARM_ID = "81db3508-b9df-4543-82ce-a12d7b5e1667";
const char* ZONE_CODE = "A1";
const char* DEVICE_NAME = "WokwiSimulator-01";

// Sensor pins (Wokwi virtual pins)
#define DHT_PIN 15
#define DHT_TYPE DHT22
#define SOIL_MOISTURE_PIN 34  // ADC pin

// Status pins
#define LED_RED 25
#define LED_GREEN 26
#define BUZZER_PIN 18
#define BUTTON_PIN 4

// OLED Display (I2C)
#define OLED_SDA 21
#define OLED_SCL 22

// ═══════════════════════════════════════════════════════════════
// GLOBAL VARIABLES
// ═══════════════════════════════════════════════════════════════

DHT dht(DHT_PIN, DHT_TYPE);

// Sensor readings
float temperature = 0;
float humidity = 0;
int soilMoisture = 0;
String riskLevel = "low";

// Simulation variables
unsigned long lastSensorTime = 0;
unsigned long lastImageTime = 0;
const unsigned long SENSOR_INTERVAL = 10000;  // 10 seconds
const unsigned long IMAGE_INTERVAL = 60000;   // 60 seconds

// Simulated sensor data (realistic ranges)
float tempMin = 18.0, tempMax = 32.0;
float humidityMin = 40.0, humidityMax = 95.0;
int soilMin = 20, soilMax = 85;

// ═══════════════════════════════════════════════════════════════
// SETUP
// ═══════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n╔════════════════════════════════════════╗");
  Serial.println("║    WOKWI SIMULATOR - TomatoGuard      ║");
  Serial.println("║      Virtual Testing Environment      ║");
  Serial.println("╚════════════════════════════════════════╝\n");

  // Initialize pins
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Status LED: startup (red)
  digitalWrite(LED_RED, HIGH);
  digitalWrite(LED_GREEN, LOW);

  // Initialize DHT sensor (in simulation, it will always work)
  dht.begin();
  delay(500);
  Serial.println("✅ DHT22 sensor initialized");

  // Connect to Wokwi WiFi
  connectToWiFi();

  // Ready status (green)
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_GREEN, HIGH);

  Serial.println("✅ System Ready!");
  Serial.println("\n📊 Starting sensor loop...\n");
}

// ═══════════════════════════════════════════════════════════════
// MAIN LOOP
// ═══════════════════════════════════════════════════════════════

void loop() {
  unsigned long currentMillis = millis();

  // Read and send sensor data
  if (currentMillis - lastSensorTime >= SENSOR_INTERVAL) {
    lastSensorTime = currentMillis;
    readAndSendSensors();
  }

  // Simulate image capture
  if (currentMillis - lastImageTime >= IMAGE_INTERVAL) {
    lastImageTime = currentMillis;
    simulateImageCapture();
  }

  // Check button
  if (digitalRead(BUTTON_PIN) == LOW) {
    delay(200);
    Serial.println("\n🔘 Button pressed - manual capture!");
    simulateImageCapture();
    delay(500);
  }

  delay(100);
}

// ═══════════════════════════════════════════════════════════════
// SENSOR SIMULATION
// ═══════════════════════════════════════════════════════════════

void readAndSendSensors() {
  Serial.println("\n═══ SENSOR READING ═══");

  // Read DHT22 (or use simulated values)
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  // If sensor read fails, use simulated values
  if (isnan(temperature) || isnan(humidity)) {
    temperature = simulateTemperature();
    humidity = simulateHumidity();
    Serial.println("⚠️  Using simulated sensor values");
  }

  // Read soil moisture
  int rawSoil = analogRead(SOIL_MOISTURE_PIN);
  soilMoisture = map(rawSoil, 0, 4095, 0, 100);

  // If value is unrealistic, simulate
  if (soilMoisture < 0 || soilMoisture > 100) {
    soilMoisture = simulateSoilMoisture();
  }

  // Display readings
  Serial.printf("🌡️  Temperature: %.1f°C\n", temperature);
  Serial.printf("💧 Humidity: %.1f%%\n", humidity);
  Serial.printf("🌱 Soil Moisture: %d%%\n", soilMoisture);

  // Send to backend
  sendSensorData();

  // Update display
  updateStatusLED();
}

float simulateTemperature() {
  // Simulate temperature variation (sine wave for realistic pattern)
  float timeOfDay = (millis() / 1000.0) / 3600.0;  // Hours (scaled)
  float variation = 7.0 * sin(timeOfDay * 2 * PI / 24.0);
  return 25.0 + variation + random(-5, 5) / 10.0;
}

float simulateHumidity() {
  // Inverse of temperature (typically)
  float variation = -5.0 * sin(millis() / 1000.0 / 3600.0 * 2 * PI / 24.0);
  return 65.0 + variation + random(-10, 10) / 10.0;
}

int simulateSoilMoisture() {
  // Gradual decrease (simulating drying soil)
  int baseSoil = 70 - (millis() / 600000);  // Decreases over time
  return constrain(baseSoil + random(-5, 5), 20, 85);
}

void sendSensorData() {
  HTTPClient http;
  String url = String(BACKEND_URL) + "/iot/sensors";

  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);

  // Create JSON payload
  StaticJsonDocument<256> doc;
  doc["farm_id"] = FARM_ID;
  doc["temperature"] = round(temperature * 10.0) / 10.0;
  doc["humidity"] = round(humidity * 10.0) / 10.0;
  doc["soil_moisture"] = soilMoisture;

  String payload;
  serializeJson(doc, payload);

  Serial.println("📤 Sending to backend...");

  int httpCode = http.POST(payload);

  if (httpCode == 201 || httpCode == 200) {
    Serial.println("✅ Data sent successfully!");

    // Parse response
    String response = http.getString();
    StaticJsonDocument<256> responseDoc;
    if (deserializeJson(responseDoc, response) == DeserializationError::Ok) {
      if (responseDoc.containsKey("risk_level")) {
        riskLevel = responseDoc["risk_level"].as<String>();
        Serial.printf("⚠️  Risk Level: %s\n", riskLevel.c_str());
      }
    }
  } else {
    Serial.printf("❌ HTTP Error: %d\n", httpCode);
  }

  http.end();
}

// ═══════════════════════════════════════════════════════════════
// IMAGE SIMULATION
// ═══════════════════════════════════════════════════════════════

void simulateImageCapture() {
  Serial.println("\n═══ IMAGE CAPTURE (SIMULATED) ═══");
  Serial.println("📷 Capturing image from virtual camera...");

  // Simulate capture delay
  delay(500);

  int imageSize = random(8000, 12000);
  Serial.printf("Image size: %d bytes\n", imageSize);

  // Send simulated image data
  sendSimulatedImage();
}

void sendSimulatedImage() {
  HTTPClient http;
  String url = String(BACKEND_URL) + "/disease/predict";

  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);

  // In simulator, send a simple JSON request instead of binary data
  StaticJsonDocument<256> doc;
  doc["farm_id"] = FARM_ID;
  doc["zone_code"] = ZONE_CODE;
  doc["simulated"] = true;

  String payload;
  serializeJson(doc, payload);

  Serial.println("📤 Sending simulated image...");

  int httpCode = http.POST(payload);

  if (httpCode == 200 || httpCode == 201) {
    Serial.println("✅ Image processed!");

    String response = http.getString();
    StaticJsonDocument<256> responseDoc;
    if (deserializeJson(responseDoc, response) == DeserializationError::Ok) {
      if (responseDoc.containsKey("disease_name")) {
        String diseaseName = responseDoc["disease_name"];
        Serial.printf("🦠 Result: %s\n", diseaseName.c_str());

        // Alert if disease detected
        if (diseaseName != "Healthy") {
          soundBuzzer(6);
          blinkLED(LED_RED, 3, 200);
        } else {
          digitalWrite(LED_GREEN, HIGH);
        }
      }
    }
  } else {
    Serial.printf("❌ HTTP Error: %d\n", httpCode);
  }

  http.end();
}

// ═══════════════════════════════════════════════════════════════
// STATUS INDICATORS
// ═══════════════════════════════════════════════════════════════

void updateStatusLED() {
  if (riskLevel == "low") {
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_RED, LOW);
  } else if (riskLevel == "medium") {
    blinkLED(LED_RED, 1, 500);
    soundBuzzer(2);
  } else if (riskLevel == "high" || riskLevel == "critical") {
    digitalWrite(LED_RED, HIGH);
    digitalWrite(LED_GREEN, LOW);
    soundBuzzer(3);
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

void soundBuzzer(int beeps) {
  for (int i = 0; i < beeps; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(100);
    digitalWrite(BUZZER_PIN, LOW);
    delay(100);
  }
}

// ═══════════════════════════════════════════════════════════════
// WIFI
// ═══════════════════════════════════════════════════════════════

void connectToWiFi() {
  Serial.print("🔗 Connecting to WiFi: ");
  Serial.println(SSID);

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
  } else {
    Serial.println("\n⚠️  WiFi simulation mode active");
  }
}

// ═══════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════

float constrain(float value, float minVal, float maxVal) {
  if (value < minVal) return minVal;
  if (value > maxVal) return maxVal;
  return value;
}
