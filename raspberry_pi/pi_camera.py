"""
Raspberry Pi Fixed Camera — Autonomous tomato zone scanner
TomatoGuard — University of Rwanda Final Year Project 2026

This is the in-farm camera node. It runs continuously on a Raspberry Pi 4
with the HQ Camera module mounted centrally on the farm and:

  1. Logs in to the backend to obtain a JWT token.
  2. For every farm zone (A1..D4), captures an image and uploads it to the
     /disease/predict endpoint, where the two-stage AI pipeline
     (leaf validator -> disease classifier) runs and stores any detection.
  3. After each full sweep, asks the backend for the recommended scan
     interval (which adapts to the current IoT risk level) and sleeps.

Camera source is auto-detected:
  - Raspberry Pi HQ Camera via picamera2 (real deployment)
  - USB / webcam via OpenCV (fallback)
  - A sample image file (SIMULATION fallback — lets the script run and be
    demonstrated on a laptop with no camera hardware attached)

Run:   python pi_camera.py
Stop:  Ctrl+C
"""

import io
import sys
import time
import requests

# ─── CONFIGURATION ──────────────────────────────────────────
BACKEND_URL = "https://zoogloeal-nonprescribed-lovella.ngrok-free.dev"
FARM_ID     = "81db3508-b9df-4543-82ce-a12d7b5e1667"

# Farmer login used by the camera node to authenticate to the backend
LOGIN_EMAIL    = "farmer@example.com"
LOGIN_PASSWORD = "changeme"

# Zones to scan — defaults to the full 4x4 grid (A1..D4)
ZONES = [f"{row}{col}" for row in ["A", "B", "C", "D"] for col in range(1, 5)]

# Fallback image used when no physical camera is present (simulation/demo)
SAMPLE_IMAGE = "sample_leaf.jpg"

# Header so ngrok does not return its browser-warning HTML page
HEADERS_BASE = {"ngrok-skip-browser-warning": "true"}

DEFAULT_INTERVAL_MINUTES = 30


# ─── CAMERA BACKEND DETECTION ───────────────────────────────
def _make_camera():
    """Return a capture() function that yields JPEG bytes.
    Tries the real Pi camera, then a USB webcam, then a sample file."""

    # 1. Raspberry Pi HQ Camera (real farm deployment)
    try:
        from picamera2 import Picamera2  # type: ignore

        picam = Picamera2()
        picam.configure(picam.create_still_configuration(
            main={"size": (1280, 1280)}
        ))
        picam.start()
        time.sleep(2)  # allow auto-exposure to settle

        def capture():
            buf = io.BytesIO()
            picam.capture_file(buf, format="jpeg")
            return buf.getvalue()

        print("[CAMERA] Using Raspberry Pi HQ Camera (picamera2)")
        return capture
    except Exception:
        pass

    # 2. USB webcam via OpenCV
    try:
        import cv2  # type: ignore

        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            def capture():
                ok, frame = cam.read()
                if not ok:
                    raise RuntimeError("Webcam read failed")
                ok, enc = cv2.imencode(".jpg", frame)
                return enc.tobytes()

            print("[CAMERA] Using USB webcam (OpenCV)")
            return capture
    except Exception:
        pass

    # 3. Sample image fallback (simulation / no hardware)
    def capture():
        with open(SAMPLE_IMAGE, "rb") as f:
            return f.read()

    print(f"[CAMERA] No camera detected — using sample image '{SAMPLE_IMAGE}' (SIMULATION mode)")
    return capture


# ─── BACKEND COMMUNICATION ──────────────────────────────────
def login() -> str:
    """Authenticate and return a JWT access token."""
    resp = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD},
        headers=HEADERS_BASE,
        timeout=15,
    )
    resp.raise_for_status()
    token = resp.json().get("access_token")
    if not token:
        raise RuntimeError(f"Login returned no token: {resp.text}")
    return token


def upload_zone_image(token: str, zone_code: str, image_bytes: bytes) -> dict:
    """Send a captured zone image to the AI predict endpoint."""
    files = {"file": (f"{zone_code}.jpg", image_bytes, "image/jpeg")}
    data = {"farm_id": FARM_ID, "zone_code": zone_code}
    headers = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}

    resp = requests.post(
        f"{BACKEND_URL}/disease/predict",
        files=files,
        data=data,
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_scan_interval(token: str) -> int:
    """Ask the backend for the current recommended scan interval (minutes)."""
    headers = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(
            f"{BACKEND_URL}/farms/{FARM_ID}/scan-interval",
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()
        body = resp.json()
        minutes = int(body.get("scan_interval_minutes", DEFAULT_INTERVAL_MINUTES))
        print(f"[INTERVAL] risk={body.get('risk_level')} -> next sweep in {minutes} min "
              f"({body.get('reason', '')})")
        return minutes
    except Exception as e:
        print(f"[INTERVAL] Could not fetch interval ({e}); using default {DEFAULT_INTERVAL_MINUTES} min")
        return DEFAULT_INTERVAL_MINUTES


# ─── MAIN SCAN LOOP ─────────────────────────────────────────
def scan_once(token: str, capture):
    """Capture and analyse every zone one time."""
    for zone_code in ZONES:
        try:
            image_bytes = capture()
            result = upload_zone_image(token, zone_code, image_bytes)

            disease = result.get("disease_name", "Unknown")
            conf = result.get("confidence_score", 0)
            saved = result.get("saved", False)
            flag = "ALERT" if saved else "ok"
            print(f"  [{zone_code}] {disease} ({conf:.1f}%) — {flag}")
        except Exception as e:
            print(f"  [{zone_code}] capture/upload failed: {e}")
        time.sleep(1)  # small gap between zones


def main():
    print("=" * 55)
    print("  TOMATOGUARD RASPBERRY PI CAMERA NODE")
    print(f"  Backend: {BACKEND_URL}")
    print(f"  Farm ID: {FARM_ID}")
    print(f"  Zones:   {len(ZONES)} ({ZONES[0]}..{ZONES[-1]})")
    print("=" * 55)
    print("Press Ctrl+C to stop\n")

    capture = _make_camera()

    try:
        token = login()
        print("[AUTH] Logged in to backend OK\n")
    except Exception as e:
        print(f"[AUTH] Login failed: {e}")
        sys.exit(1)

    sweep = 0
    while True:
        sweep += 1
        print(f"\n--- Sweep #{sweep} : scanning {len(ZONES)} zones ---")
        scan_once(token, capture)

        minutes = get_scan_interval(token)
        time.sleep(minutes * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCamera node stopped.")
