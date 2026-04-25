#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// ─── WiFi (Wokwi virtual WiFi) ───────────────────────────────
#define WIFI_SSID "Wokwi-GUEST"
#define WIFI_PASS ""

// ─── Backend URL (ngrok) ─────────────────────────────────────
#define BACKEND_URL "https://zoogloeal-nonprescribed-lovella.ngrok-free.dev"
#define FARM_ID     "81db3508-b9df-4543-82ce-a12d7b5e1667"

// ─── Sensor Pins ─────────────────────────────────────────────
#define DHT_PIN     15
#define DHT_TYPE    DHT22
#define SOIL_PIN    34

// ─── Send interval (30 seconds) ──────────────────────────────
#define INTERVAL_MS 30000

DHT dht(DHT_PIN, DHT_TYPE);
unsigned long lastSend = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();

  Serial.println("\n========================================");
  Serial.println("  TomatoGuard ESP32 IoT Node");
  Serial.println("  University of Rwanda FYP 2026");
  Serial.println("========================================");

  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
  Serial.println("========================================\n");
}

void loop() {
  unsigned long now = millis();
  if (now - lastSend >= INTERVAL_MS || lastSend == 0) {
    lastSend = now;
    sendSensorData();
  }
}

void sendSensorData() {
  float temperature = dht.readTemperature();
  float humidity    = dht.readHumidity();

  // Soil moisture: convert analog 0-4095 to percentage 0-100
  int soilRaw      = analogRead(SOIL_PIN);
  float soilMoisture = map(soilRaw, 4095, 0, 0, 100);

  // Validate readings
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("[ERROR] Failed to read DHT22 sensor!");
    return;
  }

  Serial.println("─────────────────────────────────────");
  Serial.print("[SENSOR] Temperature : "); Serial.print(temperature); Serial.println(" °C");
  Serial.print("[SENSOR] Humidity    : "); Serial.print(humidity);    Serial.println(" %");
  Serial.print("[SENSOR] Soil Moisture: "); Serial.print(soilMoisture); Serial.println(" %");

  // Build JSON
  StaticJsonDocument<256> doc;
  doc["farm_id"]      = FARM_ID;
  doc["temperature"]  = temperature;
  doc["humidity"]     = humidity;
  doc["soil_moisture"] = soilMoisture;

  String payload;
  serializeJson(doc, payload);

  // Send HTTP POST
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(BACKEND_URL "/iot/sensors");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("ngrok-skip-browser-warning", "true");

    int responseCode = http.POST(payload);

    if (responseCode > 0) {
      String response = http.getString();
      Serial.print("[HTTP] Response code: "); Serial.println(responseCode);

      StaticJsonDocument<512> res;
      deserializeJson(res, response);
      const char* risk = res["risk_level"] | "unknown";
      Serial.print("[BACKEND] Risk Level: "); Serial.println(risk);
    } else {
      Serial.print("[HTTP] Error: "); Serial.println(responseCode);
    }
    http.end();
  } else {
    Serial.println("[WiFi] Not connected!");
  }
}
