import cv2
import queue
import threading
import time
from .camera_manager import find_working_camera
import service.runtime_state as runtime_state

frame_queue = queue.Queue(maxsize=5)
running = False
current_index = None


def open_camera():
    global current_index

    while True:
        try:
            idx = find_working_camera()
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)

            if cap.isOpened():
                current_index = idx
                runtime_state.camera_connected = True
                print(f"Camera connected at index {idx}")
                return cap

        except Exception as e:
            print("Camera search failed, retrying...", e)

        time.sleep(2)


def camera_loop():
    global running

    cap = open_camera()
    running = True
    print("Camera started")

    while running:

        ret, frame = cap.read()

        # camera unplugged / droidcam closed
        if not ret or frame is None:
            runtime_state.camera_connected = False
            print("Camera lost. Reconnecting...")
            cap.release()
            time.sleep(1)
            cap = open_camera()
            continue

        runtime_state.last_frame_time = time.time()

        # Always keep newest frame (drop old ones)
        if frame_queue.full():
            try:
                frame_queue.get_nowait()
            except queue.Empty:
                pass

        frame_queue.put(frame)

    cap.release()
    print("Camera stopped")


def start_camera():
    t = threading.Thread(target=camera_loop, daemon=True)
    t.start()
