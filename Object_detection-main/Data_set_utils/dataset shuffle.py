import os
import random
import shutil

# ---------------- CONFIG ----------------
# Path to your dataset
DATASET_PATH = r"C:\Users\kfakh\Downloads\data_train_ras"  # adjust to your dataset root folder
IMAGES_DIR = os.path.join(DATASET_PATH, "images", "train")
LABELS_DIR = os.path.join(DATASET_PATH, "labels", "train")

# Validation fraction (e.g. 0.2 = 20% validation)
VAL_RATIO = 0.2
RANDOM_SEED = 42
# ----------------------------------------

# New directories for val split
IMAGES_VAL_DIR = os.path.join(DATASET_PATH, "images", "val")
LABELS_VAL_DIR = os.path.join(DATASET_PATH, "labels", "val")

# Make sure val directories exist
os.makedirs(IMAGES_VAL_DIR, exist_ok=True)
os.makedirs(LABELS_VAL_DIR, exist_ok=True)

# Collect all image files
image_files = [f for f in os.listdir(IMAGES_DIR)
               if f.lower().endswith((".jpg", ".jpeg", ".png"))]

# Shuffle for randomness
random.seed(RANDOM_SEED)
random.shuffle(image_files)

# Compute split index
n_total = len(image_files)
n_val = int(n_total * VAL_RATIO)

val_files = image_files[:n_val]
print(f"Found {n_total} images, moving {n_val} to validation set.")

for img_name in val_files:
    # Move image
    src_img = os.path.join(IMAGES_DIR, img_name)
    dst_img = os.path.join(IMAGES_VAL_DIR, img_name)
    shutil.move(src_img, dst_img)

    # Move label (same basename with .txt)
    base = os.path.splitext(img_name)[0]
    label_name = base + ".txt"
    src_label = os.path.join(LABELS_DIR, label_name)
    dst_label = os.path.join(LABELS_VAL_DIR, label_name)
    if os.path.exists(src_label):
        shutil.move(src_label, dst_label)
    else:
        print(f"Warning: no label file found for {img_name}")
print("Done splitting dataset.")
