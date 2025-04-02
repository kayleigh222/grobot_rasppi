import os
import cv2
import numpy as np
from pyzbar.pyzbar import decode

# Define holder color range in HSV (currently blue)
HOLDER_COLOR_LOWER_THRESHOLD_HSV = np.array([100, 150, 50])   # Lower bound of blue
HOLDER_COLOR_UPPER_THRESHOLD_HSV = np.array([140, 255, 255])  # Upper bound of blue

# Define leg color range in HSV (currently green)
LEG_COLOR_LOWER_THRESHOLD_HSV = np.array([30, 50, 50])   # Lower bound of green
LEG_COLOR_UPPER_THRESHOLD_HSV = np.array([90, 255, 255])  # Upper bound of green

# Define a minimum area threshold for contours to be considered a contour
MIN_HOLDER_AREA = 3000 
MIN_LEG_AREA = 3000

# max distance between a holder center and its barcode
MAX_DISTANCE_BETWEEN_HOLDER_CENTER_AND_BARCODE = 400

NUM_BARCODES = 1  # Number of barcodes to on conveyors total

# ----------- PUSH LEG LOCATIONS -------------
def find_leg_top_conveyor(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # Convert the image to HSV color space to detect color easier
    # Create mask
    mask = cv2.inRange(hsv, LEG_COLOR_LOWER_THRESHOLD_HSV, LEG_COLOR_UPPER_THRESHOLD_HSV)
    cv2.imwrite('mask.jpg', mask)

    # Find contours of leg areas
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours based on size
    leg_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > MIN_LEG_AREA]
    # draw the contours on the image
    for leg_contour in leg_contours:
        cv2.drawContours(image, [leg_contour], -1, (0, 255, 0), 3)
    cv2.imwrite('image_with_leg_contours.jpg', image)
     # print number of leg contours
    print(f"Number of leg contours found: {len(leg_contours)}")

    # get the leg contour with the highest x value
    leg_contour = max(leg_contours, key=lambda cnt: cv2.boundingRect(cnt)[0])
    x, y, w, h = cv2.boundingRect(leg_contour)  # Get bounding box of the leg 

    return x, y # return the top left corner of the leg contour


# ----------- CONVEYOR LOCATIONS -------------
def get_conveyor_threshold(image):
    conveyor_left, conveyor_right = find_left_and_right_of_conveyors(image)
    distance = conveyor_right - conveyor_left
    threshold = conveyor_right - distance//2
    
    return threshold

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
            # cv2.line(image, (col_idx, 0), (col_idx, image.shape[0] - 1), (0, 255, 0), 2)
            break  # Exit once we find the last column meeting the threshold
    
    # cv2.imwrite('top_and_bottom_of_conveyor.jpg', image)
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

def get_top_edge_of_holder(holder_contour, image):
    # Get bounding box of the contour
    x, y, w, h = cv2.boundingRect(holder_contour)

    # # draw the bounding box on the image 
    # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle
    # cv2.imwrite('bounding_box_of_holder.jpg', image)

    # The top edge is at y with width w
    top_edge = [(x, y), (x + w, y)]
    print(f"Top edge coordinates: {top_edge}")
    return top_edge

def get_bottom_edge_of_holder(holder_contour, image):
    # Get bounding box of the contour
    x, y, w, h = cv2.boundingRect(holder_contour)

    # # draw the bounding box on the image 
    # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle
    # cv2.imwrite('bounding_box_of_holder.jpg', image)

    # The bottom edge is at y+h with width w
    bottom_edge = [(x, y + h), (x + w, y + h)]
    print(f"Bottom edge coordinates: {bottom_edge}")
    return bottom_edge

#conveyor_threshold: the y-coordinate threshold that divides the top and bottom conveyors
def top_holder_left_conveyor(image, conveyor_threshold):
    print('finding top holder left conveyor')
    left_conveyor_holders, right_conveyor_holders = holders_divided_into_conveyors(image, conveyor_threshold)
    # Check if there are any barcodes in the right conveyor
    if left_conveyor_holders:
        # Find the barcode with the maximum x-coordinate in the right conveyor
        top_holder_left_conveyor = max(left_conveyor_holders, key=lambda holder: holder['holder_center'][0])
    else:
        # Handle the case where there are no barcodes in the right conveyor
        top_holder_left_conveyor = None  # or some default value/message
    print("Top holder left conveyor center:", top_holder_left_conveyor['holder_center'])
    print("Top holder left conveyor empty:", top_holder_left_conveyor['is_empty'])
    return top_holder_left_conveyor

