"""
speech.py - Text-to-Speech Engine using espeak-ng
"""
import subprocess
import threading
import queue
import logging

class SpeechEngine:
    def __init__(self):
        # Queue size 2: drop old messages to avoid audio lag backlog
        self.queue = queue.Queue(maxsize=2)
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        logging.info("Speech Engine Online.")

    def speak(self, text):
        """Queue a message. Drops it silently if already busy."""
        try:
            self.queue.put_nowait(text)
        except queue.Full:
            pass

    def _worker(self):
        # Detect if espeak-ng is available (clearer than espeak)
        try:
            subprocess.run(["espeak-ng", "--version"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            cmd = "espeak-ng"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            cmd = "espeak"

        logging.info(f"Using TTS binary: {cmd}")

        while True:
            msg = self.queue.get()
            if msg:
                # Clean punctuation that causes espeak to pause awkwardly
                msg = (msg.replace("!", ".")
                          .replace('"', '')
                          .replace("'", ""))

                try:
                    subprocess.run(
                        [
                            cmd,
                            "-v", "en",       # Standard English voice — clearest pronunciation
                            "-s", "165",       # 165 words/min — fast but clearly understandable
                            "-p", "50",        # Pitch 50 — natural male tone
                            "-a", "200",       # Full volume
                            "-g", "5",         # 5ms gap between words — smooth flow, no robotic pauses
                            msg
                        ],
                        timeout=12,
                        stderr=subprocess.DEVNULL
                    )
                except subprocess.TimeoutExpired:
                    pass
                except FileNotFoundError:
                    logging.error(f"{cmd} not found. Run: sudo apt install espeak-ng -y")
                except Exception as e:
                    logging.error(f"TTS error: {e}")
            self.queue.task_done()
