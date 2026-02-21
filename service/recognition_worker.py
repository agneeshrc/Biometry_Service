import threading
from .camera_worker import frame_queue
from .tracker import TRACKER
import service.runtime_state as runtime_state
from engine.embedder import get_embedding
from engine.recognizer import recognize
from engine.normalize import generate_orientations

running = False


def recognition_loop():
    global running
    running = True
    runtime_state.recognition_active = True
    print("Recognition started")

    while running:
        frame = frame_queue.get()

        try:
            best_state = "UNKNOWN"
            best_name = None
            best_conf = 0.0
            found_face = False

            # Try multiple orientations and choose best similarity
            for variant in generate_orientations(frame):

                embedding, box = get_embedding(variant)

                if embedding is None:
                    continue

                found_face = True

                state, name, conf = recognize(embedding)

                if conf > best_conf:
                    best_state = state
                    best_name = name
                    best_conf = conf

            # --- send results to tracker (NOT directly to STATE) ---
            if not found_face:
                TRACKER.update("No Face", 0.0)

            elif best_state == "CONFIRMED":
                TRACKER.update(best_name, best_conf)

            elif best_state == "UNCERTAIN":
                TRACKER.update(best_name, best_conf)

            else:
                TRACKER.update("Unknown", best_conf)

        except Exception as e:
            print("Recognition error:", e)


def start_recognition():
    t = threading.Thread(target=recognition_loop, daemon=True)
    t.start()
