import time
from collections import deque, Counter
from .state import STATE

# --- CONFIG ---
HISTORY = 8
CONFIRM_COUNT = 4
LOST_TIMEOUT = 2.0
MIN_CONFIDENCE = 0.45
FAST_CONFIRM = 0.65   # instant confirmation threshold


class IdentityTracker:

    def __init__(self):
        self.history = deque(maxlen=HISTORY)
        self.current_name = None
        self.last_seen_time = 0
        self.confirmed = False
        self.last_confidence = 0.0

    def update(self, name, confidence):

        now = time.time()

        # --- FAST CONFIRM (high confidence detection) ---
        if name not in ["No Face", "Unknown"] and confidence >= FAST_CONFIRM:
            self.current_name = name
            self.confirmed = True
            self.last_confidence = confidence
            self.last_seen_time = now
            STATE.update(name, confidence)
            self.history.clear()
            self.history.append(name)
            return

        # --- NO FACE CASE ---
        if name in ["No Face", "Unknown"] or confidence < MIN_CONFIDENCE:
            self.history.append(None)
        else:
            self.history.append(name)
            self.last_seen_time = now

        # --- MAJORITY DECISION ---
        counts = Counter(self.history)
        candidate, freq = counts.most_common(1)[0]

        # --- CONFIRMATION ---
        if candidate is not None and freq >= CONFIRM_COUNT:
            self.current_name = candidate
            self.confirmed = True
            self.last_confidence = confidence
            STATE.update(candidate, confidence)
            return

        # --- LOST DETECTION ---
        if self.confirmed:
            if now - self.last_seen_time > LOST_TIMEOUT:
                self.current_name = None
                self.confirmed = False
                STATE.update("No Face", 0.0)
                return
            else:
                STATE.update(self.current_name, self.last_confidence)
                return

        # --- STILL DETECTING ---
        STATE.update("Detecting", confidence)


TRACKER = IdentityTracker()
