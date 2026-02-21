import cv2
import numpy as np
from engine.embedder import get_embedding
from engine.database import add_person

CAM_INDEX = 2
SAMPLES_REQUIRED = 20

cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Camera not detected")
    exit()

print("Enrollment UI started")

# ---------------- STATES ----------------
typing_mode = False
enrolling = False
skip_next_key = False
typed_name = ""
person_name = ""
collected_embeddings = []
# ----------------------------------------

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    display = cv2.flip(frame, 1)

    key = cv2.waitKey(1) & 0xFF

    # ---------- START TYPING ----------
    if key == ord('e') and not typing_mode and not enrolling:
        typing_mode = True
        typed_name = ""
        skip_next_key = True

    # ---------- HANDLE TYPING ----------
    if typing_mode:

        if key == 13:  # ENTER
            if typed_name.strip() != "":
                person_name = typed_name.strip()
                enrolling = True
                collected_embeddings = []
                typing_mode = False
                print(f"Enrollment started for: {person_name}")
            else:
                typing_mode = False

        elif key == 8:  # BACKSPACE
            typed_name = typed_name[:-1]

        elif 32 <= key <= 126 and not skip_next_key:
            typed_name += chr(key)


    # ---------- CAPTURE EMBEDDINGS ----------
    if enrolling:
        embedding, box = get_embedding(display)

        if embedding is not None:
            collected_embeddings.append(embedding)
            print(f"Captured {len(collected_embeddings)}/{SAMPLES_REQUIRED}")

        if box is not None:
            x, y, w, h = box
            cv2.rectangle(display, (x, y), (x + w, y + h), (0,255,0), 2)

        if len(collected_embeddings) >= SAMPLES_REQUIRED:
            avg_embedding = np.mean(collected_embeddings, axis=0)
            add_person(person_name, avg_embedding, len(collected_embeddings))

            print(f"{person_name} successfully enrolled!\n")

            enrolling = False
            person_name = ""
            typed_name = ""

    # ---------- UI TEXT ----------
    if typing_mode:
        status = f"Enter name: {typed_name}_"
        color = (0,255,255)

    elif enrolling:
        status = f"Enrolling {person_name}: {len(collected_embeddings)}/{SAMPLES_REQUIRED}"
        color = (0,255,0)

    else:
        status = "Press E to enroll | Q to quit"
        color = (0,200,200)

    cv2.rectangle(display, (10, 10), (display.shape[1]-10, 50), (0,0,0), -1)
    cv2.putText(display, status, (20,40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    skip_next_key = False

    cv2.imshow("Enrollment", display)

    if key == ord('q') or key == 27:
        break

cap.release()
cv2.destroyAllWindows()
