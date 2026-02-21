import cv2

def generate_orientations(frame):
    return [
        frame,
        cv2.flip(frame, 1),                      # mirrored
        cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE),
        cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE),
        cv2.flip(cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE), 1),
        cv2.flip(cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE), 1),
    ]
