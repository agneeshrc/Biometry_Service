import time
import numpy as np
from .camera_worker import frame_queue
from engine.embedder import get_embedding
from engine.normalize import generate_orientations
from engine.database import add_person

CAPTURE_SECONDS = 5
REQUIRED_SAMPLES = 15


def capture_embeddings():
    samples = []
    start = time.time()

    while time.time() - start < CAPTURE_SECONDS:

        frame = frame_queue.get()

        best_emb = None
        best_conf = 0

        for variant in generate_orientations(frame):
            emb, _ = get_embedding(variant)
            if emb is not None:
                best_emb = emb
                break

        if best_emb is not None:
            samples.append(best_emb)

        if len(samples) >= REQUIRED_SAMPLES:
            break

    return samples


def enroll_person(name):

    samples = capture_embeddings()

    if len(samples) < 5:
        return False, "Not enough face samples"

    avg_embedding = np.mean(samples, axis=0)

    add_person(name, avg_embedding.tolist())

    return True, f"{name} enrolled with {len(samples)} samples"