#conveyor_threshold: the y-coordinate threshold that divides the top and bottom conveyors
def top_holder_right_conveyor(image, conveyor_threshold):
    left_conveyor_holders, right_conveyor_holders = holders_divided_into_conveyors(image, conveyor_threshold)
    # Check if there are any barcodes in the right conveyor
    if right_conveyor_holders:
        # Find the barcode with the maximum x-coordinate in the right conveyor
        top_holder_right_conveyor = max(right_conveyor_holders, key=lambda holder: holder['holder_center'][0])
    else:
        # Handle the case where there are no barcodes in the right conveyor
        top_holder_right_conveyor = None  # or some default value/message
    print("Top holder right conveyor center:", top_holder_right_conveyor['holder_center'])
    print("Top holder right conveyor empty:", top_holder_right_conveyor['is_empty'])
    return top_holder_right_conveyor

# conveyor_threshold: the y-coordinate threshold that divides the top and bottom conveyors
def holders_divided_into_conveyors(image, conveyor_threshold):    
    holders = find_holders(image)  # Get empty holder contours

    # Initialize the lists for left and right conveyor barcodes
    left_conveyor_holders = []
    right_conveyor_holders = []

    # Iterate through the barcode centers and classify them based on their y values
    for holder in holders:
        x, y = holder['holder_center']  # Unpack the barcode center coordinates
        if y < conveyor_threshold:
            left_conveyor_holders.append(holder)  # Barcode is above the threshold (left conveyor)
        else:
            right_conveyor_holders.append(holder)  # Barcode is below the threshold (right conveyor)

        # Draw contours for the left conveyor holders in blue
    for holder in left_conveyor_holders:
        cv2.drawContours(image, [holder['contour']], -1, (255, 0, 0), 3)  # Blue color for left conveyor

    # Draw contours for the right conveyor holders in green
    for holder in right_conveyor_holders:
        cv2.drawContours(image, [holder['contour']], -1, (0, 255, 0), 3)  # Green color for right conveyor

    # Draw the conveyor threshold line (horizontal line at the y-coordinate of the threshold)
    # cv2.line(image, (0, conveyor_threshold), (image.shape[1], conveyor_threshold), (0, 0, 255), 2)  # Red line

    # Save the image with the drawn contours
    # cv2.imwrite('image_with_divided_conveyors.jpg', image)

    return left_conveyor_holders, right_conveyor_holders    

