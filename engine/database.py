import numpy as np
import os

DB_PATH = "embeddings/database.npy"


# ---------- LOAD ----------
def load_db():
    if not os.path.exists(DB_PATH):
        return {}

    db = np.load(DB_PATH, allow_pickle=True).item()

    # MIGRATION: old format (name -> embedding)
    for k, v in list(db.items()):
        if isinstance(v, np.ndarray):
            db[k] = {"embedding": v, "samples": 1}

    return db


# ---------- SAVE ----------
def save_db(db):
    np.save(DB_PATH, db)


# ---------- ADD / UPDATE ----------
def add_person(name, new_embedding, new_samples=1):
    db = load_db()

    if name in db:
        old_emb = db[name]["embedding"]
        old_n = db[name]["samples"]

        # running average update
        updated_emb = (old_emb * old_n + new_embedding * new_samples) / (old_n + new_samples)

        db[name]["embedding"] = updated_emb
        db[name]["samples"] = old_n + new_samples

        print(f"[UPDATE] {name} improved → total samples: {db[name]['samples']}")

    else:
        db[name] = {"embedding": new_embedding, "samples": new_samples}
        print(f"[NEW] {name} enrolled")

    save_db(db)


# ---------- REMOVE ----------
def remove_person(name):
    db = load_db()
    if name in db:
        del db[name]
        save_db(db)
        return True
    return False


def list_users():
    return list(load_db().keys())


