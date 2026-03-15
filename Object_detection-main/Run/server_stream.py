from flask import Flask, render_template_string, Response
import cv2

app = Flask(__name__)

# OpenCV video capture
cap = cv2.VideoCapture(0)  # 0 = default webcam

# Simple HTML template for the page
HTML_PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Webcam Stream</title>
  <style>
    body{
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial;
      margin:0; padding:1rem;
      display:flex; flex-direction:column; align-items:center;
      background:#0f1720; color:#e6eef8;
    }
    h1{margin:0 0 0.5rem 0;}
    #stream{max-width:100%; height:auto; border-radius:8px; box-shadow:0 6px 20px rgba(0,0,0,0.6);}
    .info{margin-top:0.5rem; font-size:0.9rem; opacity:0.9;}
  </style>
</head>
<body>
  <h1>Webcam stream</h1>
  <p class="info">Live Camera Feed</strong></p>
  <img id="stream" src="/video_feed" alt="Live webcam stream" />
</body>
</html>
"""

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        # === Apply your changes here ===
        # Example: convert to grayscale
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Convert grayscale back to 3 channels for proper streaming
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Stream as multipart response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
