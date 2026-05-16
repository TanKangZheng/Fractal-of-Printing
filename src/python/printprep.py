# Third-Party Packages
import numpy as np
from PIL import Image, ImageEnhance, ImageOps
import cv2
from cv2 import dnn_superres

# Python Packages
import os
import sys

# --- CONFIG --------------------------------------------------

MODEL_FILE = "FSRCNN_x2.pb"
MODEL_NAME = "fsrcnn"
SCALE = 2

# -------------------------------------------------------------

def boost_saturation(folder, factor=1.3, log_func=print):
    """
    factor = 1.0 -> no change
    factor > 1.0 -> more saturation
    """
    for filename in os.listdir(folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            path = os.path.join(folder, filename)

            with Image.open(path).convert("RGB") as img:
                enhancer = ImageEnhance.Color(img)
                saturated = enhancer.enhance(factor)
                saturated.save(path)

            log_func(f"Saturation boosted: {filename}")

def boost_uniform_vibrancy(folder, factor=1.25, log_func=print):
    """
    factor = 1.0  -> no change
    factor = 1.2+ -> stronger color
    """

    for filename in os.listdir(folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            path = os.path.join(folder, filename)

            img = Image.open(path).convert("RGB")
            hsv = img.convert("HSV")
            hsv_arr = np.array(hsv).astype(float)

            # Boost saturation channel uniformly
            hsv_arr[:, :, 1] *= factor
            hsv_arr[:, :, 1] = np.clip(hsv_arr[:, :, 1], 0, 255)

            boosted = Image.fromarray(hsv_arr.astype("uint8"), "HSV").convert("RGB")
            boosted.save(path)

            log_func(f"Uniform vibrancy boosted: {filename}")

def add_border(folder, border_ratio=0.04, log_func = print):
    """
    border_ratio = percentage of the shortest image side
    0.04 ≈ 1/8 inch on a 63x88mm template
    """

    for filename in os.listdir(folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            path = os.path.join(folder, filename)

            img = Image.open(path).convert("RGBA")

            # Replace fully transparent pixels with black
            pixels = img.getdata()
            img.putdata([
                (0, 0, 0, 255) if p[3] == 0 else p
                for p in pixels
            ])

            w, h = img.size
            border_pixels = int(min(w, h) * border_ratio)

            bordered = ImageOps.expand(
                img,
                border=border_pixels,
                fill="black"
            )

            out_path = os.path.join(folder, filename)
            bordered.save(out_path, "PNG")
            log_func(f"Border added: {filename}")

def upscale_bordered(folder, log_func = print):

    # Load super-resolution model
    sr = dnn_superres.DnnSuperResImpl_create()
    sr.readModel(resource_path(os.path.join("pb", MODEL_FILE)))
    sr.setModel(MODEL_NAME, SCALE)

    # Get list of images
    image_files = [
        f for f in os.listdir(folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]

    # Process images
    for filename in image_files:
        log_func(f"Upscaling {filename}...")
        in_file = os.path.join(folder, filename)
        img = cv2.imread(in_file)

        # Upscale using FSRCNN x2
        upscaled = sr.upsample(img)

        # Save output as PNG
        out_file = os.path.join(folder, in_file)
        cv2.imwrite(out_file, upscaled)
        log_func(f"Upscale completed: {filename}...")

def resource_path(relative_path):
    # Get the correct path whether running as script or exe
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), '..', relative_path)

# boost_saturation(folder, 1.23)
# boost_uniform_vibrancy(folder, 1.10)
# add_border(folder)
# upscale_bordered(folder)