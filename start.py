#!/usr/bin/env python3
"""
start.py - System Setup and Application Launcher
"""
import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
VENV_DIR = BASE_DIR / "venv"
VENV_PYTHON = VENV_DIR / "bin" / "python3"
MODEL_FILE = BASE_DIR / "model" / "yolov8n.onnx"
APP_FILE = BASE_DIR / "app.py"

def setup():
    print("\n--- VisionAid System Setup ---")
    
    # 1. Check system dependencies (OpenCV & espeak)
    print("Checking system dependencies...")
    try:
        import cv2
        subprocess.run(["which", "espeak"], check=True, stdout=subprocess.DEVNULL)
        print("System dependencies OK.")
    except (ImportError, subprocess.CalledProcessError):
        print("Installing system dependencies (OpenCV + espeak)...")
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "python3-opencv", "espeak"], check=True)

    # 2. Create virtual environment
    if not VENV_DIR.exists():
        print("Setting up virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "--system-site-packages", str(VENV_DIR)], check=True)
        
    # 3. Install remaining requirements
    print("Installing libraries...")
    subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", "-r", str(BASE_DIR / "requirements.txt")], check=True)

    # 4. Validate Model
    if not MODEL_FILE.exists():
        print(f"ERROR: Place yolov8n.onnx in {MODEL_FILE}")
        sys.exit(1)

def run():
    print("\n🚀 Launching System...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE_DIR)
    # Use absolute path for app.py to be 100% safe
    subprocess.run([str(VENV_PYTHON), str(APP_FILE)], cwd=str(BASE_DIR), env=env)

if __name__ == "__main__":
    try:
        setup()
        run()
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        input("Press Enter to close...")
