from ultralytics import YOLO
import cv2
import numpy as np
import requests
import os
import matplotlib.pyplot as plt

# 1️⃣ Download example image
img_name = r"images\download (1).jpeg"

# 2️⃣ Load model
model = YOLO(r"best.pt")  # change path if needed

# 3️⃣ Run prediction
results = model.predict(source=img_name, imgsz=640, conf=0.25)

# 4️⃣ Annotated image from YOLO (BGR)
annotated = results[0].plot()

# Convert BGR → RGB for matplotlib
annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

# 5️⃣ Manually draw contour rectangles on a copy of the original image
img = cv2.imread(img_name)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

for box in results[0].boxes.xyxy:  # xyxy format: x1,y1,x2,y2
    x1, y1, x2, y2 = map(int, box)
    pts = np.array([[x1,y1],[x2,y1],[x2,y2],[x1,y2]], np.int32)
    pts = pts.reshape((-1,1,2))
    cv2.polylines(img_rgb, [pts], isClosed=True, color=(0,255,0), thickness=2)

# 6️⃣ Show both images with matplotlib
plt.figure(figsize=(16,8))

plt.subplot(1,2,1)
plt.imshow(annotated_rgb)
plt.title("YOLO built-in annotations")
plt.axis('off')

plt.subplot(1,2,2)
plt.imshow(img_rgb)
plt.title("Original + contour rectangles")
plt.axis('off')

plt.tight_layout()
plt.show()
