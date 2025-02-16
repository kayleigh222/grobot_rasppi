import cv2
from picamera2 import Picamera2
from pyzbar.pyzbar import decode
import numpy as np

# Initialize the camera
cam = Picamera2()
height = 1080
width = 1920
middle = (width // 2, height // 2)

# Configure the camera for a single image capture
config = cam.create_still_configuration(main={"format": "RGB888", "size": (width, height)})
cam.configure(config)
cam.start()

# Capture a single image
frame = cam.capture_array()

# Detect barcodes in the image
barcodes = decode(frame)

# Loop over all detected barcodes
for barcode in barcodes:
    # Get the bounding box for the barcode
    rect_points = barcode.polygon
    if len(rect_points) == 4:
        pts = [tuple(point) for point in rect_points]
        cv2.polylines(frame, [np.array(pts, dtype=np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)

    # Get the barcode data (text)
    barcode_data = barcode.data.decode("utf-8")
    barcode_type = barcode.type

    # Display the barcode data on the image
    cv2.putText(frame, f'{barcode_data} ({barcode_type})', (barcode.rect.left, barcode.rect.top - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

# Draw a circle at the center (optional)
cv2.circle(frame, middle, 10, (255, 0, 255), -1)

# Display the image with barcode data
cv2.imshow('Captured Image with Barcodes', frame)
cv2.waitKey(0)  # Wait indefinitely until a key is pressed
cv2.destroyAllWindows()

# Stop the camera
cam.stop()
