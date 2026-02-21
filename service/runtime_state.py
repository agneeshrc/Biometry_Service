import time

START_TIME = time.time()

camera_connected = False
recognition_active = False
last_frame_time = 0


def uptime():
    return time.time() - START_TIME
