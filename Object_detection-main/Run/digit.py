import cv2
from ultralytics import YOLO

# --- 1️⃣ Load your trained YOLO classification model ---
model = YOLO("digit.pt")  # change path if needed

# --- 2️⃣ Open webcam (0 = default camera) ---
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# --- 3️⃣ Define ROI size ---
roi_w, roi_h = 200, 200  # width and height of the ROI

# --- 4️⃣ Loop through frames ---
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame_h, frame_w = frame.shape[:2]

    # --- Center the ROI in the frame ---
    roi_x = (frame_w - roi_w) // 2
    roi_y = (frame_h - roi_h) // 2

    # Draw rectangle on original frame to show ROI
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x+roi_w, roi_y+roi_h), (0,255,0), 2)

    # Crop the ROI for classification
    roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]

    # YOLO expects RGB
    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

    # --- Run classification on ROI ---
    results = model(roi_rgb, imgsz=224)

    # --- Get top predicted class ---
    pred_idx = results[0].probs.top1
    pred_class = results[0].names[pred_idx]
    pred_prob = float(results[0].probs.top1conf)

    # --- Print result ---
    print(f"Predicted: {pred_class} ({pred_prob:.2f})")

    # --- Draw result on frame ---
    text = f"{pred_class}: {pred_prob:.2f}"
    cv2.putText(frame, text, (roi_x, roi_y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                1.0, (0, 0, 255), 2)

    # --- Display frame ---
    cv2.imshow("YOLO Classification Live", frame)

    # --- Exit on 'q' key ---
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()
