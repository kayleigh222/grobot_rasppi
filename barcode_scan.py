import cv2
import os

# Step 1: Capture an image with rpicam-still
os.system("rpicam-still --output captured_image.jpg")

# Step 2: Read the image with OpenCV
image = cv2.imread('captured_image.jpg')

# Step 3: Calculate the center of the image
# height, width, _ = image.shape
# center = (width // 2, height // 2)

# Step 4: Draw a dot in the center of the image (dot color is green)
# cv2.circle(image, center, 10, (0, 255, 0), -1)  # Green dot with radius 10

# Step 5: Display the image with the dot in the center
cv2.imshow('Captured Image with Dot', image)
cv2.waitKey(0)  # Wait for a key press to close the window
cv2.destroyAllWindows()


# import cv2
# from picamera2 import Picamera2
# from pyzbar.pyzbar import decode
# import numpy as np

# # Initialize the camera
# cam = Picamera2()
# height = 1080
# width = 1920

# # Configure the camera for a single image capture
# config = cam.create_still_configuration(main={"format": "RGB888", "size": (width, height)})
# cam.configure(config)
# cam.start()

# # Capture a single image
# frame = cam.capture_array()

# # Detect barcodes in the image
# barcodes = decode(frame)

# # Loop over all detected barcodes
# for barcode in barcodes:
#     # Get the bounding box for the barcode
#     rect_points = barcode.polygon
#     if len(rect_points) == 4:
#         pts = [tuple(point) for point in rect_points]
#         cv2.polylines(frame, [np.array(pts, dtype=np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)

#     # Get the barcode data (text)
#     barcode_data = barcode.data.decode("utf-8")
#     barcode_type = barcode.type

#     # Display the barcode data on the image
#     cv2.putText(frame, f'{barcode_data} ({barcode_type})', (barcode.rect.left, barcode.rect.top - 10),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

# # Display the image with barcode data
# cv2.imshow('Captured Image with Barcodes', frame)
# cv2.waitKey(0)  # Wait indefinitely until a key is pressed
# cv2.destroyAllWindows()

# # Stop the camera
# cam.stop()
