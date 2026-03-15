import cv2
from ultralytics import YOLO

# Load YOLOv11s classification model
model = YOLO("best (2).pt")  # Replace with your model path

# Open webcam
cap = cv2.VideoCapture(0)

# Define ROI size (width and height)
ROI_WIDTH, ROI_HEIGHT = 224, 224  # same as model input

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_h, frame_w = frame.shape[:2]

    # Compute top-left corner of ROI (centered)
    x1 = (frame_w - ROI_WIDTH) // 2
    y1 = (frame_h - ROI_HEIGHT) // 2
    x2 = x1 + ROI_WIDTH
    y2 = y1 + ROI_HEIGHT

    # Crop ROI for classification
    roi = frame[y1:y2, x1:x2]

    # Perform inference on ROI
    results = model(roi)

    # Get top-1 class and confidence
    pred_class_id = results[0].probs.top1
    confidence = float(results[0].probs.top1conf)
    label = results[0].names[pred_class_id]

    # Draw ROI rectangle on original frame
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Display classification result above the ROI
    display_text = f"{label}: {confidence:.2f}"
    cv2.putText(frame, display_text, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Show frame
    cv2.imshow("YOLOv11s Classification ROI", frame)

    # Exit on ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
