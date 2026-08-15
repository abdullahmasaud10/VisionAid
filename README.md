# VisionAid – Blind Assistance System 🦯

Real-time object detection + ultrasonic distance sensing + voice guidance
for visually impaired users, running on **Raspberry Pi 4B**.

---

## Project Structure

```
AI_FYP/
├── start.py                            ← Main launcher & automatic setup
├── app.py                              ← Flask server & spatial guidance loop
├── detector.py                         ← YOLOv8 ONNX object detection module
├── ultrasonic.py                       ← HC-SR04 ultrasonic distance sensor driver
├── speech.py                           ← Non-blocking Text-to-Speech audio queue
├── camera.py                           ← V4L2 threaded USB camera capture
├── config.py                           ← System parameters, pins, and classes
├── requirements.txt                    ← Python package dependencies
├── visionaid.service                   ← systemd auto-start boot service
├── VisionAid_Complete_Project_Guide.docx ← Complete project mechanism & setup guide
├── model/
│   └── yolov8n.onnx                    ← Optimized YOLOv8 ONNX model weights
├── templates/
│   └── index.html                      ← Web monitoring dashboard UI
└── static/
    ├── css/style.css
    └── js/app.js
```

---

## Hardware Wiring

### HC-SR04 Ultrasonic Sensor → Raspberry Pi GPIO (BCM)

```
HC-SR04 Pin    Raspberry Pi Pin
───────────    ─────────────────
VCC      →     Pin 2  (5V)
GND      →     Pin 6  (GND)
TRIG     →     Pin 16 (GPIO 23)
ECHO     →     Pin 18 (GPIO 24)  ← Use a 1kΩ + 2kΩ voltage divider!
```

> ⚠️ **ECHO voltage divider is mandatory.**
> The Pi GPIO is 3.3 V tolerant. HC-SR04 ECHO outputs 5 V.
> Wire: ECHO → 1kΩ → GPIO 24, then GPIO 24 → 2kΩ → GND.

### USB Webcam
Plug into any USB port. Detected automatically as `/dev/video0`.

---

## Quick Start (Raspberry Pi)

### 1 – Transfer project to Pi

```bash
# From your PC (replace IP with your Pi's IP)
scp -r E:/AI_FYP pi@192.168.1.x:/home/pi/AI_FYP
```

Or clone/copy any other way (USB, git, etc.)

### 2 – Run the launcher

```bash
cd /home/pi/AI_FYP
python3 start.py
```

`start.py` will automatically:

| Step | Action |
|------|--------|
| 1 | Verify Python ≥ 3.9 |
| 2 | Detect Raspberry Pi hardware |
| 3 | Install system packages via `apt` (espeak, libatlas, v4l-utils …) |
| 4 | Create Python virtual environment `./venv` |
| 5 | Install all pip packages (flask, opencv, pyttsx3, RPi.GPIO …) |
| 6 | Validate `model/best.onnx` exists |
| 7 | Launch Flask server |

### 3 – Open the Dashboard

On any device connected to the same network:

```
http://<raspberry-pi-ip>:5000
```

To find your Pi's IP:
```bash
hostname -I
```

---

## Configuration (`config.py`)

| Setting | Default | Description |
|---------|---------|-------------|
| `GPIO_TRIG` | 23 | HC-SR04 Trigger pin (BCM) |
| `GPIO_ECHO` | 24 | HC-SR04 Echo pin (BCM) |
| `DISTANCE_CRITICAL` | 0.5 m | STOP immediately |
| `DISTANCE_WARNING` | 1.5 m | Warn + give direction |
| `DISTANCE_NEAR` | 3.0 m | Announce object name |
| `CONFIDENCE_THRESHOLD` | 0.45 | Detection minimum confidence |
| `CAMERA_INDEX` | 0 | USB camera index |
| `SPEECH_COOLDOWN` | 3.0 s | Min gap between repeated announcements |
| `FLASK_PORT` | 5000 | Web dashboard port |

---

## Voice Guidance Logic

