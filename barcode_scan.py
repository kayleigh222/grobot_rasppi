import cv2
from pyzbar.pyzbar import decode

def barcodes_divided_into_conveyors(image_path):
    image = cv2.imread(image_path) # read the captured image with opencv
    barcode_centres = find_barcode_locations(image)  # Get barcode center coordinates
    if not barcode_centres:
        return [], []  # No barcodes found

    # figure out threshold for left and right conveyor
    # use canny edge detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
     # The second and third arguments are the lower and upper thresholds for edge detection
    edges = cv2.Canny(blurred, 100, 200)
    cv2.imwrite('captured_image_edges.jpg', edges)

    return [], []

def find_barcode_locations(image):
    barcodes = decode(image) # detect barcodes
    print(f"Number of barcodes found: {len(barcodes)}")

    centres = []  # List to store center coordinates

    # loop through each detected barcode
    for barcode in barcodes:
        # Get the rectangle around the barcode
        x, y, w, h = barcode.rect
        centre_x = x + w/2
        centre_y = y + h/2
        centres.append((centre_x, centre_y))  # Store the center coordinates

        # IF WANT TO VISUALISE:
        # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red rectangle
        # cv2.circle(image, (centre_x, centre_y), radius=3, color=(0, 0, 255), thickness=-1)  # Red filled dot at centre of barcode
        # cv2.imwrite('captured_image_with_barcodes.jpg', image)
    
        # IF DEBUGGING:
        # print(f"Barcode Location: (x: {x}, y: {y}, width: {w}, height: {h})")
        # print(f"Barcode Data: {barcode.data.decode('utf-8')}")
    
    return centres  # Return the list of center coordinates
