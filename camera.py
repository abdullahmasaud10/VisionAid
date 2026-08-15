"""
camera.py - High FPS Camera Stream
Optimized for Raspberry Pi with V4L2 and a lock-free latest-frame buffer.
"""
import cv2
import threading
import logging

class CameraStream:
    def __init__(self, index=0, width=320, height=240, fps=120):
        self.index = index
        self._lock = threading.Lock()
        self.frame = None
        self.stopped = False

        # Force V4L2 backend on Raspberry Pi
        self.cap = cv2.VideoCapture(self.index, cv2.CAP_V4L2)

        # Buffer size 1 = always get the newest frame, never wait for old ones
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)

        # Use MJPEG codec inside V4L2 for hardware-accelerated capture
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        # Warm up: grab first frame
        ret, frame = self.cap.read()
        if ret:
            self.frame = frame
            logging.info(f"Camera started: {width}x{height} @ {fps}fps (V4L2 MJPG)")
        else:
            logging.error(f"Failed to open camera at index {index}")

        # Start the capture thread
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        """Continuously reads the latest frame into the buffer."""
        while not self.stopped:
            if not self.cap.isOpened():
                break
            ret, frame = self.cap.read()
            if ret:
                with self._lock:
                    self.frame = frame

    def read(self):
        """Returns the most recent frame (thread-safe)."""
        with self._lock:
            return self.frame

    def stop(self):
        self.stopped = True
        self.cap.release()
