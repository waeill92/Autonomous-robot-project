import cv2
import time
import numpy as np
import serial
from ultralytics import YOLO
import RBG

# Define ROI as a simple rectangle (x, y, width, height)
ROI_RECT = (100, 100, 440, 280)  # x, y, w, h

def init(Digit_model=r"Models\\digit_det.pt", Object_model=r"Models\\best_openvino_model", serial_port="COM4", baudrate=112500):
    total_start = time.time()

    # Load models
    step_start = time.time()
    print("Loading models...")
    Dig_model = YOLO(Digit_model)
    Obj_model = YOLO(Object_model)
    step_end = time.time()
    print(f"Models loaded in {step_end - step_start:.3f} sec")

    # Warm-up with blank frame
    step_start = time.time()
    blank_frame = (255 * np.ones((640, 640, 3), dtype="uint8"))
    print("Warming up models on blank frame...")
    _ = Dig_model.predict(blank_frame)
    _ = Obj_model.predict(blank_frame)
    step_end = time.time()
    print(f"Warm-up done in {step_end - step_start:.3f} sec")

    # Initialize video capture
    step_start = time.time()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open camera.")
        return None, None, None, None
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    step_end = time.time()
    print(f"Video capture initialized in {step_end - step_start:.3f} sec")

    # Initialize serial
    step_start = time.time()
    try:
        ser = serial.Serial(serial_port, baudrate, timeout=1)
        step_end = time.time()
        print(f"Serial initialized on {serial_port} at {baudrate} baud in {step_end - step_start:.3f} sec")
    except Exception as e:
        print(f"Error: Could not open serial port {serial_port}: {e}")
        ser = None

    total_end = time.time()
    print(f"Total init process took {total_end - total_start:.3f} sec")

    return Dig_model, Obj_model, cap, ser

def apply_roi(frame, roi_rect):
    x, y, w, h = roi_rect
    roi_frame = frame[y:y+h, x:x+w]
    return roi_frame

def draw_roi_contour(frame, roi_rect):
    x, y, w, h = roi_rect
    contour_frame = frame.copy()
    cv2.rectangle(contour_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imshow("ROI Contour", contour_frame)
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyWindow("ROI Contour")
            break

def predict_digit_model(model, frame, conf=0.7, debug=False):
    start = time.time()
    results = model.predict(frame, conf=conf,imgsz=640, verbose=False)
    end = time.time()
    print(f"Digit_model detected {len(results[0].boxes)} objects in {end - start:.3f} sec")

    if len(results[0].boxes) == 0:
        return ""

    class_map = {0: '3', 1: '5', 2: '6', 3: '9'}

    confidences = results[0].boxes.conf
    classes = results[0].boxes.cls
    if len(confidences) > 0:
        max_idx = int(np.argmax(confidences))
        most_confident_digit = class_map.get(int(classes[max_idx].item()), '')
    else:
        most_confident_digit = class_map.get(int(classes[0].item()), '')

    if debug:
        annotated_frame = results[0].plot()
        cv2.imshow("Digit Model Debug", annotated_frame)
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyWindow("Digit Model Debug")
                break

    return most_confident_digit

def predict_object_model(model, frame, conf=0.7, debug=False):
    start = time.time()
    results = model.predict(frame, conf=conf,imgsz=640,verbose=False)
    end = time.time()
    print(f"Object_model detected {len(results[0].boxes)} objects in {end - start:.3f} sec")

    cube_count = 0
    pyramid_count = 0
    for cls in results[0].boxes.cls:
        if int(cls) == 0:
            cube_count += 1
        elif int(cls) == 1:
            pyramid_count += 1

    output_string = f"{pyramid_count} {cube_count}"

    if debug:
        annotated_frame = results[0].plot()
        cv2.imshow("Object Model Debug", annotated_frame)
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyWindow("Object Model Debug")
                break

    return output_string

def send_uart_string(ser, data_str):
    if ser is not None and ser.is_open:
        ser.write(f"{data_str}\n".encode())
        print(f"Sent via UART: {data_str}")
    else:
        print("Error: Serial port not initialized or closed.")

def main():
    Dig_model, Obj_model, cap, ser = init()
    if cap is None or ser is None:
        return

    print("Waiting for UART messages...")

    while True:
        if ser.in_waiting > 0:
            msg = ser.readline().decode().strip()
            print(f"Received UART message: {msg}")

            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to grab frame.")
                continue

            #draw_roi_contour(frame, ROI_RECT)

            if msg.lower() == "digit":
                digit_result = predict_digit_model(Dig_model, frame)
                send_uart_string(ser, digit_result)
                print(f"Digit result: {digit_result}")
            elif msg.lower() == "object":
                object_result = predict_object_model(Obj_model, frame)
                send_uart_string(ser, object_result)
                print(f"Object result: {object_result}")
            elif msg.lower() == "color":
                color_result = RBG.detect_color(frame)
                send_uart_string(ser, color_result)
                print(f"Color result: {color_result}") 
            else:
                send_uart_string(ser, "ERROR")
                print("Unknown command, ignoring.")
        else:
            time.sleep(0.01)

    cap.release()
    ser.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()