# gen_printed_digits_detection_yolo_maskbbox.py
import os
import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import uuid

OUT = "digits_dataset_det"
fonts_dir = "fonts"  # put some .ttf files here
IMG_SIZE = 224      # final image size used for training
BASE_SIZE = 640     # central crop size (we will crop this after transforms)
PAD_RATIO = 0.6
PAD = int(BASE_SIZE * PAD_RATIO)
PADDED_SIZE = BASE_SIZE + 2 * PAD

# mapping digits to class IDs
digit_to_class = {3: 0, 5: 1, 6: 2, 9: 3}

# create folders
for folder in ["images/train", "images/val", "images/test",
               "labels/train", "labels/val", "labels/test"]:
    os.makedirs(os.path.join(OUT, folder), exist_ok=True)


def bbox_of_mask(arr, thresh=240):
    """Return bounding box (xmin,ymin,xmax,ymax) of pixels < thresh. Return None if none."""
    ys, xs = np.where(arr < thresh)
    if xs.size == 0 or ys.size == 0:
        return None
    xmin, xmax = int(xs.min()), int(xs.max())
    ymin, ymax = int(ys.min()), int(ys.max())
    return xmin, ymin, xmax, ymax


def render_digit_on_padded_canvas(digit, font_path, padded_size=PADDED_SIZE, base_size=BASE_SIZE):
    """Draw digit randomly inside the central BASE_SIZE area on a padded canvas with random bright bg."""
    bg_val = random.randint(200, 255)
    canvas = Image.new("L", (padded_size, padded_size), color=bg_val)
    draw = ImageDraw.Draw(canvas)

    # choose font size that fits inside base_size
    for _ in range(12):
        font_size = int(base_size * random.uniform(0.25, 0.55))
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), str(digit), font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if w < base_size * 0.95 and h < base_size * 0.95:
            break

    # position randomly inside central area with margin
    margin = int(base_size * 0.03)
    crop_x0 = PAD + margin
    crop_y0 = PAD + margin
    crop_x1 = PAD + base_size - margin - w
    crop_y1 = PAD + base_size - margin - h
    if crop_x1 < crop_x0:
        crop_x1 = crop_x0
    if crop_y1 < crop_y0:
        crop_y1 = crop_y0

    pos_x = random.randint(crop_x0, crop_x1)
    pos_y = random.randint(crop_y0, crop_y1)

    draw.text((pos_x, pos_y), str(digit), font=font, fill=0)
    return canvas, (pos_x, pos_y, w, h), bg_val


def simulate_y_rotation_arr(arr, angle=None, bg_val=255):
    """Apply Y-rotation perspective with EXACT depth = w * 0.4 (preserved)."""
    h, w = arr.shape
    if angle is None:
        angle = random.uniform(-35, 35)
    depth = w * 0.4  # kept as requested
    shift = np.tan(np.radians(angle)) * depth
    if angle > 0:
        src = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        dst = np.float32([[shift, 0], [w - shift, 0], [0, h], [w, h]])
    else:
        src = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        dst = np.float32([[0, 0], [w, 0], [-shift, h], [w + shift, h]])
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(arr, M, (w, h), borderValue=int(bg_val))
    return warped


def random_geo_photometric_arr(arr, bg_val=255):
    """Apply rotation + small perspective jitter + photometric changes (no pts needed here)."""
    h, w = arr.shape

    # affine rotation
    ang = random.uniform(-15, 15)
    M_aff = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
    arr = cv2.warpAffine(arr, M_aff, (w, h), borderValue=int(bg_val))

    # small perspective jitter
    pts1 = np.float32([[0, 0], [w - 1, 0], [0, h - 1], [w - 1, h - 1]])
    delta = 0.08 * min(w, h)
    pts2 = pts1 + np.random.uniform(-delta, delta, pts1.shape).astype(np.float32)
    M2 = cv2.getPerspectiveTransform(pts1, pts2)
    arr = cv2.warpPerspective(arr, M2, (w, h), borderValue=int(bg_val))

    # photometric
    alpha = random.uniform(0.7, 1.3)
    beta = random.uniform(-30, 30)
    arr = np.clip(arr.astype(np.float32) * alpha + beta, 0, 255).astype(np.uint8)

    # optional blur/noise/sharpen
    if random.random() < 0.25:
        arr = cv2.GaussianBlur(arr, (3, 3), 0)
    if random.random() < 0.1:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        arr = cv2.filter2D(arr, -1, kernel)
    if random.random() < 0.25:
        noise = np.random.normal(0, 10, arr.shape).astype(np.int16)
        arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # small bg brightness shift
    bg_shift = random.randint(-30, 30)
    arr = np.clip(arr.astype(np.int16) + bg_shift, 0, 255).astype(np.uint8)

    return arr


