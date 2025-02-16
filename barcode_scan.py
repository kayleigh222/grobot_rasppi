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

# Step 5: Calculate the center of the image
height, width, _ = image.shape
center = (width // 2, height // 2)

# Step 6: Draw a dot in the center of the image (dot color is green)
cv2.circle(image, center, 10, (0, 255, 0), -1)  # Green dot with radius 10

# Step 7: Save the modified image with barcodes and the center dot
cv2.imwrite('captured_image_with_barcodes_and_dot.jpg', image)

# The image is saved as 'captured_image_with_barcodes_and_dot.jpg' without displaying it


# import cv2
# import os

# # Step 1: Capture an image with rpicam-still without displaying it
# os.system("rpicam-still --output captured_image.jpg --nopreview")

# # Step 2: Read the captured image with OpenCV
# image = cv2.imread('captured_image.jpg')

# # Step 3: Calculate the center of the image
# height, width, _ = image.shape
# center = (width // 2, height // 2)

# # Step 4: Draw a dot in the center of the image (dot color is green)
# cv2.circle(image, center, 10, (0, 255, 0), -1)  # Green dot with radius 10

# # Step 5: Save the modified image
# cv2.imwrite('captured_image_with_dot.jpg', image)

# # The image is saved as 'captured_image_with_dot.jpg' without displaying it