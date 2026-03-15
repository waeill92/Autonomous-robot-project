from ultralytics import YOLO
import cv2
import numpy as np
import time 

# 1️⃣ Load your trained model
model = YOLO(r"Models\best_openvino_model")  # change path to your weights

# 2️⃣ Open webcam (0 = default camera)
cap = cv2.VideoCapture(0)  # or put an RTSP/USB camera URL instead

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# 3️⃣ Loop through frames
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # 4️⃣ Run YOLO on the frame
    start=time.time()
    #frame=cv2.resize(frame,(640,640))
    results = model.predict(source=frame, imgsz=640, conf=0.5, verbose=False)
    print(time.time()-start)
    # 5️⃣ Get annotated frame (boxes + labels drawn by YOLO)
    annotated_frame = results[0].plot()  # OpenCV BGR image

    # 6️⃣ Count pyramids and cubes
    pyramid_count = 0
    cube_count = 0
    for cls_id in results[0].boxes.cls:  # class IDs of detected objects
        cls_id = int(cls_id)
        class_name = model.names[cls_id]  # get the label name
        if class_name.lower() == "pyramid":
            pyramid_count += 1
        elif class_name.lower() == "cube":
            cube_count += 1

    # 7️⃣ Draw bounding boxes (optional, your existing code)
    for box in results[0].boxes.xyxy:
        x1, y1, x2, y2 = map(int, box)
        pts = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], np.int32).reshape((-1,1,2))
        cv2.polylines(annotated_frame, [pts], isClosed=True, color=(0,255,0), thickness=2)

    # 8️⃣ Display counts on the frame
    cv2.putText(annotated_frame, f"Pyramids: {pyramid_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(annotated_frame, f"Cubes: {cube_count}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # 9️⃣ Show the annotated frame
    cv2.imshow("YOLO Live", annotated_frame)

    # 🔟 Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 1️⃣1️⃣ Cleanup
cap.release()
cv2.destroyAllWindows()
