import cv2
import mediapipe as mp
from pythonosc import udp_client
from collections import deque
import time

# MediaPipe setup
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# OSC setup
wsl_ip = "172.30.40.252"  # WSL IP
windows_ip = "127.0.0.1"  # Localhost for Windows
osc_port = 5009
osc_client_wsl = udp_client.SimpleUDPClient(wsl_ip, osc_port)
osc_client_windows = udp_client.SimpleUDPClient(windows_ip, osc_port)

# === Smoothing Settings ===
smooth_buffer = deque(maxlen=5)  # For moving average
last_coords = [0.0, 0.0, 0.0]
last_send_time = 0
send_interval = 0.1  # seconds
threshold = 0.1  # minimum change required to send OSC

def has_moved_significantly(current, last, threshold=0.05):
    return any(abs(c - l) > threshold for c, l in zip(current, last))

def generate_frames_local():
    global last_coords, last_send_time
    cap = cv2.VideoCapture(0)
    hand_was_present = False

    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            hand_detected = False

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )

                    # Get landmark 9 (middle finger MCP)
                    lm9 = hand_landmarks.landmark[9]
                    coords = [round(lm9.x, 2), round(lm9.y, 2), 0.0]
                    hand_detected = True
                    smooth_buffer.append(coords)

                    if len(smooth_buffer) == smooth_buffer.maxlen:
                        smoothed = [
                            round(sum(val) / len(val), 2)
                            for val in zip(*smooth_buffer)
                        ]

                        now = time.time()
                        if has_moved_significantly(smoothed, last_coords, threshold) and (now - last_send_time > send_interval):
                            osc_client_wsl.send_message("/xyz", smoothed)
                            osc_client_windows.send_message("/xyz", smoothed)
                            print(f"📤 Sent OSC /xyz: {smoothed}")
                            last_coords = smoothed
                            last_send_time = now

            if not hand_detected and hand_was_present:
                osc_client_wsl.send_message("/xyz", [0.0, 0.0, 0.0])
                osc_client_windows.send_message("/xyz", [0.0, 0.0, 0.0])
                
                if last_coords != [0.0, 0.0, 0.0]: # only send 0.0 if last coord wasnt already 0.0
                    print("👋 Hand left — Sent OSC /xyz: [0.0, 0.0, 0.0]")
                    last_coords = [0.0, 0.0, 0.0]
                    smooth_buffer.clear()

            hand_was_present = hand_detected

            # Flip image for selfie-view display
            cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    generate_frames_local()
