from fastapi import FastAPI
import time
from .state import STATE
from .camera_worker import start_camera
from .recognition_worker import start_recognition
from .enroll import enroll_person
from engine.database import list_users
import service.runtime_state as runtime_state


app = FastAPI()

@app.on_event("startup")
def startup_event():
    start_camera()
    start_recognition()

@app.get("/identity")
def get_identity():
    return STATE.read()

@app.post("/enroll/{name}")
def enroll(name: str):
    success, msg = enroll_person(name)
    return {"success": success, "message": msg}

@app.get("/users")
def get_users():
    return {"users": list_users()}

@app.get("/status")
def status():
    return {
        "service": "running",
        "camera_connected": runtime_state.camera_connected,
        "recognition_active": runtime_state.recognition_active,
        "seconds_since_last_frame": time.time() - runtime_state.last_frame_time if runtime_state.last_frame_time else None,
        "uptime": runtime_state.uptime()
    }