# Finds all holders, returns the contours and empty status
def find_holders(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # Convert the image to HSV color space to detect color easier
    # Create mask
    mask = cv2.inRange(hsv, HOLDER_COLOR_LOWER_THRESHOLD_HSV, HOLDER_COLOR_UPPER_THRESHOLD_HSV)
    cv2.imwrite('mask.jpg', mask)

    # Find contours of blue areas
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours based on size
    holder_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > MIN_HOLDER_AREA]
     # print number of holder contours
    print(f"Number of holder contours found: {len(holder_contours)}")

    # Find barcodes in the image
    barcode_centres = find_barcode_locations(image)

    # List to store information about the holders
    holders_info = []

    # Iterate through blue contours
    for holder_contour in holder_contours:
        x, y, w, h = cv2.boundingRect(holder_contour)  # Get bounding box of blue patch
        holder_center = (x + w // 2, y + h // 2)  # Get center of blue patch
        print(f"Holder center: {holder_center}")

        # Check proximity to barcodes to determine if the holder is empty
        too_close = False

        # draw a circle representing the max distance between a holder center and its barcode
        # cv2.circle(image, holder_center, MAX_DISTANCE_BETWEEN_HOLDER_CENTER_AND_BARCODE, (0, 0, 255), 2)

        for barcode_centre in barcode_centres:
            # Compute Euclidean distance to barcode
            distance = np.sqrt((holder_center[0] - barcode_centre[0])**2 + 
                               (holder_center[1] - barcode_centre[1])**2)

            if distance < MAX_DISTANCE_BETWEEN_HOLDER_CENTER_AND_BARCODE:  # Adjust distance threshold based on image scale
                too_close = True
                break  # No need to check further if already too close
        
        # Store the contour, empty status, and barcode (if not empty)
        holder_info = {
            'contour': holder_contour,
            'is_empty': not too_close,  # If not too close to barcode, it's considered empty
            'holder_center': holder_center
        }
        holders_info.append(holder_info)

    # Optionally, draw contours for all holders
    # for holder in holders_info:
    #     color = (255, 0, 0) if holder['is_empty'] else (0, 255, 0)  # Blue for empty, green for not empty
    #     cv2.drawContours(image, [holder['contour']], -1, color, 3)  # Draw each holder's contour with different color

    # cv2.imwrite('image_with_all_holders.jpg', image)

    return holders_info


# -------- BARCODE LOCATIONS ----------------

#conveyor_threshold: the y-coordinate threshold that divides the top and bottom conveyors
def top_barcode_right_conveyor(image, conveyor_threshold):
    left_conveyor_barcodes, right_conveyor_barcodes = barcodes_divided_into_conveyors(image, conveyor_threshold)
    # Check if there are any barcodes in the right conveyor
    if right_conveyor_barcodes:
        # Find the barcode with the maximum x-coordinate in the right conveyor
        top_barcode_right_conveyor = max(right_conveyor_barcodes, key=lambda point: point[0])
    else:
        # Handle the case where there are no barcodes in the right conveyor
        top_barcode_right_conveyor = None  # or some default value/message
    print("Top barcode right conveyor:", top_barcode_right_conveyor)
    return top_barcode_right_conveyor

#conveyor_threshold: the y-coordinate threshold that divides the top and bottom conveyors
def top_barcode_left_conveyor(image, conveyor_threshold):
    left_conveyor_barcodes, right_conveyor_barcodes = barcodes_divided_into_conveyors(image, conveyor_threshold)
    # Check if there are any barcodes in the right conveyor
    if left_conveyor_barcodes:
        # Find the barcode with the maximum x-coordinate in the right conveyor
        top_barcode_left_conveyor = max(left_conveyor_barcodes, key=lambda point: point[0])
    else:
        # Handle the case where there are no barcodes in the right conveyor
        top_barcode_left_conveyor = None  # or some default value/message
    print("Top barcode left conveyor:", top_barcode_left_conveyor)
    return top_barcode_left_conveyor

def barcodes_divided_into_conveyors(image, conveyor_threshold):
    
    barcode_centres = find_barcode_locations(image)  # Get barcode center coordinates
    if not barcode_centres:
        return [], []  # No barcodes found

    # Initialize the lists for left and right conveyor barcodes
    left_conveyor_barcodes = []
    right_conveyor_barcodes = []

    # Iterate through the barcode centers and classify them based on their y values
    for centre in barcode_centres:
        x, y = centre  # Unpack the barcode center coordinates
        if y < conveyor_threshold:
            left_conveyor_barcodes.append(centre)  # Barcode is above the threshold (left conveyor)
        else:
            right_conveyor_barcodes.append(centre)  # Barcode is below the threshold (right conveyor)

    return left_conveyor_barcodes, right_conveyor_barcodes    

def find_barcode_locations(image):
    num_barcodes_found = 0
    while(num_barcodes_found != NUM_BARCODES):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        equalized = cv2.equalizeHist(gray)
        barcodes = decode(equalized) # detect barcodes
        num_barcodes_found = len(barcodes)
        if num_barcodes_found != NUM_BARCODES:
            print("Barcodes: ", barcodes)
            print(f"Found {num_barcodes_found} barcodes, expected {NUM_BARCODES}, retrying...")
            image_path = 'retrying_image_to_detect_all_barcodes'
            os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
            image = cv2.imread(image_path) # read the captured image with opencv

    print("Correct number of barcodes found: ", barcodes)
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
