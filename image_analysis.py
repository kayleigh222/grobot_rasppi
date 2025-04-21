import os
import cv2
import numpy as np
from pyzbar.pyzbar import decode


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

def capture_image(path="captured_image.jpg"):
    os.system(f"rpicam-still --output {path} --nopreview")
    return cv2.imread(path)

# ----------- LEG DETECTION -------------
def find_leg_contours(image):
    """
    Detects contours of legs in the image.
    - Assumes legs are green and defined by a color mask.
    - Assumes there are two legs, so picks the two largest green contours.
    - Draws and saves the mask and contour outline.
    Returns: list of contours.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LEG_COLOR_LOWER_THRESHOLD_HSV, LEG_COLOR_UPPER_THRESHOLD_HSV)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("No leg contours found.")  
        
    # filter to the two largest contours
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]
    
    # draw leg contours in blue
    cv2.drawContours(image, contours, -1, (255, 0, 0), 3)
    
    for contour in contours:
        cv2.drawContours(image, [contour], -1, (0, 255, 0), 3)
    
    cv2.imwrite('image_with_leg_contours.jpg', image)
    
    return contours

def find_leg_top_conveyor(leg_contours):
    """
    Detects the top-left corner of the top leg contour on the conveyor.
    - Assumes legs are green and defined by a color mask.
    - Draws and saves the mask and contour outline.
    Returns: (x, y) coordinate of top-left corner of bounding box.
    """
    top_leg_contour = max(leg_contours, key=lambda c: cv2.boundingRect(c)[0]) # pick the leg with the greatest x value

    x, y, w, h = cv2.boundingRect(top_leg_contour)
    return x, y

def find_leg_bottom_conveyor(leg_contours):
    """
    Detects the top-right corner of the bottom leg contour on the conveyor.
    - Assumes legs are green and defined by a color mask.
    - Draws and saves the mask and contour outline.
    Returns: (x, y) coordinate of top-left corner of bounding box.
    """
    leg_contour = min(leg_contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(leg_contour)
    return x+w, y+h

# ----------- CONVEYOR DETECTION -------------
def get_conveyor_threshold(image):
    """
    Returns the vertical threshold that splits the top and bottom conveyors.
    Uses vertical bounds from `find_left_and_right_of_conveyors`.
    Returns: threshold, left, right bounds.
    """
    conveyor_left, conveyor_right = find_left_and_right_of_conveyors(image)
    distance = conveyor_right - conveyor_left
    threshold = conveyor_right - distance // 2
    return threshold, conveyor_left, conveyor_right

def find_top_and_bottom_of_conveyors(image):
    """
    Finds top and bottom edges of conveyors by scanning columns for darkness.
    Returns: (top, bottom) column indices.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary_mask = np.where(gray < 50, 1, 0) # Create a binary mask where intensity < 50 is set to 1, and others are set to 0
    cv2.imwrite('binary_mask_for_conveyors.jpg', binary_mask * 255)  # Save the binary mask for debugging
    # find the contours of the dark sections
    # contours = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    # # pick the contour with the largest area
    # largest_contour = max(contours, key=cv2.contourArea) if contours else None
    # if largest_contour is None:
    #     print("No contours found")
    #     return 0, 0    
    
    threshold = 500 # minimum number of dark pixels for a column to be part of a conveyor

    # Bottom (leftmost dark column)
    conveyor_bottom = next((i for i, col in enumerate(binary_mask.T) if np.sum(col) >= threshold), 0)

    # Top (rightmost dark column)
    conveyor_top = next((i for i in range(binary_mask.shape[1] - 1, -1, -1)
                         if np.sum(binary_mask[:, i]) >= threshold), 0)
    return conveyor_top, conveyor_bottom

