from deepface import DeepFace
import numpy as np

def get_embedding(frame):
    try:
        result = DeepFace.represent(
            img_path = frame,
            model_name = "Facenet512",
            enforce_detection = False,
            detector_backend = "opencv"
        )

        if len(result) == 0:
            return None, None

        embedding = np.array(result[0]["embedding"])

        # facial area info
        region = result[0]["facial_area"]
        x, y, w, h = region["x"], region["y"], region["w"], region["h"]

        return embedding, (x, y, w, h)

    except Exception:
        return None, None
