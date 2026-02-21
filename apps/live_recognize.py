import cv2
from collections import deque, Counter
from engine.embedder import get_embedding
from engine.recognizer import recognize

CAM_INDEX = 2
RECOGNIZE_EVERY = 10

HISTORY_SIZE = 6
LOCK_REQUIRED = 2
LOCK_THRESHOLD = 0.55

UNLOCK_THRESHOLD = 0.35
HOLD_FRAMES = 25

SWITCH_THRESHOLD = 0.65
SWITCH_REQUIRED = 3

MIN_FACE_SIZE = 80        # reject tiny detections
FACE_STABLE_REQUIRED = 3  # frames face must persist

cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("Camera not detected")
    exit()

frame_count = 0
hold_counter = 0
face_stable_count = 0

name_history = deque(maxlen=HISTORY_SIZE)
stable_name = "Unknown"
stable_box = None

candidate_name = None
candidate_count = 0
locked_name = None
locked_conf = 0.0

switch_candidate = None
switch_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    display = cv2.flip(frame, 1)

    if frame_count % RECOGNIZE_EVERY == 0:

        embedding, box = get_embedding(display)

        valid_face = False

        if box is not None:
            x,y,w,h = box

            # -------- FACE SIZE FILTER --------
            if w >= MIN_FACE_SIZE and h >= MIN_FACE_SIZE:
                face_stable_count += 1
            else:
                face_stable_count = 0

            if face_stable_count >= FACE_STABLE_REQUIRED:
                valid_face = True
        else:
            face_stable_count = 0

        # -------- ONLY RECOGNIZE VALID FACE --------
        if valid_face and embedding is not None:
            state, name, conf = recognize(embedding)

            if state == "CONFIRMED":
                detected = name
            else:
                detected = "Unknown"

            stable_box = box
        else:
            detected = "Unknown"
            conf = 0.0

        name_history.append(detected)
        stable_name = Counter(name_history).most_common(1)[0][0]

        # ---------------- LOCK ACQUIRE ----------------
        if locked_name is None:

            if stable_name not in ["Unknown","No face"] and conf > LOCK_THRESHOLD:
                if candidate_name == stable_name:
                    candidate_count += 1
                else:
                    candidate_name = stable_name
                    candidate_count = 1

                if candidate_count >= LOCK_REQUIRED:
                    locked_name = stable_name
                    locked_conf = conf
                    hold_counter = HOLD_FRAMES

        # ---------------- LOCKED: CHECK SWITCH ----------------
        else:

            if stable_name != locked_name and conf > SWITCH_THRESHOLD:

                if switch_candidate == stable_name:
                    switch_count += 1
                else:
                    switch_candidate = stable_name
                    switch_count = 1

                if switch_count >= SWITCH_REQUIRED:
                    locked_name = stable_name
                    locked_conf = conf
                    hold_counter = HOLD_FRAMES
                    name_history.clear()

            # maintain lock
            if conf > UNLOCK_THRESHOLD:
                hold_counter = HOLD_FRAMES
            else:
                hold_counter -= 1
                if hold_counter <= 0:
                    locked_name = None

    frame_count += 1

    # -------- DISPLAY --------
    if locked_name is not None:
        text = f"{locked_name} ({locked_conf:.2f})"
        color = (0,200,0)
    else:
        text = "Unknown"
        color = (0,0,255)

    if stable_box is not None:
        x,y,w,h = stable_box
        cv2.rectangle(display,(x,y),(x+w,y+h),color,2)
        cv2.putText(display,text,(x,y-10),
                    cv2.FONT_HERSHEY_SIMPLEX,0.7,color,2)

    cv2.imshow("Live Recognition",display)

    if cv2.waitKey(1)&0xFF in [27,ord('q')]:
        break

cap.release()
cv2.destroyAllWindows()
