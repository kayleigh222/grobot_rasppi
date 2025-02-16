import cv2
from picamera2 import Picamera2
import numpy as np

# Initialize the camera
picam2 = Picamera2()

# Configure the camera
picam2.configure(picam2.create_still_configuration())

# Start the camera
picam2.start()

# Capture frames and process with OpenCV
while True:
    # Capture a frame
    frame = picam2.capture_array()

    print("Frame shape:", frame.shape)

      # Ensure the frame has the right number of channels
    if len(frame.shape) == 2:  # Grayscale or single-channel image
        # Convert grayscale to BGR
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    elif len(frame.shape) == 3 and frame.shape[-1] == 1:  # Single-channel image (e.g., YUV420)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    elif len(frame.shape) == 3 and frame.shape[-1] == 3:  # BGR format
        frame_bgr = frame  # No conversion needed
    else:
        print("Unsupported frame format")
        break

    # Convert the frame from YUV420 to BGR (OpenCV format)
    # frame_bgr = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_I420)

    # Show the frame
    cv2.imshow("Camera", frame_bgr)

    # Wait for the 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
picam2.stop()
cv2.destroyAllWindows()



# import cv2
# import zbar
# from PIL import Image  # Ensure you import Image from PIL

# # Initialize the camera
# cap = cv2.VideoCapture("libcamerasrc ! videoconvert ! appsink", cv2.CAP_GSTREAMER)

# # Initialize the ZBar scanner
# scanner = zbar.Scanner()

# try:
#     while True:
#         # Capture frame from the camera
#         ret, frame = cap.read()
#         if not ret:
#             print("Failed to grab frame")
#             break

#         # Convert the frame to grayscale (optional, but improves barcode detection)
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#         # Scan the frame for barcodes
#         pil_image = Image.fromarray(gray)  # Convert frame to PIL Image
#         results = scanner.scan(pil_image)

#         for result in results:
#             # Print the barcode data
#             print(f"Detected barcode: {result.data.decode('utf-8')}")

#             # Draw a rectangle around the detected barcode
#             x, y, w, h = result.position
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

#         # Display the frame with barcodes highlighted
#         cv2.imshow('Barcode Scanner', frame)

#         # Break the loop if the user presses 'q'
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

# except KeyboardInterrupt:
#     print("\nKeyboard Interrupt detected. Exiting...")

# finally:
#     # **Fix: Explicitly set the GStreamer pipeline to NULL**
#     if cap.isOpened():
#         cap.release()  # Release the camera
#     cv2.destroyAllWindows()  # Close OpenCV windows

#     # **Ensure GStreamer pipeline is stopped**
#     import os
#     os.system("gst-launch-1.0 -e videotestsrc ! fakesink & killall gst-launch-1.0")

#     print("Camera released and windows closed.")

