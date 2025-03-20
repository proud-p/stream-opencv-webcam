
# code from https://mediapipe.readthedocs.io/en/latest/solutions/hands.html

import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
import json

def generate_frames_local():
  # For webcam input:
  cap = cv2.VideoCapture(0)
  with mp_hands.Hands(
      model_complexity=0,
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
      success, image = cap.read()
      if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

      # To improve performance, optionally mark the image as not writeable to
      # pass by reference.
      image.flags.writeable = False
      image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
      results = hands.process(image)

      # Draw the hand annotations on the image.
      image.flags.writeable = True
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
          mp_drawing.draw_landmarks(
              image,
              hand_landmarks,
              mp_hands.HAND_CONNECTIONS,
              mp_drawing_styles.get_default_hand_landmarks_style(),
              mp_drawing_styles.get_default_hand_connections_style())
          
        print(hand_landmarks.landmark[9]) #middle finger MCP
      # Flip the image horizontally for a selfie-view display.
      cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
      if cv2.waitKey(5) & 0xFF == 27:
        break
  cap.release()
  
  



def generate_frames():
  global latest_landmark_9  # Store data for API
  
  mp_drawing = mp.solutions.drawing_utils
  mp_drawing_styles = mp.solutions.drawing_styles
  mp_hands = mp.solutions.hands
  cap = cv2.VideoCapture(0)  # Capture from webcam
  with mp_hands.Hands(
      model_complexity=0,
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5) as hands:

      while cap.isOpened():
          success, image = cap.read()
          if not success:
              print("Ignoring empty camera frame.")
              break  # Stop if camera feed is lost

          # Convert the image to RGB for processing
          image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
          results = hands.process(image_rgb)
          
          # Default coordinates (if no hand detected)
          latest_landmark_9 = {"x": None, "y": None, "z": None}

          # Draw hand landmarks
          if results.multi_hand_landmarks:
              for hand_landmarks in results.multi_hand_landmarks:
                  mp_drawing.draw_landmarks(
                      image, hand_landmarks,
                      mp_hands.HAND_CONNECTIONS,
                      mp_drawing_styles.get_default_hand_landmarks_style(),
                      mp_drawing_styles.get_default_hand_connections_style())
                  
              # Get XYZ of Landmark 9 (Middle Finger MCP)
              landmark_9 = hand_landmarks.landmark[9]
              latest_landmark_9 = {"x": landmark_9.x, "y": landmark_9.y, "z": landmark_9.z}

          # Flip the image for a selfie-view display
          image = cv2.flip(image, 1)

          # Encode frame for streaming
          _, buffer = cv2.imencode('.jpg', image)
          frame_bytes = buffer.tobytes()
          
          json_data = json.dumps(latest_landmark_9).encode("utf-8") 

          yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
          yield (b"--xyz\r\n"
                   b"Content-Type: application/json\r\n\r\n" + json_data + b"\r\n")
                   

  cap.release()
  
if __name__ == '__main__':
  generate_frames_local()
  # cv2.destroyAllWindows()