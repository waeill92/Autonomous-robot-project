import cv2

# Open webcam (0 is usually the default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Canny edge detection
    edges = cv2.Canny(gray, 100, 200)

    # Show original and edge-detected frames
    cv2.imshow('Original', frame)
    cv2.imshow('Edges', edges)

    # Exit loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
