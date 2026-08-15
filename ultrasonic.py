"""
ultrasonic.py - HC-SR04 Distance Sensor Driver
"""
import RPi.GPIO as GPIO
import time
import logging

class UltrasonicSensor:
    def __init__(self, trig, echo):
        self.trig = trig
        self.echo = echo
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.trig, GPIO.OUT)
            GPIO.setup(self.echo, GPIO.IN)
            GPIO.output(self.trig, False)
            logging.info(f"Ultrasonic initialized: TRIG={trig}, ECHO={echo}")
        except Exception as e:
            logging.error(f"GPIO Setup failed: {e}")

    def get_distance(self):
        try:
            # Send Pulse
            GPIO.output(self.trig, True)
            time.sleep(0.00001)
            GPIO.output(self.trig, False)

            start_time = time.time()
            stop_time = time.time()

            # Wait for Echo
            timeout = time.time() + 0.1
            while GPIO.input(self.echo) == 0:
                start_time = time.time()
                if start_time > timeout: return 4.0 # Default to safe distance

            while GPIO.input(self.echo) == 1:
                stop_time = time.time()
                if stop_time > timeout: return 4.0

            elapsed = stop_time - start_time
            distance = (elapsed * 34300) / 2
            return round(distance / 100, 2) # Convert to meters
            
        except Exception:
            return 4.0 # Safe fallback
