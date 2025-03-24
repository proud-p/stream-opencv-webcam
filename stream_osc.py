import cv2
import mediapipe as mp
from pythonosc import udp_client

# MediaPipe setup
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# OSC setup
osc_ip = "192.168.0.2"   # Replace with receiver's IP
osc_port = 5009
osc_client = udp_client.SimpleUDPClient(osc_ip, osc_port)

def generate_frames_local():
    cap = cv2.VideoCapture(0)
    last_coords = None
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
                    coords = [round(lm9.x, 2), round(lm9.y, 2), round(lm9.z, 2)]
                    hand_detected = True

                    if coords != last_coords:
                        osc_client.send_message("/xyz", coords)
                        print(f"Sent OSC /xyz: {coords}")
                        last_coords = coords

            if not hand_detected and hand_was_present:
                # Send [0.0, 0.0, 0.0] once when hand disappears
                osc_client.send_message("/xyz", [0.0, 0.0, 0.0])
                print("Sent OSC /xyz: [0.0, 0.0, 0.0] (hand left)")
                last_coords = [0.0, 0.0, 0.0]

            hand_was_present = hand_detected

            # Flip the image horizontally for a selfie-view display.
            cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    generate_frames_local()
