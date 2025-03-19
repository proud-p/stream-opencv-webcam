import cv2
import threading
from flask import Flask, Response

app = Flask(__name__)
video = cv2.VideoCapture(0)  # Change to 1 if using an external camera

def generate_frames():
    while True:
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)  # Change port if needed
    print("Video feed started at http://127.0.0.1:5000/video_feed")