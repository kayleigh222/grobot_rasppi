import cv2
import numpy as np
from pyzbar.pyzbar import decode

# Define holder color range in HSV (currently blue)
HOLDER_COLOR_LOWER_THRESHOLD_HSV = np.array([100, 150, 50])   # Lower bound of blue
HOLDER_COLOR_UPPER_THRESHOLD_HSV = np.array([140, 255, 255])  # Upper bound of blue


# ----------- CONVEYOR LOCATIONS -------------
def find_top_and_bottom_of_conveyors(image): # top and bottom when vertical in real world (vertical in image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Create a binary mask where intensity < 50 is set to 1, and others are set to 0
    binary_mask = np.where(gray < 50, 1, 0)

    conveyor_top = 0
    conveyor_bottom = 0

    # Iterate through the columns and find the first column with enough dark pixels (top of conveyors)
    threshold = 500  # Minimum number of ones required in a row to consider it to be part of the conveyor
    for col_idx, col in enumerate(binary_mask.T):  # Transpose to iterate over columns
        ones_count = np.sum(col)  # Count the number of ones in the current column
        if ones_count >= threshold:
            conveyor_bottom = col_idx
            # draw a vertical green line
            cv2.line(image, (col_idx, 0), (col_idx, image.shape[0] - 1), (0, 255, 0), 2)
            break  # Exit once we find the first column meeting the threshold
            
    # Iterate through the columns from right to left and find the last column with enough dark pixels
    for col_idx in range(binary_mask.shape[1] - 1, -1, -1):  # Start from the last column
        col = binary_mask[:, col_idx]  # Select the column
        ones_count = np.sum(col)  # Count the number of ones in the current column
        if ones_count >= threshold:
            conveyor_top = col_idx
             # draw a vertical green line
            cv2.line(image, (col_idx, 0), (col_idx, image.shape[0] - 1), (0, 255, 0), 2)
            break  # Exit once we find the last column meeting the threshold
    
    cv2.imwrite('top_and_bottom_of_conveyor.jpg', image)
    return conveyor_top, conveyor_bottom

def find_left_and_right_of_conveyors(image): # left and right when vertical in real world (horizontal in image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Create a binary mask where intensity < 50 is set to 1, and others are set to 0
    binary_mask = np.where(gray < 50, 1, 0)

    conveyor_left = 0
    conveyor_right = 0

    # Iterate through the rows and find the first row with enough dark pixels (top of conveyors)
    threshold = 2000  # Minimum number of ones required in a row to consider it to be part of the conveyor
    for row_idx, row in enumerate(binary_mask):
        ones_count = np.sum(row)  # Count the number of ones in the current row
        if ones_count >= threshold:
            conveyor_left = row_idx
            # print(f"The first row with at least {threshold} ones is row {row_idx}")
            # # Draw a horizontal green line along the y-coordinate of the found row
            # cv2.line(image, (0, row_idx), (image.shape[1] - 1, row_idx), (0, 255, 0), 2)
            break  # Exit the loop once we find the row

    # Iterate through the rows and find the last row with enough dark pixels (bottom of conveyors)
    for row_idx in range(binary_mask.shape[0] - 1, -1, -1):  # Start from the last row
        row = binary_mask[row_idx]
        ones_count = np.sum(row)  # Count the number of ones in the current row
        if ones_count >= threshold:
            conveyor_right = row_idx
            # print(f"The first row from the bottom with at least {threshold} ones is row {row_idx}")
            # # Draw a horizontal green line along the y-coordinate of the found row
            # cv2.line(image, (0, row_idx), (image.shape[1] - 1, row_idx), (0, 255, 0), 2)
            break  # Exit the loop once we find the row

    # cv2.imwrite('left_and_right_of_conveyor.jpg', image)
    return conveyor_left, conveyor_right