def find_left_and_right_of_conveyors(image):
    """
    Finds left and right edges of conveyors by scanning rows for darkness.
    Returns: (left, right) row indices.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary_mask = np.where(gray < 50, 1, 0) # Create a binary mask where intensity < 50 is set to 1, and others are set to 0
    threshold = 2000 # minimum number of dark pixels for a row to be considered part of the conveyor

    conveyor_left = next((i for i, row in enumerate(binary_mask) if np.sum(row) >= threshold), 0)
    conveyor_right = next((i for i in range(binary_mask.shape[0] - 1, -1, -1)
                           if np.sum(binary_mask[i]) >= threshold), 0)
    return conveyor_left, conveyor_right

# ----------- HOLDER DETECTION -------------
def get_bottom_left_corner(corners):
    # takes an array of corner coordinates and returns the bottom leftmost
    return min(corners, key=lambda pt: 0.2*pt[0] - 0.8*pt[1])

def get_top_left_corner(corners):
    # takes an array of corner coordinates and returns the top leftmost
    return min(corners, key=lambda pt: 0.2*pt[0] + 0.8*pt[1])

def get_bottom_edge_of_holder(holder_contour):
    """
    Returns the bottom edge of a holder's bounding box.
    """
    x, y, w, h = cv2.boundingRect(holder_contour)
    bottom_edge = [(x, y), (x, y + h)]
    return bottom_edge

def top_holder_left_conveyor(holders_divided_into_conveyors):
    """
    Returns the holder on the left conveyor with the largest x (i.e., furthest right in the image, closest to top of conveyors in real life).
    """
    left_conveyor_holders, _ = holders_divided_into_conveyors
    if not left_conveyor_holders:
        return None

    top_holder = max(left_conveyor_holders, key=lambda h: h['holder_center'][0])
    return top_holder

def top_holder_right_conveyor(holders_divided_into_conveyors):
    """
    Returns the holder on the right conveyor with the largest x (i.e., furthest right in the image, closest to top of conveyors in real life).
    """
    _, right_conveyor_holders = holders_divided_into_conveyors
    if not right_conveyor_holders:
        return None

    top_holder = max(right_conveyor_holders, key=lambda h: h['holder_center'][0])
    return top_holder

def bottom_holder_right_conveyor(holders_divided_into_conveyors):
    """
    Returns the holder on the right conveyor with the largest x (i.e., furthest right in the image, closest to top of conveyors in real life).
    """
    _, right_conveyor_holders = holders_divided_into_conveyors
    if not right_conveyor_holders:
        return None

    top_holder = min(right_conveyor_holders, key=lambda h: h['holder_center'][0])
    return top_holder

def bottom_holder_left_conveyor(holders_divided_into_conveyors):
    """
    Returns the holder on the left conveyor with the largest x (i.e., furthest right in the image, closest to top of conveyors in real life).
    """
    left_conveyor_holders, _ = holders_divided_into_conveyors
    if not left_conveyor_holders:
        return None

    top_holder = min(left_conveyor_holders, key=lambda h: h['holder_center'][0])
    return top_holder

def top_holder_with_barcode_right_conveyor(holders_divided_into_conveyors):
    """
    Loops through right conveyor holders and returns the top-most non-empty holder.
    Removes empty holders from the list.
    """
    _, right_conveyor_holders = holders_divided_into_conveyors
    top_holder_with_barcode = None

    while top_holder_with_barcode is None:
        if not right_conveyor_holders:
            print("Error: No qrcodes found in right conveyor")
            break

        top_candidate = max(right_conveyor_holders, key=lambda h: h['holder_center'][0])
        if top_candidate['is_empty']:
            right_conveyor_holders.remove(top_candidate)
        else:
            top_holder_with_barcode = top_candidate

    if top_holder_with_barcode:
        print("Top holder with qrcode: ", top_holder_with_barcode['holder_center'])
    return top_holder_with_barcode

def bottom_holder_with_barcode_left_conveyor(holders_divided_into_conveyors):
    """
    Loops through right conveyor holders and returns the top-most non-empty holder.
    Removes empty holders from the list.
    """
    left_conveyor_holders, _ = holders_divided_into_conveyors
    bottom_holder_with_barcode = None

    while bottom_holder_with_barcode is None:
        if not left_conveyor_holders:
            print("Error: No qrcodes found in left conveyor")
            break

        top_candidate = min(left_conveyor_holders, key=lambda h: h['holder_center'][0])
        if top_candidate['is_empty']:
            left_conveyor_holders.remove(top_candidate)
        else:
            bottom_holder_with_barcode = top_candidate

    if bottom_holder_with_barcode:
        print("Bottom holder with qrcode: ", bottom_holder_with_barcode['holder_center'])
    return bottom_holder_with_barcode

def extract_holder_corners(image, contour, num_corners=8, quality_level=0.02, min_distance=20):
    approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
    blank_image = np.zeros_like(image)
    cv2.drawContours(blank_image, [approx], -1, (255, 255, 255), 1)
    gray = cv2.cvtColor(blank_image, cv2.COLOR_BGR2GRAY)
    corners = cv2.goodFeaturesToTrack(gray, maxCorners=num_corners, qualityLevel=quality_level, minDistance=min_distance)
    return np.intp(corners).reshape(-1, 2) if corners is not None else [] # reshape the corners into array of points (cv2 returns it with weird structure to suit 3D stuff)

def divide_holders_into_conveyors(conveyor_threshold, holders_from_find_holders):
    """
    Divides detected holders into left or right conveyors based on y-coordinate.
    Returns: (left_holders, right_holders)
    """
    left_conveyor_holders = []
    right_conveyor_holders = []

    for holder in holders_from_find_holders:
        _, y = holder['holder_center']
        if y < conveyor_threshold:
            left_conveyor_holders.append(holder)
        else:
            right_conveyor_holders.append(holder)

    return left_conveyor_holders, right_conveyor_holders

# Finds all holders, returns the contours and empty status
def find_holders(image, max_dist_between_holder_center_and_barcode=500):
    """
    Detects holder regions (red-colored contours) in the input image and determines whether 
    each holder is empty or occupied based on proximity to a detected QR code.

    Parameters:
        image (numpy.ndarray): A BGR image (as read by OpenCV) in which holders and qrcodes are to be detected.
        max_dist_between_holder_center_and_barcode (int): The maximum allowed distance (in pixels) between 
            the holder's center and a nearby qrcode
     for the holder to be considered "occupied".

    Returns:
        holders_info (list of dict): A list where each dictionary contains information about a detected holder:
            - 'contour' (numpy.ndarray): The contour of the holder region.
            - 'is_empty' (bool): True if no qrcode
     was found near the holder, otherwise False.
            - 'holder_center' (tuple of int): The (x, y) coordinates of the center of the holder's bounding box.
            - 'id' (str or None): The decoded string from the nearby QR code if present; otherwise None.
    """
    # Convert image to HSV for better color filtering
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Split channels
    h, s, v = cv2.split(hsv)

    # Equalize the V channel
    v_eq = cv2.equalizeHist(v)

    # Merge back and convert to HSV image
    hsv_eq = cv2.merge((h, s, v_eq))

    # Now apply your red masks
    mask1 = cv2.inRange(hsv_eq, HOLDER_COLOR_LOWER_THRESHOLD_HSV, HOLDER_COLOR_UPPER_THRESHOLD_HSV)
    mask2 = cv2.inRange(hsv_eq, HOLDER_COLOR_LOWER_THRESHOLD_HSV_2, HOLDER_COLOR_UPPER_THRESHOLD_HSV_2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    cv2.imwrite('red_mask_equalized.jpg', red_mask)

    # # Mask red hues (both ends of HSV spectrum for red)
    # mask1 = cv2.inRange(hsv, HOLDER_COLOR_LOWER_THRESHOLD_HSV, HOLDER_COLOR_UPPER_THRESHOLD_HSV)
    # mask2 = cv2.inRange(hsv, HOLDER_COLOR_LOWER_THRESHOLD_HSV_2, HOLDER_COLOR_UPPER_THRESHOLD_HSV_2)
    # red_mask = cv2.bitwise_or(mask1, mask2)
    # cv2.imwrite('red_mask.jpg', red_mask)  # Save the mask for debugging

    # Find contours of red areas (potential holders)
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    holder_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > MIN_HOLDER_AREA]
    print(f"Number of holder contours found: {len(holder_contours)}")

    # Detect qrcodes
    qrcodes = find_qrcodes(image)

    holders_info = []

    # Analyze each potential holder
    for holder_contour in holder_contours:
        x, y, w, h = cv2.boundingRect(holder_contour)
        holder_center = (x + w // 2, y + h // 2)
        print(f"Holder center: {holder_center}")

        near_barcode = (holder_center[0], holder_center[1] + 450)

        # Determine if a qrcode is nearby
        barcode_close = False
        closest_barcode = None

        for qrcode in qrcodes:
            distance = np.linalg.norm(np.array(near_barcode) - np.array(qrcode[1]))
            if distance < max_dist_between_holder_center_and_barcode:
                barcode_close = True
                closest_barcode = qrcode
                break

        # Save holder info
        holders_info.append({
            'contour': holder_contour,
            'is_empty': not barcode_close,
            'holder_center': holder_center,
            'id': closest_barcode[0] if barcode_close else None
        })

    return holders_info

# -------- QR CODE DETECTION ----------------
def get_bottom_qr_right_conveyor(image, conveyor_threshold):
    """
    Finds the bottom QR code on the right conveyor (y > threshold), based on the lowest x-position.
    """
    _, right_conveyor_qrcodes = qrs_divided_into_conveyors(image, conveyor_threshold)
    if right_conveyor_qrcodes:
        return min(right_conveyor_qrcodes, key=lambda b: b[1][0])
    print("No right conveyor qrcodes found.")
    return None


def get_top_qr_left_conveyor(image, conveyor_threshold):
    """
    Finds the top qrcode on the left conveyor (y < threshold), based on the highest x-position.
    """
    left_conveyor_qrcodes, _ = qrs_divided_into_conveyors(image, conveyor_threshold)
    if left_conveyor_qrcodes:
        return max(left_conveyor_qrcodes, key=lambda b: b[1][0])
    print("No left conveyor qrcodes found.")
    return None

def get_top_qr_right_conveyor(image, conveyor_threshold):
    """
    Finds the top qrcode on the left conveyor (y < threshold), based on the highest x-position.
    """
    _, right_conveyor_qrcodes = qrs_divided_into_conveyors(image, conveyor_threshold)
    if right_conveyor_qrcodes:
        return max(right_conveyor_qrcodes, key=lambda b: b[1][0])
    print("No left conveyor qrcodes found.")
    return None

def qrs_divided_into_conveyors(image, conveyor_threshold):
    """
    Divides detected qrcodes into top and bottom conveyor based on their y-position.
    Returns two lists of (data, center) tuples.
    """
    qrcodes = find_qrcodes(image)
    if not qrcodes:
        return [], []

    left = [b for b in qrcodes if b[1][1] < conveyor_threshold]
    right = [b for b in qrcodes if b[1][1] >= conveyor_threshold]
    return left, right 
 
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

    while num_qrcodes_found < NUM_QRCODES:
        # Preprocess for better QR detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        equalized = cv2.equalizeHist(blurred)
        cv2.imwrite('equalized_qr_image.jpg', equalized)  # Save the equalized image for debugging

        # Decode QR codes
        detected_qrcodes = decode(equalized)
        num_qrcodes_found = len(detected_qrcodes)
        qrcode_info = []

        for qr in detected_qrcodes:
            data = qr.data.decode("utf-8")
            x, y, w, h = qr.rect
            center = (x + w / 2, y + h / 2)
            qrcode_info.append((data, center))

            print(f"QR Code Data: {data}")
            print(f"QR Code Center: ({center[0]:.1f}, {center[1]:.1f})")

        if num_qrcodes_found < NUM_QRCODES:
            print(f"Found {num_qrcodes_found} QR codes, expected {NUM_QRCODES}, retrying...")
            image_path = 'retrying_image_to_detect_all_qrcodes.jpg'
            os.system(f"rpicam-still --output {image_path} --nopreview")
            image = cv2.imread(image_path)

    print("Correct number of QR codes found.")
    return qrcode_info

if __name__ == "__main__":
    # image = capture_image()
    image = cv2.imread('captured_image.jpg')
    print("Image loaded successfully.")
    holders = find_holders(image)
    print(f"Number of holders found: {len(holders)}")
    conveyor_threshold, conveyors_left, conveyors_right = get_conveyor_threshold(image) # find threshold between left and right conveyor
    holders_divided_into_conveyors = divide_holders_into_conveyors(conveyor_threshold, holders_from_find_holders=holders)
    print("Divided holders into conveyors.")
    top_holder_right = top_holder_right_conveyor(holders_divided_into_conveyors)
    print("Extracting corners")
    corners_right = extract_holder_corners(image, top_holder_right['contour'], 16, 0.04, 50)
    for corner in corners_right:
        x, y = corner.ravel()
        cv2.circle(image, (x, y), 10, (255, 0, 0), -1)  # Green circle for right corners
    cv2.imwrite('corners_right.jpg', image)