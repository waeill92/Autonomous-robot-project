from flask import Flask, Response
import cv2

app = Flask(__name__)

# Initialize webcam (0 = default camera)
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield frame in HTTP response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Get your computer's IP on the local network, e.g. 192.168.1.5
    # Run the server on that IP and port 5000
    app.run(host='0.0.0.0', port=5000)
