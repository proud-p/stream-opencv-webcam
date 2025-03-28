from flask import Flask, Response
from hand_track import generate_frames

app = Flask(__name__)

@app.route('/video_feed')
def video_feed():
    """Serves video with XYZ coordinates embedded in HTTP headers."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/video_copy')
# def video_copy():
#     """Serves video with XYZ coordinates embedded in HTTP headers."""
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
# #TODO add a route for voice question - should be question, and newly received = True/false

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
    print("Video feed started at http://127.0.0.1:5000/video_feed")