def expand_bbox(xmin, ymin, xmax, ymax, expand_px, limit_w, limit_h):
    xmin_e = max(0, int(xmin - expand_px))
    ymin_e = max(0, int(ymin - expand_px))
    xmax_e = min(limit_w - 1, int(xmax + expand_px))
    ymax_e = min(limit_h - 1, int(ymax + expand_px))
    return xmin_e, ymin_e, xmax_e, ymax_e


def generate(out_dir,
             samples_per_digit=500,
             digits=[3, 5, 6, 9],
             attempts_per_sample=12,
             mask_thresh=245,
             expand_px=3,
             shuffle_output=True,
             debug=False):
    fonts = [os.path.join(fonts_dir, f) for f in os.listdir(fonts_dir) if f.lower().endswith(".ttf")]
    if not fonts:
        raise Exception("Put some .ttf fonts in ./fonts/")

    counts = {d: 0 for d in digits}

    for d in digits:
        for i in range(samples_per_digit):
            font_path = random.choice(fonts)
            accepted = False
            for attempt in range(attempts_per_sample):
                pil_canvas, orig_bbox, bg_val = render_digit_on_padded_canvas(d, font_path)
                arr = np.array(pil_canvas)  # padded canvas

                # apply Y-rotation (preserve depth param)
                arr = simulate_y_rotation_arr(arr, angle=None, bg_val=bg_val)

                # apply other transforms + photometric
                arr = random_geo_photometric_arr(arr, bg_val=bg_val)

                # compute mask bbox from transformed image (this is the key)
                mask_bbox = bbox_of_mask(arr, thresh=mask_thresh)
                if mask_bbox is None:
                    continue
                xmin, ymin, xmax, ymax = mask_bbox

                # optional expand (cover blur/antialiasing)
                xmin_e, ymin_e, xmax_e, ymax_e = expand_bbox(xmin, ymin, xmax, ymax, expand_px, PADDED_SIZE, PADDED_SIZE)

                # central crop bounds in padded coords
                crop_x0 = PAD
                crop_y0 = PAD
                crop_x1 = PAD + BASE_SIZE - 1
                crop_y1 = PAD + BASE_SIZE - 1

                # check mask bbox fully inside central crop (with tiny margin)
                margin_px = 2
                if xmin_e >= crop_x0 + margin_px and ymin_e >= crop_y0 + margin_px and \
                   xmax_e <= crop_x1 - margin_px and ymax_e <= crop_y1 - margin_px:
                    # accept
                    accepted = True
                    xmin_use, ymin_use, xmax_use, ymax_use = xmin_e, ymin_e, xmax_e, ymax_e
                    break

            if not accepted:
                # fallback: render a centered safe one without transforms
                pil_canvas, orig_bbox, bg_val = render_digit_on_padded_canvas(d, font_path)
                arr = np.array(pil_canvas)
                mask_bbox = bbox_of_mask(arr, thresh=mask_thresh)
                if mask_bbox is None:
                    # surprising — set whole central crop
                    xmin_use, ymin_use, xmax_use, ymax_use = PAD, PAD, PAD + BASE_SIZE - 1, PAD + BASE_SIZE - 1
                else:
                    xmin, ymin, xmax, ymax = mask_bbox
                    xmin_use, ymin_use, xmax_use, ymax_use = expand_bbox(xmin, ymin, xmax, ymax, expand_px, PADDED_SIZE, PADDED_SIZE)

            # crop the central BASE_SIZE area
            crop_x0 = PAD
            crop_y0 = PAD
            crop = arr[crop_y0:crop_y0 + BASE_SIZE, crop_x0:crop_x0 + BASE_SIZE]

            # compute bbox relative to crop (0..BASE_SIZE-1)
            rel_xmin = xmin_use - crop_x0
            rel_ymin = ymin_use - crop_y0
            rel_xmax = xmax_use - crop_x0
            rel_ymax = ymax_use - crop_y0

            # sanitize
            rel_xmin = float(max(0, min(rel_xmin, BASE_SIZE - 1)))
            rel_ymin = float(max(0, min(rel_ymin, BASE_SIZE - 1)))
            rel_xmax = float(max(0, min(rel_xmax, BASE_SIZE - 1)))
            rel_ymax = float(max(0, min(rel_ymax, BASE_SIZE - 1)))

            rel_w = max(1.0, rel_xmax - rel_xmin)
            rel_h = max(1.0, rel_ymax - rel_ymin)
            rel_xc = rel_xmin + rel_w / 2.0
            rel_yc = rel_ymin + rel_h / 2.0

            # normalized YOLO coords (relative to BASE_SIZE)
            x_center_n = rel_xc / BASE_SIZE
            y_center_n = rel_yc / BASE_SIZE
            w_n = rel_w / BASE_SIZE
            h_n = rel_h / BASE_SIZE

            # resize crop to IMG_SIZE
            crop_resized = cv2.resize(crop, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_LANCZOS4)

            # folder split
            r = random.random()
            subset = "train" if r < 0.7 else ("val" if r < 0.9 else "test")

            idx = counts[d]
            base_name = f"{d}_{idx:05d}"
            img_path = os.path.join(out_dir, "images", subset, base_name + ".png")
            label_path = os.path.join(out_dir, "labels", subset, base_name + ".txt")

            Image.fromarray(crop_resized).save(img_path)

            # debug draw optional: saves *_dbg.png next to image
            if debug:
                vis = cv2.cvtColor(crop_resized.copy(), cv2.COLOR_GRAY2BGR)
                bx1 = int((x_center_n - w_n / 2) * IMG_SIZE)
                by1 = int((y_center_n - h_n / 2) * IMG_SIZE)
                bx2 = int((x_center_n + w_n / 2) * IMG_SIZE)
                by2 = int((y_center_n + h_n / 2) * IMG_SIZE)
                cv2.rectangle(vis, (bx1, by1), (bx2, by2), (0, 255, 0), 2)
                cv2.putText(vis, f"{digit_to_class[d]}", (max(4, bx1), max(12, by1 - 6)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.imwrite(img_path.replace(".png", "_dbg.png"), vis)

            with open(label_path, "w") as f:
                f.write(f"{digit_to_class[d]} {x_center_n:.6f} {y_center_n:.6f} {w_n:.6f} {h_n:.6f}\n")

            counts[d] += 1

    # shuffle properly (two-pass)
    if shuffle_output:
        for subset in ["train", "val", "test"]:
            img_dir = os.path.join(out_dir, "images", subset)
            label_dir = os.path.join(out_dir, "labels", subset)
            files = [f for f in os.listdir(img_dir) if f.endswith(".png")]
            random.shuffle(files)
            # rename to temp
            for i, fname in enumerate(files):
                tmp = f"tmp_{i:05d}.png"
                os.rename(os.path.join(img_dir, fname), os.path.join(img_dir, tmp))
                os.rename(os.path.join(label_dir, fname.replace(".png", ".txt")),
                          os.path.join(label_dir, tmp.replace(".png", ".txt")))
            # rename to final
            tmp_files = sorted([f for f in os.listdir(img_dir) if f.startswith("tmp_")])
            for new_idx, tmp in enumerate(tmp_files):
                new_name = f"{new_idx:05d}.png"
                os.rename(os.path.join(img_dir, tmp), os.path.join(img_dir, new_name))
                os.rename(os.path.join(label_dir, tmp.replace(".png", ".txt")),
                          os.path.join(label_dir, new_name.replace(".png", ".txt")))


if __name__ == "__main__":
    # set debug=True to create *_dbg.png visualization images
    generate(OUT, samples_per_digit=200, digits=[3, 5, 6, 9], attempts_per_sample=12,
             mask_thresh=245, expand_px=3, shuffle_output=True, debug=True)
    print("Done — dataset generated in", OUT)
