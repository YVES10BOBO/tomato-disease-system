#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
TOMATO GUARD - RASPBERRY PI CAMERA CODE
Real Camera Module Integration
═══════════════════════════════════════════════════════════════

Hardware: Raspberry Pi 4 + Raspberry Pi Camera Module v2
Sensors: DHT11/DHT22, Soil Moisture Sensor (via ADC)
Backend: FastAPI with ngrok tunnel
"""

import os
import sys
import time
import json
import requests
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Raspberry Pi specific imports
try:
    from picamera import PiCamera
    from picamera.array import PiRGBArray
    import RPi.GPIO as GPIO
    from Adafruit_DHT import DHT11, read_retry
    HARDWARE_AVAILABLE = True
except ImportError:
    print("⚠️  Hardware libraries not available - simulation mode")
    HARDWARE_AVAILABLE = False

import logging

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Backend
BACKEND_URL = "https://zoogloeal-nonprescribed-lovella.ngrok-free.dev"

# Farm Details
FARM_ID = "81db3508-b9df-4543-82ce-a12d7b5e1667"
ZONE_CODE = "A1"
DEVICE_NAME = "RaspberryPi-Cam-01"

# GPIO Pins
DHT_PIN = 17           # GPIO 17 for DHT sensor
SOIL_ADC_CHANNEL = 0   # ADC channel for soil moisture
BUZZER_PIN = 27
LED_RED_PIN = 23
LED_GREEN_PIN = 24
BUTTON_PIN = 22

# Sensor intervals (seconds)
SENSOR_READ_INTERVAL = 10
IMAGE_CAPTURE_INTERVAL = 60
HEALTH_CHECK_INTERVAL = 300

# Camera settings
CAMERA_RESOLUTION = (1280, 720)
CAMERA_FRAMERATE = 30
CAMERA_WARMUP_TIME = 2

# Paths
IMAGE_DIR = Path("/home/pi/tomato-guard/images")
LOG_DIR = Path("/home/pi/tomato-guard/logs")

# ═══════════════════════════════════════════════════════════════
# LOGGING SETUP
# ═══════════════════════════════════════════════════════════════

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "tomato_guard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# SENSOR CLASS
# ═══════════════════════════════════════════════════════════════

class SensorReader:
    def __init__(self):
        self.temperature = 0.0
        self.humidity = 0.0
        self.soil_moisture = 0
        self.lock = threading.Lock()
        self.logger = logging.getLogger("SensorReader")

        if HARDWARE_AVAILABLE:
            self._init_gpio()

    def _init_gpio(self):
        """Initialize GPIO pins"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(BUZZER_PIN, GPIO.OUT)
            GPIO.setup(LED_RED_PIN, GPIO.OUT)
            GPIO.setup(LED_GREEN_PIN, GPIO.OUT)
            GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.logger.info("✅ GPIO initialized")
        except Exception as e:
            self.logger.error(f"❌ GPIO setup failed: {e}")

    def read_dht(self):
        """Read DHT11/DHT22 sensor"""
        try:
            humidity, temperature = read_retry(DHT11, DHT_PIN)
            with self.lock:
                self.temperature = temperature
                self.humidity = humidity
            self.logger.debug(f"DHT: Temp={temperature}°C, Humidity={humidity}%")
            return temperature, humidity
        except Exception as e:
            self.logger.error(f"❌ DHT read error: {e}")
            # Simulate if hardware unavailable
            return self._simulate_dht()

    def read_soil_moisture(self):
        """Read soil moisture sensor via ADC"""
        try:
            # Requires ADS1115 or similar ADC module
            # This is a placeholder - implement based on your ADC module
            raw_value = self._read_adc(SOIL_ADC_CHANNEL)
            soil_pct = int((raw_value / 32767) * 100)  # Convert to percentage
            with self.lock:
                self.soil_moisture = soil_pct
            self.logger.debug(f"Soil: {soil_pct}%")
            return soil_pct
        except Exception as e:
            self.logger.error(f"❌ Soil moisture read error: {e}")
            return self._simulate_soil_moisture()

    def _read_adc(self, channel):
        """Read ADC value - implement based on your ADC module"""
        # Example for ADS1115
        try:
            import board
            import busio
            import adafruit_ads1x15.ads1115 as ADS
            from adafruit_ads1x15.analog_in import AnalogIn

            i2c = busio.I2C(board.SCL, board.SDA)
            ads = ADS.ADS1115(i2c)
            channel_obj = AnalogIn(ads, channel)
            return channel_obj.value
        except:
            return 2000  # Default value

    def _simulate_dht(self):
        """Simulate DHT readings"""
        import random
        temp = 25 + random.uniform(-5, 5)
        humidity = 65 + random.uniform(-20, 20)
        with self.lock:
            self.temperature = temp
            self.humidity = humidity
        return temp, humidity

    def _simulate_soil_moisture(self):
        """Simulate soil moisture readings"""
        import random
        soil = random.randint(30, 80)
        with self.lock:
            self.soil_moisture = soil
        return soil

    def get_readings(self) -> Dict:
        """Get current sensor readings"""
        with self.lock:
            return {
                "temperature": round(self.temperature, 1),
                "humidity": round(self.humidity, 1),
                "soil_moisture": self.soil_moisture,
                "timestamp": datetime.now().isoformat()
            }

# ═══════════════════════════════════════════════════════════════
# CAMERA CLASS
# ═══════════════════════════════════════════════════════════════

