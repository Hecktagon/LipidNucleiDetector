#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 15:29:16 2025

@author: jasonwells
"""

import cv2
import numpy as np
import os
import csv
import easygui  # pip install easygui

# =========================
# Settings
# =========================
POINTS_PER_CLASS = 5
CLASSES = [
    ("Lipids", (0, 255, 0)),     # Green (BGR)
    ("Nuclei", (0, 165, 255)),   # Orange (BGR)
]
CROSSHAIR_ARM = 10     # pixels
CROSSHAIR_THK = 3      # thickness
MAX_DISPLAY_W = 1400   # maximum window width for preview
MAX_DISPLAY_H = 900    # maximum window height for preview

# HSV padding around min/max from selected points (tune if needed)
HSV_PAD = np.array([10, 50, 50], dtype=np.int32)  # (H, S, V) margins

# Morphology to reduce nuclei "halo"
NUCLEI_ERODE_RADIUS_PX = 1   # 0 disables erosion; try 1–2 if halos persist
NUCLEI_ERODE_ITER = 1

# Area conversion (µm per pixel). Set to your microscope calibration.
MICRONS_PER_PIXEL = 0.5

# =========================
# File chooser
# =========================
file_path = easygui.fileopenbox(title="Select an image",
                                filetypes=["*.jpg","*.jpeg","*.png","*.tif","*.tiff","*.bmp"])
if not file_path:
    raise SystemExit("No file selected.")

image = cv2.imread(file_path)
if image is None:
    raise SystemExit("Could not read the image.")

h, w = image.shape[:2]

# =========================
# Build a fixed-size display image (scaled copy) and map clicks back
# =========================
scale = min(MAX_DISPLAY_W / w, MAX_DISPLAY_H / h, 1.0)
disp_w, disp_h = int(round(w * scale)), int(round(h * scale))
disp_base = cv2.resize(image, (disp_w, disp_h), interpolation=cv2.INTER_AREA).copy()
disp_work = disp_base.copy()

def to_orig_coords(x_disp, y_disp):
    """Map display coords back to original image coords."""
    x = int(round(x_disp / scale))
    y = int(round(y_disp / scale))
    x = max(0, min(w - 1, x))
    y = max(0, min(h - 1, y))
    return x, y

def to_disp_coords(x_orig, y_orig):
    """Map original coords to display coords (for redraw)."""
    xd = int(round(x_orig * scale))
    yd = int(round(y_orig * scale))
    xd = max(0, min(disp_w - 1, xd))
    yd = max(0, min(disp_h - 1, yd))
    return xd, yd

def draw_crosshair(img, x, y, color_bgr):
    """Draw a thick crosshair centered at (x, y) on the DISPLAY image."""
    cv2.line(img, (x - CROSSHAIR_ARM, y), (x + CROSSHAIR_ARM, y), color_bgr, CROSSHAIR_THK)
    cv2.line(img, (x, y - CROSSHAIR_ARM), (x, y + CROSSHAIR_ARM), color_bgr, CROSSHAIR_THK)

def redraw_all_crosshairs():
    """Redraw all accepted crosshairs and the pending one onto disp_work."""
    global disp_work
    disp_work = disp_base.copy()
    # Accepted points
    for cls_name, color in CLASSES:
        for (xo, yo) in accepted_points[cls_name]:
            xd, yd = to_disp_coords(xo, yo)
            draw_crosshair(disp_work, xd, yd, color)
    # Pending point (not yet accepted)
    if pending_point is not None:
        xd, yd = pending_point['disp']
        draw_crosshair(disp_work, xd, yd, pending_point['color'])

# =========================
# Selection state
# =========================
accepted_points = {cls: [] for cls, _ in CLASSES}   # original coords per class
hsv_samples = {cls: [] for cls, _ in CLASSES}       # HSV samples per class
current_class_idx = 0
awaiting_decision = False
pending_point = None  # {'orig':(x,y), 'disp':(xd,yd), 'color':(b,g,r)}

# Precompute HSV for original image
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# =========================
# Mouse callback
# =========================
def mouse_cb(event, x, y, flags, param):
    global pending_point, awaiting_decision
    if event == cv2.EVENT_LBUTTONDOWN and not awaiting_decision:
        # Convert display coords to original coords
        xo, yo = to_orig_coords(x, y)
        cls_name, color = CLASSES[current_class_idx]

        # Prepare a pending point
        pending_point = {
            'orig': (xo, yo),
            'disp': (x, y),
            'color': color,
            'class': cls_name
        }
        awaiting_decision = True
        redraw_all_crosshairs()
        cv2.imshow("Select Points", disp_work)
        print(f"Candidate selected at ({xo}, {yo}) for {cls_name}. Press 'a' to accept or 'r' to redo.")

# =========================
# Selection loop
# =========================
cv2.namedWindow("Select Points", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Select Points", disp_w, disp_h)
cv2.setMouseCallback("Select Points", mouse_cb)

print("Selection order:")
for cls_name, _ in CLASSES:
    print(f" - {cls_name}: pick {POINTS_PER_CLASS} points")
print("Controls: Left click to choose a point → 'a' accept, 'r' redo, 'u' undo last accepted, 'n' next class, ESC to quit.")

while current_class_idx < len(CLASSES):
    cls_name, color = CLASSES[current_class_idx]

    # Show and wait for keys
    cv2.imshow("Select Points", disp_work)
    key = cv2.waitKey(10) & 0xFF

    # Accept/redo pending
    if awaiting_decision:
        if key in (ord('a'), 13, 32):  # 'a' or Enter or Space
            # Commit the pending point
            (xo, yo) = pending_point['orig']
            accepted_points[cls_name].append((xo, yo))
            hsv_samples[cls_name].append(hsv_image[yo, xo])
            awaiting_decision = False
            print(f"Point {len(accepted_points[cls_name])} of {POINTS_PER_CLASS} selected for {cls_name}")
            pending_point = None
            redraw_all_crosshairs()
        elif key in (ord('r'), 8, 127):  # 'r' or Backspace/Delete
            # Discard the pending point
            awaiting_decision = False
            pending_point = None
            redraw_all_crosshairs()

    else:
        # Undo last accepted point for this class
        if key == ord('u'):
            if accepted_points[cls_name]:
                (ux, uy) = accepted_points[cls_name].pop()
                if hsv_samples[cls_name]:
                    hsv_samples[cls_name].pop()
                print(f"Undid last point ({ux},{uy}) for {cls_name}. Now {len(accepted_points[cls_name])}/{POINTS_PER_CLASS}.")
                redraw_all_crosshairs()

        # Move to next class when enough points are accepted
        if key == ord('n'):
            if len(accepted_points[cls_name]) == POINTS_PER_CLASS:
                current_class_idx += 1
                if current_class_idx < len(CLASSES):
                    print(f"→ Next: {CLASSES[current_class_idx][0]} (pick {POINTS_PER_CLASS} points)")
                redraw_all_crosshairs()
            else:
                remaining = POINTS_PER_CLASS - len(accepted_points[cls_name])
                print(f"You still need {remaining} point(s) for {cls_name} before moving on.")

    if key == 27:  # ESC
        cv2.destroyAllWindows()
        raise SystemExit("Cancelled by user.")

cv2.destroyWindow("Select Points")

# =========================
# Build HSV masks from selected samples
# =========================
masks = {}
hsv_bounds = {}
for cls_name, _ in CLASSES:
    pts = np.array(hsv_samples[cls_name], dtype=np.int32)  # shape: (N, 3)
    # Robust min/max with padding
    low = np.clip(pts.min(axis=0) - HSV_PAD, 0, 255)
    high = np.clip(pts.max(axis=0) + HSV_PAD, 0, 255)
    mask = cv2.inRange(hsv_image, low.astype(np.uint8), high.astype(np.uint8))
    masks[cls_name] = mask
    hsv_bounds[cls_name] = (low.astype(int).tolist(), high.astype(int).tolist())

# --- Post-processing to reduce halos: erode nuclei; lipid priority wins in overlaps
lipid_mask = masks["Lipids"].copy()
nuclei_mask = masks["Nuclei"].copy()

if NUCLEI_ERODE_RADIUS_PX > 0 and NUCLEI_ERODE_ITER > 0:
    ksz = 2 * NUCLEI_ERODE_RADIUS_PX + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksz, ksz))
    nuclei_mask = cv2.erode(nuclei_mask, kernel, iterations=NUCLEI_ERODE_ITER)

# ===============================
# MASK RESET + CHANNEL OVERRIDE
# ===============================
# Reset masks fresh (prevents accumulation)
lipid_mask = np.zeros((h, w), dtype=np.uint8)
nuclei_mask = np.zeros((h, w), dtype=np.uint8)

# Compute channel ratios
R = image[:, :, 2].astype(float)
G = image[:, :, 1].astype(float)
B = image[:, :, 0].astype(float)

red_ratio = R / (B + 1e-5)
blue_ratio = B / (R + 1e-5)

# Thresholds (tune as needed)
lipid_thresh = 1.5
nuclei_thresh = 1.5

# Lipid override: red dominance
lipid_override = (red_ratio > lipid_thresh) & (red_ratio > blue_ratio)
lipid_mask[lipid_override] = 255

# Nuclei override: blue dominance with intensity filter
nuclei_override = (blue_ratio > nuclei_thresh) & (blue_ratio > red_ratio) & (B > 80)
nuclei_mask[nuclei_override] = 255

# Morphological cleanup on nuclei
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
nuclei_mask = cv2.morphologyEx(nuclei_mask, cv2.MORPH_OPEN, kernel)
nuclei_mask = cv2.morphologyEx(nuclei_mask, cv2.MORPH_CLOSE, kernel)

# Replace masks dict with refined versions
masks = {
    "Lipids": lipid_mask,
    "Nuclei": nuclei_mask
}
# ===============================
# VISUALIZE MASK OVERLAY (with purple for overlap)
# ===============================
overlay = image.copy()

# Start with a blank canvas
color_mask = np.zeros_like(image)

# Define colors (BGR format for OpenCV)
green = (0, 255, 0)      # Lipids
orange = (0, 165, 255)   # Nuclei
purple = (255, 0, 255)   # Overlap (Lipids + Nuclei)

# Boolean masks
lipid_only = (masks["Lipids"] > 0) & (masks["Nuclei"] == 0)
nuclei_only = (masks["Nuclei"] > 0) & (masks["Lipids"] == 0)
overlap = (masks["Lipids"] > 0) & (masks["Nuclei"] > 0)

# Apply colors
color_mask[lipid_only] = green
color_mask[nuclei_only] = orange
color_mask[overlap] = purple

# Blend with original image
blended = cv2.addWeighted(image, 0.6, color_mask, 0.4, 0)

# Save overlay to file
overlay_path = os.path.splitext(file_path)[0] + "_mask_overlay.png"
cv2.imwrite(overlay_path, blended)
print(f"Overlay with masks saved: {overlay_path}")

# (Optional) show overlay in window
cv2.imshow("Mask Overlay", blended)
cv2.waitKey(0)
cv2.destroyWindow("Mask Overlay")

# ===============================
# RESULTS CALCULATION
# ===============================
results = []
total_pixels = h * w
total_area_um2 = total_pixels * (MICRONS_PER_PIXEL ** 2)

for cls_name, _ in CLASSES:
    pixels = int(np.count_nonzero(masks[cls_name]))
    area_um2 = pixels * (MICRONS_PER_PIXEL ** 2)
    percent = (pixels / total_pixels) * 100.0 if total_pixels > 0 else 0.0
    results.append({
        "Class": cls_name,
        "Pixel Count": pixels,
        "Area (µm²)": area_um2,
        "Percent of total (%)": percent
    })

# ===============================
# CSV OUTPUT (points + results + thresholds)
# ===============================
csv_path = os.path.splitext(file_path)[0] + "_points.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)

    # Section 1: Selected points
    writer.writerow(["Class", "X", "Y", "H", "S", "V"])
    for cls_name, pts in accepted_points.items():
        for (xo, yo) in pts:
            h_, s_, v_ = hsv_image[yo, xo]
            writer.writerow([cls_name, xo, yo, int(h_), int(s_), int(v_)])

    # Section 2: Area results
    writer.writerow([])
    writer.writerow(["--- AREA RESULTS ---"])
    writer.writerow(["Class", "Pixel Count", "Area (µm²)", "Percent of total (%)"])
    for row in results:
        writer.writerow([row["Class"], row["Pixel Count"], row["Area (µm²)"], row["Percent of total (%)"]])

    # Totals row
    writer.writerow([])
    writer.writerow(["--- TOTALS ---"])
    writer.writerow(["Total Image", total_pixels, total_area_um2, 100.0])

    # Section 3: HSV thresholds
    writer.writerow([])
    writer.writerow(["--- HSV THRESHOLDS (low→high) ---"])
    writer.writerow(["Class", "H_low", "S_low", "V_low", "H_high", "S_high", "V_high"])
    for cls_name in ["Lipids", "Nuclei"]:
        low, high = hsv_bounds[cls_name]
        writer.writerow([cls_name, *low, *high])

print(f"CSV saved with points + results + thresholds: {csv_path}")
for row in results:
    print(f"{row['Class']}: {row['Pixel Count']} px, {row['Area (µm²)']:.2f} µm², {row['Percent of total (%)']:.2f}%")
print(f"Total pixels: {total_pixels}  |  Total area: {total_area_um2:.2f} µm²")

# =========================
# Area calculations per class + totals and percentages
# =========================
results = []
total_pixels = h * w

for cls_name, _ in CLASSES:
    pixels = int(np.sum(masks[cls_name] > 0))
    area_um2 = pixels * (MICRONS_PER_PIXEL ** 2)
    percent = (pixels / total_pixels) * 100.0 if total_pixels > 0 else 0.0
    results.append({
        "Class": cls_name,
        "Pixel Count": pixels,
        "Area (µm²)": area_um2,
        "Percent of total (%)": percent
    })

# Append results + totals to same CSV
with open(csv_path, "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([])
    writer.writerow(["--- AREA RESULTS ---"])
    writer.writerow(["Class", "Pixel Count", "Area (µm²)", "Percent of total (%)"])
    for row in results:
        writer.writerow([row["Class"], row["Pixel Count"], row["Area (µm²)"], row["Percent of total (%)"]])

    # Totals row
    writer.writerow([])
    writer.writerow(["--- TOTALS ---"])
    total_area_um2 = total_pixels * (MICRONS_PER_PIXEL ** 2)
    writer.writerow(["Total Image", total_pixels, total_area_um2, 100.0])

# (Optional) save HSV thresholds used — helps reproducibility
with open(csv_path, "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([])
    writer.writerow(["--- HSV THRESHOLDS (low→high) ---"])
    writer.writerow(["Class", "H_low", "S_low", "V_low", "H_high", "S_high", "V_high"])
    for cls_name in ["Lipids", "Nuclei"]:
        low, high = hsv_bounds[cls_name]
        writer.writerow([cls_name, *low, *high])

print("Area results + totals appended to CSV.")
for row in results:
    print(f"{row['Class']}: {row['Pixel Count']} px, {row['Area (µm²)']:.2f} µm², {row['Percent of total (%)']:.2f}%")
print(f"Total pixels: {total_pixels}  |  Total area: {total_area_um2:.2f} µm²")
