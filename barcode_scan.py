import cv2
import os
import numpy as np
from pyzbar.pyzbar import decode

# Step 1: Capture an image with rpicam-still without displaying it
os.system("rpicam-still --output captured_image.jpg --nopreview")

# Step 2: Read the captured image with OpenCV
image = cv2.imread('captured_image.jpg')

# Step 3: Detect barcodes in the image
barcodes = decode(image)

# Print the number of barcodes found
print(f"Number of barcodes found: {len(barcodes)}")

# Step 4: Loop through each detected barcode
for barcode in barcodes:
    # Get the bounding box (polygon) of the barcode
    rect_points = barcode.polygon
    if len(rect_points) == 4:  # The bounding box is a quadrilateral
        pts = [tuple(point) for point in rect_points]
        cv2.polylines(image, [np.array(pts, dtype=np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)

    # Draw the rectangle around the barcode
    x, y, w, h = barcode.rect
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red rectangle

    # Print the location (bounding box) and data of the barcode
    print(f"Barcode Location: (x: {x}, y: {y}, width: {w}, height: {h})")
    print(f"Barcode Data: {barcode.data.decode('utf-8')}")

# Step 5: Save the modified image with barcodes
cv2.imwrite('captured_image_with_barcodes.jpg', image)
