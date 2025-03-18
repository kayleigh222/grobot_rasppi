import cv2
from pyzbar.pyzbar import decode

def find_top_barcode_right_conveyor(image_path):
    barcode_centres = find_barcode_locations(image_path)  # Get barcode center coordinates

    if not barcode_centres:
        return None  # No barcodes found

    # Sort by y (descending) to prioritize the right conveyor (lower in the image, higher y values)
    sorted_by_y = sorted(barcode_centres, key=lambda point: point[1], reverse=True)

    # Get the highest x value from the rightmost barcode centres
    top_barcode = max(sorted_by_y, key=lambda point: point[0])  # Max x value

    return top_barcode  # Return (centre_x, centre_y) of the top barcode
    

def find_barcode_locations(image_path):
    image = cv2.imread(image_path) # read the captured image with opencv
    barcodes = decode(image) # detect barcodes
    # print(f"Number of barcodes found: {len(barcodes)}")

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
