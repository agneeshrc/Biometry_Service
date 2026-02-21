import cv2
import time
import numpy as np

MAX_INDEX = 6
TEST_FRAMES = 15
MOTION_THRESHOLD = 2.0


def _frame_valid(frame):
    if frame is None:
        return False

    # reject fully black frames (ghost cameras)
    if np.mean(frame) < 5:
        return False

    return True


def _detect_motion(frames):
    diffs = []
    for i in range(1, len(frames)):
        diff = cv2.absdiff(frames[i], frames[i-1])
        diffs.append(np.mean(diff))
    return np.mean(diffs) > MOTION_THRESHOLD


def test_camera(index):
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        return False

    frames = []

    for _ in range(TEST_FRAMES):
        ret, frame = cap.read()
        if not ret or not _frame_valid(frame):
            cap.release()
            return False
        frames.append(frame)
        time.sleep(0.03)

    cap.release()

    return _detect_motion(frames)


def find_working_camera():
    print("Scanning cameras...")

    for i in range(MAX_INDEX):
        if test_camera(i):
            print(f"Using camera index {i}")
            return i

    raise RuntimeError("No working camera found")
