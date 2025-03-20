import cv2
import threading
from flask import Flask, Response
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from hand_track import generate_frames
app = Flask(__name__)
video = cv2.VideoCapture(0)  # Change to 1 if using an external camera

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
    print("Video feed started at http://127.0.0.1:5000/video_feed")
