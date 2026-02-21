import threading
import time

class IdentityState:
    def __init__(self):
        self.lock = threading.Lock()
        self.name = "Unknown"
        self.confidence = 0.0
        self.present = False
        self.last_seen = 0

    def update(self, name, confidence):
        with self.lock:
            self.name = name
            self.confidence = confidence
            self.present = name != "Unknown"
            self.last_seen = time.time()

    def read(self):
        with self.lock:
            return {
                "name": self.name,
                "confidence": float(self.confidence),
                "present": self.present,
                "last_seen": self.last_seen
            }

STATE = IdentityState()
