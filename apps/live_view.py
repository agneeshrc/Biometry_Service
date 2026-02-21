import cv2

# Try camera index 0 first (DroidCam usually becomes 0 or 1)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Trying camera 1...")
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Camera not detected")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Rotate portrait (fix phone tilt)
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    frame = cv2.flip(frame, 1)  # Mirror horizontally

    cv2.imshow("Live Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

"""
import cv2
import time

def find_working_camera(max_tested=6):
    for i in range(max_tested):
        print(f"[INFO] Testing camera {i+1}")

        cap = cv2.VideoCapture(i+1, cv2.CAP_DSHOW)

        if not cap.isOpened():
            cap.release()
            continue

        # give the driver time to start
        time.sleep(1)

        # attempt non-blocking grab
        ok = cap.grab()

        if not ok:
            cap.release()
            continue

        ret, frame = cap.retrieve()
        cap.release()

        if ret and frame is not None:
            print(f"[INFO] Using camera index: {i+1}")
            return i

    return None



# ---------- Camera selection ----------
cam_index = find_working_camera()

if cam_index is None:
    print("No working camera found")
    exit()

cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)

# ---------- Main Loop ----------
while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame grab failed")
        break

    # OPTIONAL: orientation correction example
    h, w = frame.shape[:2]
    if h > w:
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

    cv2.imshow("Live Camera", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
"""

#pygrabber
# pip install pygrabber 
"""
import cv2
from pygrabber.dshow_graph import FilterGraph

def find_droidcam_index():
    graph = FilterGraph()
    devices = graph.get_input_devices()

    for i, name in enumerate(devices):
        print(f"[INFO] Camera {i}: {name}")
        if "droid" in name.lower():
            print(f"[INFO] Using DroidCam at index {i}")
            return i

    return None


cam_index = find_droidcam_index()

if cam_index is None:
    print("DroidCam not found")
    exit()

cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame grab failed")
        break

    cv2.imshow("Live Camera", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
"""