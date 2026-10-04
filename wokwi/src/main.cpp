#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ─── CONFIGURATION ──────────────────────────────────────────
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";

// Using ngrok tunnel for external access
// const char* BACKEND_URL = "https://zoogloeal-nonprescribed-lovella.ngrok-free.dev";
const char* BACKEND_URL = "http://localhost:8000";
const char* FARM_ID = "81db3508-b9df-4543-82ce-a12d7b5e1667";
const unsigned long SEND_INTERVAL = 10000;

// ─── PINS ───────────────────────────────────────────────────
#define DHT_PIN    15
#define DHT_TYPE   DHT22
#define SOIL_PIN   34
#define SDA_PIN    21
#define SCL_PIN    22
#define BUZZER_PIN 18
#define RGB_R      25
#define RGB_G      26
#define RGB_B      27
#define BTN_PIN    4

// ─── OLED ───────────────────────────────────────────────────
Adafruit_SSD1306 oled(128, 64, &Wire, -1);

// ─── GLOBALS ────────────────────────────────────────────────
DHT dht(DHT_PIN, DHT_TYPE);
unsigned long lastSendTime = 0;
bool oledOK = false;

// ─── FUNCTION DECLARATIONS ──────────────────────────────────
void readAndSend();
void showScreen(String l1, String l2, String l3, String l4);
void setColor(int r, int g, int b);
void showRiskColor(String risk);
void buzzAlert(String risk);
void printExpectedRisk(float temp, float hum);

// ─── SETUP ──────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(300);

  pinMode(RGB_R,      OUTPUT);
  pinMode(RGB_G,      OUTPUT);
  pinMode(RGB_B,      OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(BTN_PIN,    INPUT_PULLUP);

  setColor(0, 0, 1);  // Blue = initializing

  dht.begin();
  Wire.begin(SDA_PIN, SCL_PIN);

  oledOK = oled.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  if (!oledOK) {
    Serial.println("[WARN] OLED not found");
  } else {
    showScreen("== TomatoGuard ==", "Univ. of Rwanda", "FYP 2026", "Starting...");
    delay(1500);
  }

  Serial.println("\n============================================");
  Serial.println("  TomatoGuard ESP32 - VS Code Wokwi");
  Serial.println("  University of Rwanda | FYP 2026");
  Serial.println("  Backend: http://localhost:8000");
  Serial.println("============================================");

  if (oledOK) showScreen("Connecting...", "WiFi: Wokwi-GUEST", "", "");

  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 40) {
    delay(500);
    Serial.print(".");
    tries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[OK] WiFi Connected!");
    Serial.print("[OK] IP: "); Serial.println(WiFi.localIP());
    setColor(0, 1, 0);  // Green = ready
    if (oledOK) {
      showScreen("WiFi Connected!", "IP: " + WiFi.localIP().toString(),
                 "Btn=send now", "Auto: 10s");
    }
    delay(2000);
  } else {
    Serial.println("\n[ERROR] WiFi failed!");
    setColor(1, 0, 0);
    if (oledOK) showScreen("WiFi FAILED", "Check Wokwi-GUEST", "", "");
  }

  Serial.println("\nTip: Click DHT22 to set Temp/Humidity.");
  Serial.println("Tip: Turn potentiometer for Soil Moisture.");
  Serial.println("Tip: Press green button to send immediately.");
  Serial.println("============================================\n");
}

// ─── LOOP ───────────────────────────────────────────────────
void loop() {
  if (digitalRead(BTN_PIN) == LOW) {
    Serial.println("[BTN] Manual send triggered!");
    readAndSend();
    delay(500);
    return;
  }

  unsigned long now = millis();
  if (lastSendTime == 0 || (now - lastSendTime) >= SEND_INTERVAL) {
    lastSendTime = now;
    readAndSend();
  }
}

