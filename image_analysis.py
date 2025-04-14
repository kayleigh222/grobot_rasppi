import os
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image


# Define holder color range in HSV (red) - because red is at both ends of the hue spectrum, need two ranges
HOLDER_COLOR_LOWER_THRESHOLD_HSV = np.array([0, 150, 50])    # Lower bound of red
HOLDER_COLOR_UPPER_THRESHOLD_HSV = np.array([10, 255, 255])  # Upper bound of red

HOLDER_COLOR_LOWER_THRESHOLD_HSV_2 = np.array([170, 150, 50])   # Lower bound of red
HOLDER_COLOR_UPPER_THRESHOLD_HSV_2 = np.array([180, 255, 255])  # Upper bound of red

# Define leg color range in HSV (currently green)
LEG_COLOR_LOWER_THRESHOLD_HSV = np.array([30, 50, 50])   # Lower bound of green
LEG_COLOR_UPPER_THRESHOLD_HSV = np.array([90, 255, 255])  # Upper bound of green

# Define a minimum area threshold for contours to be considered a contour
MIN_HOLDER_AREA = 80000 
MIN_LEG_AREA = 4500

NUM_QRCODES = 1  # Set this to however many QR codes you expect
# NUM_BARCODES = 1  # Number of barcodes to on conveyors total

