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
    # Create a binary mask where intensity < 50 is set to 1, and others are set to 0
    binary_mask = np.where(gray < 50, 1, 0)

    # Iterate through the rows and find the first row with at least 1000 ones
    threshold = 1000  # Minimum number of ones required in a row to consider it to be part of the conveyor
    for row_idx, row in enumerate(binary_mask):
        ones_count = np.sum(row)  # Count the number of ones in the current row
        if ones_count >= threshold:
            print(f"The first row with at least {threshold} ones is row {row_idx}")
            # Draw a horizontal green line along the y-coordinate of the found row
            cv2.line(image, (0, row_idx), (image.shape[1] - 1, row_idx), (0, 255, 0), 2)
            break  # Exit the loop once we find the row
   
    # image[black_pixels_mask] = [0, 255, 255]  # Yellow in BGR format
     # The second and third arguments are the lower and upper thresholds for edge detection
    # edges = cv2.Canny(blurred, 100, 200)
    cv2.imwrite('black_highlighted.jpg', image)

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