// ─── READ SENSORS + SEND ────────────────────────────────────
void readAndSend() {
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();

  if (isnan(temp) || isnan(hum)) {
    Serial.println("[ERROR] DHT22 failed — click DHT22 to set values");
    if (oledOK) showScreen("DHT22 ERROR", "Click DHT22", "Set Temp & Hum", "");
    return;
  }

  float soil = (analogRead(SOIL_PIN) / 4095.0f) * 100.0f;

  Serial.println("─────────────────────────────────────");
  Serial.print("[SENSOR] Temp : "); Serial.print(temp, 1); Serial.println(" C");
  Serial.print("[SENSOR] Hum  : "); Serial.print(hum, 1);  Serial.println(" %");
  Serial.print("[SENSOR] Soil : "); Serial.print(soil, 1); Serial.println(" %");
  printExpectedRisk(temp, hum);

  if (oledOK) {
    showScreen("Sending...",
               "T:" + String(temp,1) + "C H:" + String(hum,1) + "%",
               "Soil: " + String(soil,1) + "%", "");
  }

  StaticJsonDocument<256> doc;
  doc["farm_id"]       = FARM_ID;
  doc["temperature"]   = temp;
  doc["humidity"]      = hum;
  doc["soil_moisture"] = soil;

  String payload;
  serializeJson(doc, payload);
  Serial.print("[SEND] "); Serial.println(payload);

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WARN] WiFi lost, reconnecting...");
    WiFi.reconnect();
    delay(3000);
    return;
  }

  HTTPClient http;
  String endpoint = String(BACKEND_URL) + "/iot/sensors";
  http.begin(endpoint);
  http.addHeader("ngrok-skip-browser-warning", "true");
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(8000);

  int code = http.POST(payload);

  if (code == 201) {
    StaticJsonDocument<512> res;
    deserializeJson(res, http.getString());

    const char* risk    = res["risk_level"]          | "unknown";
    const char* summary = res["analysis"]["summary"] | "";

    Serial.print("[BACKEND] Risk: "); Serial.println(risk);
    if (strlen(summary) > 0) Serial.println(summary);

    if (oledOK) {
      String l4 = "RISK: " + String(risk);
      l4.toUpperCase();
      showScreen("TomatoGuard FYP",
                 "T:" + String(temp,1) + "C H:" + String(hum,1) + "%",
                 "Soil: " + String(soil,1) + "%", l4);
    }

    showRiskColor(String(risk));
    buzzAlert(String(risk));

  } else if (code > 0) {
    Serial.print("[ERROR] HTTP "); Serial.println(code);
    if (oledOK) showScreen("HTTP ERROR", "Code: " + String(code), "", "");

  } else {
    Serial.println("[ERROR] Cannot reach backend!");
    Serial.println("  Is backend running?  python run.py (port 8000)");
    setColor(1, 0, 0);
    if (oledOK) showScreen("NO CONNECTION", "Run backend:", "uvicorn main:app", "--port 8000");
  }

  http.end();
  Serial.println();
}

// ─── OLED ───────────────────────────────────────────────────
void showScreen(String l1, String l2, String l3, String l4) {
  oled.clearDisplay();
  oled.setTextColor(SSD1306_WHITE);

  oled.fillRect(0, 0, 128, 12, SSD1306_WHITE);
  oled.setTextColor(SSD1306_BLACK);
  oled.setTextSize(1);
  oled.setCursor(2, 2);
  oled.print(l1);
  oled.setTextColor(SSD1306_WHITE);

  oled.setCursor(0, 15); oled.print(l2);
  oled.setCursor(0, 27); oled.print(l3);
  oled.setCursor(0, 48); oled.print(l4);

  oled.display();
}

// ─── RGB LED ────────────────────────────────────────────────
void setColor(int r, int g, int b) {
  digitalWrite(RGB_R, r ? HIGH : LOW);
  digitalWrite(RGB_G, g ? HIGH : LOW);
  digitalWrite(RGB_B, b ? HIGH : LOW);
}

void showRiskColor(String risk) {
  if (risk == "low") {
    setColor(0, 1, 0);
    Serial.println("[RGB] Green — LOW");
  } else if (risk == "medium") {
    setColor(1, 1, 0);
    Serial.println("[RGB] Yellow — MEDIUM");
  } else if (risk == "high") {
    for (int i = 0; i < 3; i++) {
      setColor(1, 0, 0); delay(120);
      setColor(0, 0, 0); delay(120);
    }
    setColor(1, 0, 0);
    Serial.println("[RGB] Red x3 — HIGH");
  } else if (risk == "critical") {
    for (int i = 0; i < 5; i++) {
      setColor(1, 0, 0); delay(70);
      setColor(0, 0, 0); delay(70);
    }
    setColor(1, 0, 0);
    Serial.println("[RGB] Red x5 RAPID — CRITICAL!");
  }
}

// ─── BUZZER ─────────────────────────────────────────────────
void buzzAlert(String risk) {
  if (risk == "high") {
    tone(BUZZER_PIN, 880, 200); delay(350);
    tone(BUZZER_PIN, 880, 200); delay(350);
    Serial.println("[BUZZ] 2 beeps — HIGH");
  } else if (risk == "critical") {
    for (int i = 0; i < 5; i++) {
      tone(BUZZER_PIN, 1200, 130); delay(200);
    }
    Serial.println("[BUZZ] 5 rapid beeps — CRITICAL!");
  }
}

// ─── EXPECTED RISK (mirrors risk.py) ────────────────────────
void printExpectedRisk(float temp, float hum) {
  Serial.print("[EXPECT] ");
  if (temp >= 10 && temp <= 25 && hum >= 90)
    Serial.println("CRITICAL → Late Blight");
  else if (temp >= 24 && temp <= 29 && hum >= 80)
    Serial.println("HIGH → Early Blight");
  else if (temp >= 20 && temp <= 25 && hum >= 70)
    Serial.println("MEDIUM → Septoria");
  else if (temp > 30 && hum < 50)
    Serial.println("MEDIUM → Leaf Curl Virus");
  else if (hum >= 85)
    Serial.println("MEDIUM → High humidity");
  else
    Serial.println("LOW → Safe conditions");
}
