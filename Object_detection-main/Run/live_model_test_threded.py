from ultralytics import YOLO
import cv2
import numpy as np
import time
import threading

# 1️⃣ Load your trained model
model = YOLO("best_int8_openvino_model")  # path to your exported OpenVINO model

# 2️⃣ Open webcam (0 = default camera)
cap = cv2.VideoCapture(r"images\test2.mp4")
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # try to limit internal buffer

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Shared variable for latest frame
latest_frame = [None]
running = True

# 3️⃣ Frame-grabbing thread
def grab_frames():
    while running:
        ret, frame = cap.read()
        if not ret:
            continue
        latest_frame[0] = frame

threading.Thread(target=grab_frames, daemon=True).start()

# 4️⃣ Main processing loop
while True:
    frame = latest_frame[0]
    if frame is None:
        continue  # wait until we have a frame

    # 5️⃣ Run YOLO on the frame
    start = time.time()
    results = model.predict(source=frame, imgsz=640, conf=0.25, verbose=False)
    print("Inference time:", time.time() - start)

    # 6️⃣ Get annotated frame (boxes + labels drawn by YOLO)
    annotated_frame = results[0].plot()  # OpenCV BGR image

    # 7️⃣ Count pyramids and cubes
    pyramid_count = 0
    cube_count = 0
    for cls_id in results[0].boxes.cls:  # class IDs of detected objects
        cls_id = int(cls_id)
        class_name = model.names[cls_id]  # get the label name
        if class_name.lower() == "pyramid":
            pyramid_count += 1
        elif class_name.lower() == "cube":
            cube_count += 1

    # 8️⃣ Draw bounding boxes (optional)
    for box in results[0].boxes.xyxy:
        x1, y1, x2, y2 = map(int, box)
        pts = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]],
                       np.int32).reshape((-1, 1, 2))
        cv2.polylines(annotated_frame, [pts], isClosed=True,
                      color=(0, 255, 0), thickness=2)

    # 9️⃣ Display counts on the frame
    cv2.putText(annotated_frame, f"Pyramids: {pyramid_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(annotated_frame, f"Cubes: {cube_count}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # 🔟 Show the annotated frame
    cv2.imshow("YOLO Live", annotated_frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 1️⃣1️⃣ Cleanup
running = False
cap.release()
cv2.destroyAllWindows()