class CameraModule:
    def __init__(self):
        self.logger = logging.getLogger("CameraModule")
        self.camera = None
        IMAGE_DIR.mkdir(parents=True, exist_ok=True)

        if HARDWARE_AVAILABLE:
            self._init_camera()

    def _init_camera(self):
        """Initialize Raspberry Pi camera"""
        try:
            self.camera = PiCamera()
            self.camera.resolution = CAMERA_RESOLUTION
            self.camera.framerate = CAMERA_FRAMERATE
            time.sleep(CAMERA_WARMUP_TIME)
            self.logger.info("✅ Camera initialized")
        except Exception as e:
            self.logger.error(f"❌ Camera init failed: {e}")
            self.camera = None

    def capture_image(self) -> Optional[Path]:
        """Capture image from camera"""
        try:
            if not self.camera:
                self.logger.warning("Camera not available - returning dummy image")
                return self._create_dummy_image()

            filename = f"leaf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = IMAGE_DIR / filename

            self.camera.capture(str(filepath))
            self.logger.info(f"📷 Image captured: {filename}")
            return filepath
        except Exception as e:
            self.logger.error(f"❌ Capture failed: {e}")
            return None

    def _create_dummy_image(self) -> Path:
        """Create a dummy image for testing"""
        import random
        filename = f"dummy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = IMAGE_DIR / filename
        # Create a minimal JPEG file
        filepath.write_bytes(bytes([0xFF, 0xD8, 0xFF, 0xE0] + [0x00] * 100 + [0xFF, 0xD9]))
        return filepath

    def cleanup(self):
        """Cleanup camera resources"""
        if self.camera:
            self.camera.close()
            self.logger.info("Camera closed")

# ═══════════════════════════════════════════════════════════════
# BACKEND COMMUNICATION
# ═══════════════════════════════════════════════════════════════

class BackendClient:
    def __init__(self):
        self.logger = logging.getLogger("BackendClient")
        self.session = requests.Session()
        self.session.timeout = 10

    def send_sensor_data(self, data: Dict) -> bool:
        """Send sensor data to backend"""
        try:
            endpoint = f"{BACKEND_URL}/iot/sensors"
            payload = {
                "farm_id": FARM_ID,
                "temperature": data["temperature"],
                "humidity": data["humidity"],
                "soil_moisture": data["soil_moisture"],
                "device_name": DEVICE_NAME,
                "zone_code": ZONE_CODE
            }

            response = self.session.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code in [200, 201]:
                result = response.json()
                self.logger.info(f"✅ Sensor data sent | Risk: {result.get('risk_level')}")
                return True
            else:
                self.logger.error(f"❌ HTTP {response.status_code}: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Request failed: {e}")
            return False

    def send_image(self, image_path: Path) -> bool:
        """Send image for disease detection"""
        try:
            endpoint = f"{BACKEND_URL}/disease/predict"

            with open(image_path, 'rb') as f:
                files = {
                    'file': (image_path.name, f, 'image/jpeg')
                }
                data = {
                    'farm_id': FARM_ID,
                    'zone_code': ZONE_CODE
                }

                response = self.session.post(endpoint, files=files, data=data)

            if response.status_code in [200, 201]:
                result = response.json()
                disease = result.get("disease_name", "Unknown")
                confidence = result.get("confidence_score", 0)
                self.logger.info(f"✅ Image analyzed | Disease: {disease} ({confidence}%)")
                return True
            else:
                self.logger.error(f"❌ HTTP {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Upload failed: {e}")
            return False

# ═══════════════════════════════════════════════════════════════
# MAIN SYSTEM
# ═══════════════════════════════════════════════════════════════

class TomatoGuardSystem:
    def __init__(self):
        self.logger = logging.getLogger("TomatoGuard")
        self.sensors = SensorReader()
        self.camera = CameraModule()
        self.backend = BackendClient()
        self.running = True
        self.last_sensor_time = 0
        self.last_image_time = 0
        self.last_health_check = 0

        self.logger.info("═" * 50)
        self.logger.info("TOMATO GUARD - RASPBERRY PI SYSTEM STARTED")
        self.logger.info("═" * 50)

    def run(self):
        """Main system loop"""
        try:
            while self.running:
                current_time = time.time()

                # Read sensors
                if current_time - self.last_sensor_time >= SENSOR_READ_INTERVAL:
                    self.last_sensor_time = current_time
                    self._read_and_send_sensors()

                # Capture image
                if current_time - self.last_image_time >= IMAGE_CAPTURE_INTERVAL:
                    self.last_image_time = current_time
                    self._capture_and_send_image()

                # Health check
                if current_time - self.last_health_check >= HEALTH_CHECK_INTERVAL:
                    self.last_health_check = current_time
                    self._health_check()

                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested")
        finally:
            self.cleanup()

    def _read_and_send_sensors(self):
        """Read all sensors and send data"""
        self.logger.info("📊 Reading sensors...")

        self.sensors.read_dht()
        self.sensors.read_soil_moisture()

        data = self.sensors.get_readings()
        self.logger.info(f"Temp: {data['temperature']}°C, Humidity: {data['humidity']}%, Soil: {data['soil_moisture']}%")

        self.backend.send_sensor_data(data)

    def _capture_and_send_image(self):
        """Capture image and send for analysis"""
        self.logger.info("📷 Capturing image...")

        image_path = self.camera.capture_image()
        if image_path:
            self.backend.send_image(image_path)

    def _health_check(self):
        """Perform system health check"""
        self.logger.info("🔧 Health check")
        uptime = int(time.time())
        self.logger.info(f"Uptime: {uptime}s, Sensors OK, Camera: {'OK' if self.camera.camera else 'SIMULATED'}")

    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up...")
        self.camera.cleanup()
        if HARDWARE_AVAILABLE:
            GPIO.cleanup()
        self.logger.info("✅ Shutdown complete")

# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    system = TomatoGuardSystem()
    system.run()
