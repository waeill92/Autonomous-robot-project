from ultralytics import YOLO
import cv2
import numpy as np
import glob
import os

# 1️⃣ Path to your directory of images
image_dir = r"C:\Users\kfakh\Downloads\images"  # <-- change to your folder
image_paths = glob.glob(os.path.join(image_dir, "*.*"))  # all files
image_paths = [p for p in image_paths]

if not image_paths:
    print("No images found in", image_dir)
    exit()

# 2️⃣ Load model
model = YOLO(r"C:\Users\kfakh\Downloads\best.pt")  # change path if needed

# 3️⃣ Loop over images
for img_path in image_paths:
    print("Processing:", img_path)

    # Read image
    frame = cv2.imread(img_path)

    # 4️⃣ Run prediction on this image
    results = model.predict(source=frame, imgsz=640, conf=0.25, verbose=False)

    # 5️⃣ Get YOLO's annotated image (BGR)
    annotated_frame = results[0].plot()

    # 6️⃣ (Optional) Draw our own contour rectangles on top
    for box in results[0].boxes.xyxy:  # xyxy format: x1,y1,x2,y2
        x1, y1, x2, y2 = map(int, box)
        pts = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(annotated_frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

    # 7️⃣ Show annotated image with OpenCV
    window_name = f"YOLO - {os.path.basename(img_path)}"
    cv2.imshow(window_name, annotated_frame)

    print("Press any key to continue to the next image, or 'q' to quit.")
    key = cv2.waitKey(0) & 0xFF
    cv2.destroyWindow(window_name)
    if key == ord('q'):
        break

# 8️⃣ Cleanup
cv2.destroyAllWindows()