# -------- HOLDER LOCATIONS -----------------
def find_holder_locations(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # Convert the image to HSV color space to detect color easier
    # Create mask
    mask = cv2.inRange(hsv, HOLDER_COLOR_LOWER_THRESHOLD_HSV, HOLDER_COLOR_UPPER_THRESHOLD_HSV)
    cv2.imwrite('mask.jpg', mask)

    # Find blue contours
    blue_contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # find barcodes
    barcode_centres = find_barcode_locations(image)

    # Iterate through blue contours and check proximity to barcodes
    for blue_contour in blue_contours:
        x, y, w, h = cv2.boundingRect(blue_contour)  # Get bounding box of blue patch
        blue_center = (x + w // 2, y + h // 2)  # Get center of blue patch

        for barcode_centre in barcode_centres:

            # Compute Euclidean distance
            distance = np.sqrt((blue_center[0] - barcode_centre[0])**2 + 
                            (blue_center[1] - barcode_centre[1])**2)

            if distance < 100:  # Adjust distance threshold based on image scale
                cv2.drawContours(image, [blue_contour], -1, (0, 255, 0), 3)  # Mark blue patch in green
                print(f"Blue patch at {blue_center} is near a barcode at {barcode_centre}")

    cv2.imwrite('image_with_blue_patches_near_barcodes.jpg', image)


# -------- BARCODE LOCATIONS ----------------

def top_barcode_right_conveyor(image):
    left_conveyor_barcodes, right_conveyor_barcodes = barcodes_divided_into_conveyors(image)
    # Check if there are any barcodes in the right conveyor
    if right_conveyor_barcodes:
        # Find the barcode with the maximum x-coordinate in the right conveyor
        top_barcode_right_conveyor = max(right_conveyor_barcodes, key=lambda point: point[0])
    else:
        # Handle the case where there are no barcodes in the right conveyor
        top_barcode_right_conveyor = None  # or some default value/message
    print("Top barcode right conveyor:", top_barcode_right_conveyor)
    return top_barcode_right_conveyor

def top_barcode_left_conveyor(image):
    left_conveyor_barcodes, right_conveyor_barcodes = barcodes_divided_into_conveyors(image)
    # Check if there are any barcodes in the right conveyor
    if left_conveyor_barcodes:
        # Find the barcode with the maximum x-coordinate in the right conveyor
        top_barcode_left_conveyor = max(left_conveyor_barcodes, key=lambda point: point[0])
    else:
        # Handle the case where there are no barcodes in the right conveyor
        top_barcode_left_conveyor = None  # or some default value/message
    print("Top barcode left conveyor:", top_barcode_left_conveyor)
    return top_barcode_left_conveyor

def barcodes_divided_into_conveyors(image):
    conveyor_left, conveyor_right = find_top_and_bottom_of_conveyors(image)
    distance = conveyor_right - conveyor_left
    threshold_for_top_conveyor_barcodes = conveyor_right - distance//4
    
    barcode_centres = find_barcode_locations(image)  # Get barcode center coordinates
    if not barcode_centres:
        return [], []  # No barcodes found

    # Initialize the lists for left and right conveyor barcodes
    left_conveyor_barcodes = []
    right_conveyor_barcodes = []

    # Iterate through the barcode centers and classify them based on their y values
    for centre in barcode_centres:
        x, y = centre  # Unpack the barcode center coordinates
        if y < threshold_for_top_conveyor_barcodes:
            left_conveyor_barcodes.append(centre)  # Barcode is above the threshold (left conveyor)
        else:
            right_conveyor_barcodes.append(centre)  # Barcode is below the threshold (right conveyor)

    return left_conveyor_barcodes, right_conveyor_barcodes    

def find_barcode_locations(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    equalized = cv2.equalizeHist(gray)
    barcodes = decode(equalized) # detect barcodes
    print(f"Number of barcodes found: {len(barcodes)}")
    cv2.imwrite('thresholded_img.jpg', equalized)

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
        # cv2.circle(image, (int(centre_x), int(centre_y)), radius=3, color=(0, 0, 255), thickness=-1)  # Red filled dot at centre of barcode
        # cv2.imwrite('captured_image_with_barcodes.jpg', image)
    
        # IF DEBUGGING:
        print(f"Barcode Location: (x: {x}, y: {y}, width: {w}, height: {h})")
        print(f"Barcode Data: {barcode.data.decode('utf-8')}")
    
    return centres  # Return the list of center coordinates