# ----------- PUSH LEG LOCATIONS -------------
def find_leg_top_conveyor(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # Convert the image to HSV color space to detect color easier
    # Create mask
    mask = cv2.inRange(hsv, LEG_COLOR_LOWER_THRESHOLD_HSV, LEG_COLOR_UPPER_THRESHOLD_HSV)
    cv2.imwrite('mask.jpg', mask)

    # Find contours of leg areas
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # take only the biggest contour
    leg_contour = max(contours, key=cv2.contourArea)

    # Filter contours based on size
    # leg_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > MIN_LEG_AREA]
    # draw the contours on the image
    # for leg_contour in leg_contours:
    cv2.drawContours(image, [leg_contour], -1, (0, 255, 0), 3)
    cv2.imwrite('image_with_leg_contours.jpg', image)    

    # get the leg contour with the highest x value
    # leg_contour = max(leg_contours, key=lambda cnt: cv2.boundingRect(cnt)[0])
    x, y, w, h = cv2.boundingRect(leg_contour)  # Get bounding box of the leg 

    return x, y # return the top left corner of the leg contour


# ----------- CONVEYOR LOCATIONS -------------
def get_conveyor_threshold(image):
    conveyor_left, conveyor_right = find_left_and_right_of_conveyors(image)
    distance = conveyor_right - conveyor_left
    threshold = conveyor_right - distance//2
    
    return threshold, conveyor_left, conveyor_right

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
            # cv2.line(image, (col_idx, 0), (col_idx, image.shape[0] - 1), (0, 255, 0), 2)
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

def get_left_edge_of_holder(holder_contour, image):
    # Get bounding box of the contour
    x, y, w, h = cv2.boundingRect(holder_contour)

    # # draw the bounding box on the image 
    # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle
    # cv2.imwrite('bounding_box_of_holder.jpg', image)

    # The top edge is at y with width w
    left_edge = [(x, y), (x + w, y)]
    print(f"Top edge coordinates: {left_edge}")
    return left_edge

def get_right_edge_of_holder(holder_contour, image):
    # Get bounding box of the contour
    x, y, w, h = cv2.boundingRect(holder_contour)

    # # draw the bounding box on the image 
    # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle
    # cv2.imwrite('bounding_box_of_holder.jpg', image)

    # The bottom edge is at y+h with width w
    right_edge = [(x, y + h), (x + w, y + h)]
    print(f"Bottom edge coordinates: {right_edge}")
    return right_edge

def get_bottom_edge_of_holder(holder_contour, image):
    print('finding bottom edge of holder')
    # Get bounding box of the contour
    x, y, w, h = cv2.boundingRect(holder_contour)
    print('got bounding rectangle of holder')

    # # draw the bounding box on the image 
    # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle
    # cv2.imwrite('bounding_box_of_holder.jpg', image)

    # The bottom edge is at y+h with width w
    bottom_edge = [(x, y), (x, y+h)]
    print(f"Bottom edge coordinates: {bottom_edge}")
    return bottom_edge

#conveyor_threshold: the y-coordinate threshold that divides the top and bottom conveyors
def top_holder_left_conveyor(image, conveyor_threshold, conveyors_left, conveyors_right):
    print('finding top holder left conveyor')
    left_conveyor_holders, right_conveyor_holders = holders_divided_into_conveyors(image, conveyor_threshold, conveyors_left, conveyors_right)
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
def top_holder_right_conveyor(image, conveyor_threshold, conveyors_left, conveyors_right):
    left_conveyor_holders, right_conveyor_holders = holders_divided_into_conveyors(image, conveyor_threshold, conveyors_left, conveyors_right)
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

def top_holder_with_barcode_right_conveyor(image, conveyor_threshold, conveyors_left, conveyors_right):
    left_conveyor_holders, right_conveyor_holders = holders_divided_into_conveyors(image, conveyor_threshold, conveyors_left, conveyors_right)
    top_holder_with_barcode = None
    # Check if there are any barcodes in the right conveyor
    while(top_holder_with_barcode == None):
        print('checking top barcode right conveyor')
        if right_conveyor_holders:
            # Find the barcode with the maximum x-coordinate in the right conveyor
            top_holder_right_conveyor = max(right_conveyor_holders, key=lambda holder: holder['holder_center'][0])
            if top_holder_right_conveyor['is_empty']:
                # remove from right_conveyor_holders
                print('removing top empty holder from right conveyor')
                right_conveyor_holders.remove(top_holder_right_conveyor)
            else:
                top_holder_with_barcode = top_holder_right_conveyor
        else:
            # Handle the case where there are no barcodes in the right conveyor
            print("Error: No barcodes found in right conveyor")
            break
    print("Top holder right conveyor empty:", top_holder_right_conveyor['is_empty'])
    return top_holder_right_conveyor

# conveyor_threshold: the y-coordinate threshold that divides the top and bottom conveyors
def holders_divided_into_conveyors(image, conveyor_threshold, conveyors_left, conveyors_right):  
    max_distance_between_holder_centre_and_barcode = (conveyors_right - conveyors_left) // 2 # half the width of a conveyor - max distance between centre of holder and barcode to be able to slide across is  
    holders = find_holders(image, max_distance_between_holder_centre_and_barcode)  # Get empty holder contours

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

    print('divided holders into left and right')

    # print('left conveyor holders: ', left_conveyor_holders)
    # print('right conveyor holders: ', right_conveyor_holders)

    return left_conveyor_holders, right_conveyor_holders    

# Finds all holders, returns the contours and empty status
def find_holders(image, max_dist_between_holder_center_and_barcode=400):
    print('finding holders')
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # Convert the image to HSV color space to detect color easier
    # Create mask
    mask1 = cv2.inRange(hsv, HOLDER_COLOR_LOWER_THRESHOLD_HSV, HOLDER_COLOR_UPPER_THRESHOLD_HSV)
    mask2 = cv2.inRange(hsv, HOLDER_COLOR_LOWER_THRESHOLD_HSV_2, HOLDER_COLOR_UPPER_THRESHOLD_HSV_2)
    red_mask = cv2.bitwise_or(mask1, mask2) # have to combine 2 masks because red appears at top and bottom of spectrum
    cv2.imwrite('mask.jpg', red_mask)

    # Find contours of blue areas
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours based on size
    holder_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > MIN_HOLDER_AREA]
     # print number of holder contours
    print(f"Number of holder contours found: {len(holder_contours)}")

    # Find barcodes in the image
    barcode_info = find_qrcodes(image)

    # List to store information about the holders
    holders_info = []

    # Iterate through contours
    for holder_contour in holder_contours:
        x, y, w, h = cv2.boundingRect(holder_contour)  # Get bounding box of holder
        holder_center = (x + w // 2, y + h // 2)  # Get center of blue patch
        print(f"Holder center: {holder_center}")

        near_barcode = (holder_center[0], holder_center[1] + max_dist_between_holder_center_and_barcode)

        # Check proximity to barcodes to determine if the holder is empty
        barcode_close = False

        # draw a circle representing the max distance between a holder center and its barcode
        cv2.circle(image, near_barcode, max_dist_between_holder_center_and_barcode, (0, 0, 255), 2)

        for barcode in barcode_info:
            # Compute Euclidean distance to barcode
            distance = np.sqrt((near_barcode[0] - barcode[1][0])**2 + 
                               (near_barcode[1] - barcode[1][1])**2)

            if distance < max_dist_between_holder_center_and_barcode:  # Adjust distance threshold based on image scale
                barcode_close = True
                break  # No need to check further if already too close
        
        # Store the contour, empty status, and barcode (if not empty)
        holder_info = {
            'contour': holder_contour,
            'is_empty': not barcode_close,  # If not too close to barcode, it's considered empty
            'holder_center': holder_center,
            'barcode_data': barcode[0] if barcode_close else None  # Store barcode data if not empty
        }
        holders_info.append(holder_info)

    # Optionally, draw contours for all holders
    # for holder in holders_info:
    #     color = (255, 0, 0) if holder['is_empty'] else (0, 255, 0)  # Blue for empty, green for not empty
    #     cv2.drawContours(image, [holder['contour']], -1, color, 3)  # Draw each holder's contour with different color

    print('saving image with all holders')
    cv2.imwrite('image_with_all_holders.jpg', image)
    print('finished saving image with all holders')

    return holders_info


# -------- BARCODE LOCATIONS ----------------

#conveyor_threshold: the y-coordinate threshold that divides the top and bottom conveyors
def get_top_barcode_right_conveyor(image, conveyor_threshold):
    left_conveyor_barcodes, right_conveyor_barcodes = barcodes_divided_into_conveyors(image, conveyor_threshold)
    # Check if there are any barcodes in the right conveyor
    if right_conveyor_barcodes:
        # Find the barcode with the maximum x-coordinate in the right conveyor
        top_barcode_right_conveyor = max(right_conveyor_barcodes, key=lambda barcode: barcode[1][0])
    else:
        # Handle the case where there are no barcodes in the right conveyor
        top_barcode_right_conveyor = None  # or some default value/message
    print("Top barcode right conveyor:", top_barcode_right_conveyor)
    return top_barcode_right_conveyor

#conveyor_threshold: the y-coordinate threshold that divides the top and bottom conveyors
def get_top_barcode_left_conveyor(image, conveyor_threshold):
    left_conveyor_barcodes, right_conveyor_barcodes = barcodes_divided_into_conveyors(image, conveyor_threshold)
    # Check if there are any barcodes in the right conveyor
    if left_conveyor_barcodes:
        print('have left conveyor barcodes')
        # Find the barcode with the maximum x-coordinate in the right conveyor
        top_barcode_left_conveyor = max(left_conveyor_barcodes, key=lambda barcode: barcode[1][0])
    else:
        print('no left conveyor barcodes')
        # Handle the case where there are no barcodes in the right conveyor
        top_barcode_left_conveyor = None  # or some default value/message
    print("Top barcode left conveyor:", top_barcode_left_conveyor)
    return top_barcode_left_conveyor

def barcodes_divided_into_conveyors(image, conveyor_threshold):
    
    barcode_info = find_qrcodes(image)  # Get barcode center coordinates
    if not barcode_info:
        return [], []  # No barcodes found

    # Initialize the lists for left and right conveyor barcodes
    left_conveyor_barcodes = []
    right_conveyor_barcodes = []

    # Iterate through the barcode centers and classify them based on their y values
    for barcode in barcode_info:
        x, y = barcode[1]  # Unpack the barcode center coordinates
        if y < conveyor_threshold:
            left_conveyor_barcodes.append(barcode)  # Barcode is above the threshold (left conveyor)
        else:
            right_conveyor_barcodes.append(barcode)  # Barcode is below the threshold (right conveyor)

    return left_conveyor_barcodes, right_conveyor_barcodes   
 
def find_qrcodes(image):
    """
    Detects QR codes in an image using pyzbar, retries capturing a new image if the expected number of QR codes 
    is not found, and returns their center coordinates along with the decoded QR code data.

    Parameters:
        image (numpy.ndarray): The input image in which QR codes need to be detected.

    Returns:
        list of tuples: Each tuple contains:
            - data (str): The decoded data from the QR code.
            - center (tuple): The (x, y) coordinates of the QR code's center.
    """
    num_qrcodes_found = 0
    qrcode_info = []

    cv2.imwrite('image_to_detect_qrcodes.jpg', image)

    while num_qrcodes_found < NUM_QRCODES:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        equalized = cv2.equalizeHist(blurred)
        cv2.imwrite('filtered_image_to_detect_qrcodes.jpg', equalized) # save the image to detect qrcodes
        detected_qrcodes = decode(equalized)

        num_qrcodes_found = len(detected_qrcodes)
        qrcode_info = []

        for qr in detected_qrcodes:
            data = qr.data.decode("utf-8")

            # Get bounding box
            x, y, w, h = qr.rect
            centre_x = x + w / 2
            centre_y = y + h / 2

            qrcode_info.append((data, (centre_x, centre_y)))

            # Debug
            print(f"QR Code Data: {data}")
            print(f"QR Code Center: ({centre_x:.1f}, {centre_y:.1f})")

        if num_qrcodes_found < NUM_QRCODES:
            print(f"Found {num_qrcodes_found} QR codes, expected {NUM_QRCODES}, retrying...")
            image_path = 'retrying_image_to_detect_all_qrcodes.jpg'
            os.system(f"rpicam-still --output {image_path} --nopreview")
            image = cv2.imread(image_path)

    print("Correct number of QR codes found.")
    return qrcode_info

# def find_barcodes(image):
#      """
#     Detects barcodes in an image, retries capturing a new image if the expected number of barcodes is not found, 
#     and returns their center coordinates along with the decoded barcode data.

#     Parameters:
#         image (numpy.ndarray): The input image in which barcodes need to be detected.

#     Returns:
#         list of tuples: A list where each tuple contains:
#             - center (tuple): The (x, y) coordinates of the barcode's center.
#             - data (str): The decoded data from the barcode.

#     Example Output:
#         (["Plant 4", (150.5, 200.0)), ("Plant 1", (300.0, 450.0))]
#     """
#      num_barcodes_found = 0
#      cv2.imwrite('image_to_detect_barcodes.jpg', image) # save the image to detect barcodes
#      while(num_barcodes_found < NUM_BARCODES):
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#         equalized = cv2.equalizeHist(gray)
#         barcodes = decode(equalized) # detect barcodes
#         num_barcodes_found = len(barcodes)
#         if num_barcodes_found < NUM_BARCODES:
#             print("Barcodes: ", barcodes)
#             print(f"Found {num_barcodes_found} barcodes, expected {NUM_BARCODES}, retrying...")
#             image_path = 'retrying_image_to_detect_all_barcodes'
#             os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
#             image = cv2.imread(image_path) # read the captured image with opencv
            
#      print("Correct number of barcodes found: ", barcodes)
#      barcode_info = []  # List to store center coordinates

#     # loop through each detected barcode
#      for barcode in barcodes:
#         # Get the rectangle around the barcode
#         x, y, w, h = barcode.rect
#         centre_x = x + w/2
#         centre_y = y + h/2

#         barcode_data = barcode.data.decode('utf-8')  # Decode barcode data

#         barcode_info.append((barcode_data, (centre_x, centre_y)))  # Store center and data as a tuple

#         # IF WANT TO VISUALISE:
#         # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red rectangle
#         # cv2.circle(image, (int(centre_x), int(centre_y)), radius=3, color=(0, 0, 255), thickness=-1)  # Red filled dot at centre of barcode
#         # cv2.imwrite('captured_image_with_barcodes.jpg', image)
    
#         # IF DEBUGGING:
#         print(f"Barcode Location: (x: {x}, y: {y}, width: {w}, height: {h})")
#         print(f"Barcode Data: {barcode.data.decode('utf-8')}")
    
#      return barcode_info  # Return the list of center coordinates
