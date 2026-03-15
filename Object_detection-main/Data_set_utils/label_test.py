# verify_yolo_labels.py
import os
import random
import cv2
import matplotlib.pyplot as plt

# Path to your dataset
DATASET_DIR = "Datasets/digits_dataset_det"
SUBSET = "train"  # choose "train", "val", or "test"

images_dir = os.path.join(DATASET_DIR, "images", SUBSET)
labels_dir = os.path.join(DATASET_DIR, "labels", SUBSET)

# pick random samples
all_images = [f for f in os.listdir(images_dir) if f.endswith(".png")]
random.shuffle(all_images)

def load_labels(label_path, img_w, img_h):
    boxes = []
    with open(label_path, "r") as f:
        for line in f:
            cls, x_c, y_c, w, h = map(float, line.strip().split())
            cls = int(cls)
            x_c *= img_w
            y_c *= img_h
            w *= img_w
            h *= img_h
            x1 = int(x_c - w / 2)
            y1 = int(y_c - h / 2)
            x2 = int(x_c + w / 2)
            y2 = int(y_c + h / 2)
            boxes.append((cls, x1, y1, x2, y2))
    return boxes

# show some random images
for img_name in all_images[:10]:  # show first 10
    img_path = os.path.join(images_dir, img_name)
    label_path = os.path.join(labels_dir, img_name.replace(".png", ".txt"))

    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    if os.path.exists(label_path):
        boxes = load_labels(label_path, w, h)
        for cls, x1, y1, x2, y2 in boxes:
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, str(cls), (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(4, 4))
    plt.imshow(img_rgb)
    plt.axis("off")
    plt.title(img_name)
    plt.show()
