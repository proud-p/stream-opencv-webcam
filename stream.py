from flask import Flask, Response, jsonify
import json
from hand_track import generate_frames

app = Flask(__name__)

# Global variable to store the latest landmark data
latest_landmark_9 = {"x": None, "y": None, "z": None}

@app.route('/video_feed')
def video_feed():
    """Extracts and streams only video frames."""
    def video_generator():
        for chunk in generate_frames():
            if chunk.startswith(b"--frame"):
                yield chunk  # Only send video frames
    return Response(video_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/landmark_9')
def get_landmark_9():
    """Returns the latest XYZ coordinates as JSON."""
    global latest_landmark_9

    # Fetch a new frame until we get an XYZ update
    for chunk in generate_frames():
        if chunk.startswith(b"--xyz"):
            json_data = chunk.split(b"\r\n\r\n")[1]
            latest_landmark_9 = json.loads(json_data.decode("utf-8"))
            # print("HI")

    return jsonify(latest_landmark_9)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
    print("Video feed started at http://127.0.0.1:5000/video_feed")
    print("XYZ Data available at http://127.0.0.1:5000/landmark_9")
