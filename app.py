"""
app.py - VisionAid Main Application
Optimized for FPS, real voice guidance, and live dashboard API.
"""
import time
import cv2
import threading
from flask import Flask, render_template, Response, jsonify

from config import *
from camera import CameraStream
from detector import Detector
from ultrasonic import UltrasonicSensor
from speech import SpeechEngine

app = Flask(__name__)

# ── Initialize Hardware ───────────────────────────────────────────────────────
camera    = CameraStream(index=CAMERA_INDEX, width=320, height=240, fps=120)
detector  = Detector(MODEL_PATH, CONFIDENCE_THRESHOLD)
ultrasonic = UltrasonicSensor(GPIO_TRIG, GPIO_ECHO)
speech    = SpeechEngine()

# ── Global Shared State ───────────────────────────────────────────────────────
last_results      = []
last_instruction  = ""
fps_counter       = {"fps": 0, "count": 0, "ts": time.time()}
COLORS = [(0,255,100), (0,150,255), (255,100,0), (255,255,0), (200,0,255)]

# ── Detection Thread (runs YOLO every ~100ms) ─────────────────────────────────
def detection_loop():
    global last_results
    while True:
        frame = camera.read()
        if frame is None:
            time.sleep(0.05)
            continue
        # Run YOLO on a resized frame for speed
        small = cv2.resize(frame, (320, 240))
        last_results = detector.detect(small)
        time.sleep(0.08)

# ── Voice Guidance Thread (runs every 500ms) ──────────────────────────────────
def voice_guidance_loop():
    global last_results, last_instruction
    last_spoken = {}

    while True:
        distance = ultrasonic.get_distance()

        if last_results:
            # Pick the most confident detection
            top = max(last_results, key=lambda x: x['confidence'])
            class_id = top['class_id']
            label = CLASS_NAMES[class_id] if class_id < len(CLASS_NAMES) else "object"

            # Direction from bounding box center
            x1, y1, x2, y2 = top['box']
            cx_ratio = ((x1 + x2) / 2.0) / 320.0

            if cx_ratio < 0.40:
                direction_phrase = "on your left"
                turn_suggestion  = "Turn right"
            elif cx_ratio > 0.60:
                direction_phrase = "on your right"
                turn_suggestion  = "Turn left"
            else:
                direction_phrase = "directly ahead"
                turn_suggestion  = "Stop"

            now = time.time()
            cooldown_ok = label not in last_spoken or (now - last_spoken[label]) > SPEECH_COOLDOWN

            if cooldown_ok:
                if distance <= DISTANCE_CRITICAL:
                    msg = f"Warning! {label} directly ahead. Stop now."
                elif distance <= DISTANCE_WARNING:
                    msg = f"{label} {direction_phrase}, {distance:.1f} metres. {turn_suggestion}."
                elif distance <= 3.0:
                    msg = f"{label} detected {direction_phrase}, {distance:.1f} metres away."
                else:
                    msg = None

                if msg:
                    print(f"[GUIDANCE] {msg}")
                    last_instruction = msg
                    speech.speak(msg)
                    last_spoken[label] = now

        time.sleep(0.5)

# ── FPS Counter Thread ────────────────────────────────────────────────────────
def fps_loop():
    while True:
        fps_counter["count"] += 1
        elapsed = time.time() - fps_counter["ts"]
        if elapsed >= 2.0:
            fps_counter["fps"] = round(fps_counter["count"] / elapsed, 1)
            fps_counter["count"] = 0
            fps_counter["ts"] = time.time()
        time.sleep(0.033)  # ~30 hz counter tick

threading.Thread(target=detection_loop,    daemon=True).start()
threading.Thread(target=voice_guidance_loop, daemon=True).start()
threading.Thread(target=fps_loop,          daemon=True).start()

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def gen():
        while True:
            frame = camera.read()
            if frame is None:
                continue  # No sleep: check again immediately for max FPS

            # Scale up for display
            display = cv2.resize(frame, (640, 480))

            # Draw detection boxes
            for i, det in enumerate(last_results):
                x1, y1, x2, y2 = det['box']
                # Scale coords from 320x240 to 640x480
                x1, y1, x2, y2 = x1*2, y1*2, x2*2, y2*2
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(640, x2), min(480, y2)

                color = COLORS[i % len(COLORS)]
                label = CLASS_NAMES[det['class_id']] if det['class_id'] < len(CLASS_NAMES) else "OBJ"
                conf  = det.get('confidence', 0)

                cv2.rectangle(display, (x1, y1), (x2, y2), color, 2)
                txt = f"{label.upper()} {conf*100:.0f}%"
                cv2.putText(display, txt, (x1, max(y1 - 8, 14)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

            # FPS overlay in top-right
            fps_txt = f"FPS: {fps_counter['fps']}"
            cv2.putText(display, fps_txt, (550, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 100), 2)

            _, buf = cv2.imencode('.jpg', display, [cv2.IMWRITE_JPEG_QUALITY, 65])
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n')
            fps_counter["count"] += 1

    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def status():
    return jsonify({
        "distance":         round(ultrasonic.get_distance(), 2),
        "detections":       [
            {"label": CLASS_NAMES[d['class_id']], "confidence": round(d['confidence'], 2)}
            for d in last_results if d['class_id'] < len(CLASS_NAMES)
        ],
        "fps":              fps_counter["fps"],
        "last_instruction": last_instruction,
        "system_ok":        True
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=FLASK_PORT, threaded=True)
