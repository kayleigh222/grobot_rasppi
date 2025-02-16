import cv2
import zbar

# Initialize the camera
cap = cv2.VideoCapture("libcamerasrc ! videoconvert ! appsink", cv2.CAP_GSTREAMER)

# Initialize the ZBar scanner
scanner = zbar.Scanner()

while True:
    # Capture frame from the camera
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to grayscale (optional, but improves barcode detection)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Scan the frame for barcodes
    pil_image = Image.fromarray(gray)  # Convert frame to PIL Image
    results = scanner.scan(pil_image)

    for result in results:
        # Print the barcode data
        print(f"Detected barcode: {result.data.decode('utf-8')}")

        # Draw a rectangle around the detected barcode
        x, y, w, h = result.position
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the frame with barcodes highlighted
    cv2.imshow('Barcode Scanner', frame)

    # Break the loop if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()