```
Distance ≤ 0.5 m  →  "Warning! [object] directly ahead. Stop! 0.3 metres."
Distance ≤ 1.5 m  →  "[object] on your left, 1.2 metres. Turn right."
Distance ≤ 3.0 m  →  "[object] detected on your right, 2.5 metres away."

Object position in frame:
  cx_ratio < 0.45  →  "on your left"   → suggest turn right
  cx_ratio > 0.55  →  "on your right"  → suggest turn left
  otherwise        →  "ahead"
```

Critical hazard objects (pothole, stairs, ditch, manhole …) always say **"Stop immediately"** regardless of direction.

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/` | Live dashboard |
| `GET` | `/video_feed` | MJPEG annotated camera stream |
| `GET` | `/api/status` | JSON: distance, detections, FPS |
| `POST` | `/api/speech` | `{"text": "…"}` → speak via TTS |

### Example `/api/status` response
```json
{
  "distance": 1.24,
  "detections": [
    {"label": "person", "confidence": 0.87},
    {"label": "chair",  "confidence": 0.72}
  ],
  "fps": 12.4,
  "system_ok": true
}
```

---

## Auto-Start on Boot (Optional)

To have the system start automatically when the Pi powers on:

```bash
# Copy service file
sudo cp /home/pi/AI_FYP/visionaid.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable visionaid
sudo systemctl start visionaid

# Check status
sudo systemctl status visionaid

# View live logs
sudo journalctl -u visionaid -f
```

---

## Troubleshooting

### Camera not found
```bash
# List connected cameras
ls /dev/video*
v4l2-ctl --list-devices

# Change index in config.py if needed
CAMERA_INDEX = 1
```

### GPIO / Sensor errors
```bash
# Check GPIO access (Pi OS Bookworm uses gpiod)
sudo usermod -aG gpio pi
# Then log out and back in

# Test ultrasonic manually
python3 -c "
import RPi.GPIO as GPIO, time
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT); GPIO.setup(24, GPIO.IN)
GPIO.output(23, True); time.sleep(0.00001); GPIO.output(23, False)
print('Echo pin:', GPIO.input(24))
GPIO.cleanup()
"
```

### No sound / espeak
```bash
sudo apt install espeak -y
# Test
espeak "Hello world"
# Check audio output device
aplay -l
```

### Model fails to load
```bash
# Verify the file is a valid ONNX model
python3 -c "
import cv2
net = cv2.dnn.readNetFromONNX('model/best.onnx')
print('Model OK, outputs:', net.getUnconnectedOutLayersNames())
"
```

### Slow FPS on Raspberry Pi
- Use `CAMERA_WIDTH=320, CAMERA_HEIGHT=240` in `config.py`
- Lower `CONFIDENCE_THRESHOLD` to `0.35` for slightly faster NMS
- Close other running processes: `sudo systemctl stop triggerhappy`

---

## Detected Object Classes (60)

| ID | Class | ID | Class | ID | Class |
|----|-------|----|-------|----|-------|
| 0 | person | 20 | crosswalk | 40 | shopping_cart |
| 1 | chair | 21 | traffic_light | 41 | umbrella |
| 2 | table | 22 | stop_sign | 42 | backpack |
| 3 | car | 23 | bench | 43 | handbag |
| 4 | motorcycle | 24 | trash_bin | 44 | suitcase |
| 5 | rickshaw | 25 | fire_hydrant | 45 | bottle |
| 6 | bicycle | 26 | wall | 46 | cup |
| 7 | bus | 27 | fence | 47 | food_stall |
| 8 | truck | 28 | ramp | 48 | fruit_cart |
| 9 | dog | 29 | wheelchair | 49 | electric_pole |
| 10 | cat | 30 | cane | 50 | wire |
| 11 | cow | 31 | puddle | 51 | ditch |
| 12 | buffalo | 32 | manhole | 52 | rock |
| 13 | goat | 33 | speed_bump | 53 | barrier |
| 14 | horse | 34 | cart | 54 | construction_zone |
| 15 | donkey | 35 | shop_front | 55 | signboard |
| 16 | stairs | 36 | door | 56 | parked_vehicle |
| 17 | gate | 37 | window | 57 | median |
| 18 | pole | 38 | tree | 58 | drain |
| 19 | pothole | 39 | curb | 59 | road_divider |
