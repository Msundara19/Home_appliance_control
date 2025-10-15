import cv2
import mediapipe as mp
import requests
import time
from pathlib import Path
from typing import List
from src.common.helpers import load_config

cfg = load_config()
CAMERA_INDEX = int(cfg.get("camera_index", 0))
RASPI_BASE = cfg.get("raspi_base_url", "http://127.0.0.1:8081")
SIMULATION = bool(cfg.get("simulation_mode", False))
TIMEOUT = float(cfg.get("request_timeout_sec", 2.5))
DRAW_TEXT = bool(cfg.get("draw_debug_text", True))

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

def count_extended_fingers(lm: List[List[int]]) -> int:
    """Given a list of [id, x, y], return number of extended fingers.
    Simple heuristic based on landmark order used by MediaPipe Hands.
    """
    if not lm or len(lm) < 21:
        return 0
    # y increases downward in image coordinates
    def is_extended(tip, pip):
        return lm[tip][2] < lm[pip][2]

    fingers = 0
    # Index, Middle, Ring, Little
    for tip, pip in [(8,6),(12,10),(16,14),(20,18)]:
        if is_extended(tip, pip):
            fingers += 1
    # Thumb: compare x relative to knuckle (assumes palm facing camera)
    if lm[4][1] < lm[3][1]:
        fingers += 1
    return fingers

def call_endpoint(path: str):
    url = f"{RASPI_BASE}{path}"
    if SIMULATION:
        print(f"[SIMULATION] Would call {url}")
        return
    try:
        resp = requests.post(url, timeout=TIMEOUT)
        print(f"[{resp.status_code}] {url}")
    except Exception as e:
        print(f"[HTTP ERROR] {url} :: {e}")

def gesture_to_action(fingers: int):
    if fingers == 2:
        call_endpoint("/on")
        return "ON"
    if fingers == 1:
        call_endpoint("/off")
        return "OFF"
    if fingers == 3:
        # Placeholder for volume up
        return "VOL+"
    if fingers == 4:
        # Placeholder for volume down
        return "VOL-"
    return None

def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {CAMERA_INDEX}")
    print("Press 'q' to quit.")

    # Reduce CPU load slightly
    last_action = None
    last_time = 0.0
    action_cooldown = 0.75  # seconds

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    ) as hands:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = hands.process(rgb)

            if res.multi_hand_landmarks:
                for hand_lms in res.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)

                # build simple list of [id, x, y]
                h, w, _ = frame.shape
                lms = []
                for idx, lm in enumerate(res.multi_hand_landmarks[0].landmark):
                    lms.append([idx, int(lm.x * w), int(lm.y * h)])

                fingers = count_extended_fingers(lms)
                now = time.time()
                if now - last_time > action_cooldown:
                    action = gesture_to_action(fingers)
                    if action:
                        last_action = action
                        last_time = now

                if DRAW_TEXT:
                    txt = f"fingers={fingers} action={last_action or '-'}"
                    cv2.putText(frame, txt, (16, 32), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            else:
                if DRAW_TEXT:
                    cv2.putText(frame, "No hand detected", (16, 32), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

            cv2.imshow("Gesture Control", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()