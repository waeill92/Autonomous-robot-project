import cv2
import numpy as np

# Open webcam
cap = cv2.VideoCapture(0)

# HSV ranges
lower_range_blue = np.array([97, 85, 76])
upper_range_blue = np.array([119, 255, 255])

lower_range_green = np.array([50, 54, 0])
upper_range_green = np.array([89, 213, 255])

lower_range_red1 = np.array([0, 190, 0])
upper_range_red1 = np.array([5, 255, 153])
lower_range_red2 = np.array([174, 99, 0])
upper_range_red2 = np.array([179, 255, 255])

# -------------------- COLOR FUNCTIONS -------------------- #
def blue(image):
    max_area = 0
    x = y = w = h = 0
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_range_blue, upper_range_blue)
    _, mask_bin = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(mask_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for c in cnts:
        area = cv2.contourArea(c)
        if area > max_area:
            max_area = area
            x, y, w, h = cv2.boundingRect(c)

    if max_area > 0:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(image, "DETECT", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    return max_area

def green(image):
    max_area = 0
    x = y = w = h = 0
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_range_green, upper_range_green)
    _, mask_bin = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(mask_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for c in cnts:
        area = cv2.contourArea(c)
        if area > max_area:
            max_area = area
            x, y, w, h = cv2.boundingRect(c)

    if max_area > 0:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, "DETECT", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    return max_area

def red(image):
    max_area = 0
    x = y = w = h = 0
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, lower_range_red1, upper_range_red1)
    mask2 = cv2.inRange(hsv, lower_range_red2, upper_range_red2)
    mask_combined = cv2.bitwise_or(mask1, mask2)

    cnts, _ = cv2.findContours(mask_combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for c in cnts:
        area = cv2.contourArea(c)
        if area > max_area:
            max_area = area
            x, y, w, h = cv2.boundingRect(c)

    if max_area > 0:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
    return max_area

# -------------------- MAIN COLOR DETECTION -------------------- #
def detect_color(frame):
    red_count = 0
    green_count = 0
    blue_count = 0

    # Take multiple samples to reduce noise
    for _ in range(10):
        r_area = red(frame)
        #g_area = green(frame)
        b_area = blue(frame)
        #max_area = max(r_area, g_area, b_area)
        max_area = max(r_area,b_area)
        if max_area == r_area:
            red_count += 1
        # elif max_area == g_area:
        #     green_count += 1
        else:
            blue_count += 1

    #max_count = max(red_count, green_count, blue_count)
    max_count = max(red_count,blue_count)

    if max_count == red_count:
        return "r"
    # elif max_count == green_count:
    #     return "green"
    else:
        return "b"

# -------------------- RUN -------------------- #
# if __name__ == "__main__":
#     color_detected = detect_color()
#     print(color_detected)






# import cv2
# import numpy as np

# # Open webcam
# cap = cv2.VideoCapture(0)

# # HSV ranges for colors
# COLOR_RANGES = {
#     "blue": [(np.array([97, 85, 76]), np.array([119, 255, 255]))],
#     "green": [(np.array([50, 54, 0]), np.array([89, 213, 255]))],
#     "red": [
#         (np.array([0, 190, 0]), np.array([5, 255, 153])),
#         (np.array([174, 99, 0]), np.array([179, 255, 255]))
#     ]
# }

# # Rectangle colors for drawing (BGR)
# DRAW_COLORS = {
#     "blue": (255, 0, 0),
#     "green": (0, 255, 0),
#     "red": (0, 0, 255)
# }

# # -------------------- GENERIC COLOR DETECTION -------------------- #
# def detect_color_area(image, color_name):
#     hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
#     # Combine masks for multi-range colors
#     mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
#     for lower, upper in COLOR_RANGES[color_name]:
#         mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower, upper))
    
#     cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
#     max_area = 0
#     rect = None
#     for c in cnts:
#         area = cv2.contourArea(c)
#         if area > max_area:
#             max_area = area
#             rect = cv2.boundingRect(c)
    
#     if rect:
#         x, y, w, h = rect
#         cv2.rectangle(image, (x, y), (x + w, y + h), DRAW_COLORS[color_name], 2)
#         cv2.putText(image, color_name.upper(), (x, y - 10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, DRAW_COLORS[color_name], 2)
    
#     return max_area

# # -------------------- MAIN COLOR DETECTION -------------------- #
# def detect_dominant_color(samples=20):
#     ret, frame = cap.read()
#     if not ret:
#         print("Failed to grab frame")
#         return None
    
#     counts = {"red": 0, "green": 0, "blue": 0}
    
#     for _ in range(samples):
#         areas = {color: detect_color_area(frame.copy(), color) for color in COLOR_RANGES}
#         dominant = max(areas, key=areas.get)
#         counts[dominant] += 1
    
#     cap.release()
#     return max(counts, key=counts.get)

# # -------------------- RUN -------------------- #
# if __name__ == "__main__":
#     dominant_color = detect_dominant_color()
#     print(dominant_color)
