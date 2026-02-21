import numpy as np
from .database import load_db

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def recognize(embedding, threshold=0.45, strong_threshold=0.65):
    db = load_db()

    best_match = None
    best_score = -1

    for person, data in db.items():
        emb = data["embedding"]
        score = cosine_similarity(embedding, emb)
        if score > best_score:
            best_score = score
            best_match = person

    # -------- DECISION STATES --------
    if best_score >= strong_threshold:
        return "CONFIRMED", best_match, best_score

    elif best_score >= threshold:
        return "UNCERTAIN", best_match, best_score

    else:
        return "UNKNOWN", None, best_score
