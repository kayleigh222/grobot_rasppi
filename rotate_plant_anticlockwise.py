import os
import cv2
from bottom_conveyor_motor_code import clean_up_bottom_conveyor, set_up_bottom_conveyor, step_bottom_conveyor_backward, step_bottom_conveyor_forward
import pigpio
import RPi.GPIO as GPIO
import argparse
import gc
import numpy as np
import time
import threading
from image_analysis import bottom_holder_left_conveyor, bottom_holder_right_conveyor, bottom_holder_with_barcode_left_conveyor, capture_image, divide_holders_into_conveyors, extract_holder_corners, find_holders, find_leg_bottom_conveyor, find_leg_contours, find_leg_top_conveyor, get_bottom_left_corner, get_bottom_qr_right_conveyor, get_leftmost_corner, get_rightmost_corner, get_top_left_corner, get_top_qr_left_conveyor, top_holder_left_conveyor, top_holder_right_conveyor, get_conveyor_threshold, top_holder_with_barcode_right_conveyor, get_bottom_edge_of_holder
from calibration import BOTTOM_CONVEYOR_SPEED_BACKWARD, BOTTOM_CONVEYOR_SPEED_FORWARD, TOP_CONVEYOR_SPEED_BACKWARD, TOP_CONVEYOR_SPEED_FORWARD, calibrate_bottom_conveyor_motor, calibrate_top_conveyor_motor, calibrate_vertical_conveyor_motors, load_variables, LEFT_CONVEYOR_SPEED, RIGHT_CONVEYOR_SPEED
from servo_motor_code import clean_up_servo, set_up_servo, sweep_servo
import servo_motor_code
from top_conveyor_motor_code import clean_up_top_conveyor, set_up_top_conveyor, step_top_conveyor_backward, step_top_conveyor_forward
from vertical_conveyor_left_motor_code import move_left_conveyor, set_up_left_conveyor, clean_up_left_conveyor
from vertical_conveyor_right_motor_code import move_right_conveyor, set_up_right_conveyor, clean_up_right_conveyor

# running with flag --calibrate in command line will trigger calibration before movement
parser = argparse.ArgumentParser(description="Run plant position updater with optional calibration.")
parser.add_argument('--calibrate', action='store_true', help='Run motor calibration before starting.')
args = parser.parse_args()

DISTANCE_BELOW_TARGET_HOLDER_TO_SLIDE_ACROSS = 20 # pixels - max vertical distance between holders to be able to slide across

# variables for PID control - used to move conveyor to align holders before sliding tray across
previous_error = 0
integral = 0

def pid_control(error, Kp=0.7, Ki=0.005, Kd=0.05): # error is the difference between the target value and the current value
    global previous_error, integral # integral used to be 0.1

    print("Error: ", error)

    integral += error
    derivative = error - previous_error
    previous_error = error

    print('Integral: ', integral)
    print('Derivative: ', derivative)
    print('K_p:', Kp)
    print('K_i:', Ki)
    print('K_d:', Kd)

    # Calculate how much to move the conveyor
    adjustment = Kp * error + Ki * integral + Kd * derivative
    print("Adjustment: ", adjustment)
    return adjustment

def update_bottom_left_plant_position(image, conveyor_threshold):
    """
    Identifies the x-coordinate of the bottom edge of the bottom holder with a visible QR code 
    on the left-side conveyor.

    Args:
        image (np.ndarray): The input image from the conveyor camera.
        conveyor_threshold (int): Pixel value separating left and right conveyors.

    Returns:
        int: X-coordinate of the bottom edge of the topmost right conveyor holder with a barcode.
        id (str or None): The decoded string from the holder's QR code if present; otherwise None.
    """
    holders = find_holders(image)
    holders_divided = divide_holders_into_conveyors(conveyor_threshold, holders)
    bottom_plant = bottom_holder_with_barcode_left_conveyor(holders_divided)
    bottom = get_bottom_edge_of_holder(bottom_plant['contour'])
    return bottom[0][0], bottom_plant['id']

def update_top_right_plant_position(image, conveyor_threshold):
    """
    Identifies the x-coordinate of the bottom edge of the topmost holder with a visible barcode 
    on the right-side conveyor.

    Args:
        image (np.ndarray): The input image from the conveyor camera.
        conveyor_threshold (int): Pixel value separating left and right conveyors.

    Returns:
        int: X-coordinate of the bottom edge of the topmost right conveyor holder with a barcode.
        id (str or None): The decoded string from the holder's QR code if present; otherwise None.
    """
    holders = find_holders(image)
    holders_divided = divide_holders_into_conveyors(conveyor_threshold, holders)
    top_plant = top_holder_with_barcode_right_conveyor(holders_divided)
    bottom = get_bottom_edge_of_holder(top_plant['contour'])
    return bottom[0][0], top_plant['id']

# ----------- TURN ON LIGHTS BY RUNNING SERVO MOTOR IN SEPARATE THREAD TO TRIGGER MOTION SENSOR --------
try:
    GPIO.cleanup()  # Clean up GPIO settings
    gc.collect() # run garbage collector to free up memory
    # os.system("sudo pigpiod")
    # time.sleep(1)  # Give it a second to start
    # pi = pigpio.pi() # Connect to pigpio daemon
    # set_up_servo(pi) # Set up servo motor
    # servo_motor_code.sweeping = True # Control flag
    # servo_thread = threading.Thread(target=sweep_servo, args=(pi,)) # Create thread to run servo motor
    # servo_thread.start()

    if args.calibrate:
        print("Running motor calibration...")
        calibrate_vertical_conveyor_motors()
        calibrate_top_conveyor_motor()
        calibrate_bottom_conveyor_motor()
        print("Calibration complete.")
    else:
        print("Skipping calibration.")

    # # ----------- TAKE INITIAL IMAGE AND LOAD CALIBRATION VARIABLES ------------------
    image = capture_image()
    calibration_variables = load_variables() 

    # # ---------- FIND OUTLINES OF CONVEYOR TO GET TARGET LOCATION FOR TOP RIGHT TRAY -----------
    conveyor_threshold, conveyors_left, conveyors_right, top_conveyor, bottom_conveyor = get_conveyor_threshold(image) # find threshold between left and right conveyor
    conveyor_height = top_conveyor - bottom_conveyor
    leg_contours = find_leg_contours(image)
    top_conveyor_leg_top_left_x, top_conveyor_leg_top_left_y  = find_leg_top_conveyor(leg_contours)
    # draw a circle at top conveyor leg top left
    # cv2.circle(image, (top_conveyor_leg_top_left_x, top_conveyor_leg_top_left_y), 10, (255, 0, 0), 5)  # Green circle
    target_location_for_top_tray = int(top_conveyor_leg_top_left_x - 200) # don't increase this, or won't be close enough for conveyor to push across. if target too far up to reach, tilt top conveyor forward
    # ----------- FIND TOP HOLDER ON RIGHT CONVEYOR ------------------
    bottom_of_top_holder_right_conveyor_x_coord, top_right_plant_id = update_top_right_plant_position(image, conveyor_threshold)
    distance_from_bottom_of_holder_to_target = target_location_for_top_tray - bottom_of_top_holder_right_conveyor_x_coord

    print("Moving right conveyor up close enough to slide tray across.")
    print("Distance to target location to slide across: ", distance_from_bottom_of_holder_to_target)
    num_moves = 0

    # ------ USE PID CONTROL TO MOVE TOP HOLDER ON RIGHT CONVEYOR UP CLOSE ENOUGH TO SLIDE TRAY ACROSS -----------
    while(distance_from_bottom_of_holder_to_target > 50): # TODO: base target location on end of top conveyor leg for better relability
        # Visualise current (red) and target (green) location
        cv2.line(image, (target_location_for_top_tray, 0), (target_location_for_top_tray, image.shape[0]), (0, 0, 255), 2)  
        cv2.line(image, (int(bottom_of_top_holder_right_conveyor_x_coord), 0), (int(bottom_of_top_holder_right_conveyor_x_coord), image.shape[0]), (0, 0, 255), 2) 
        cv2.imwrite("before_move_right_holder_to_top.jpg", image)

        # move conveyor
        steps_to_take = int(pid_control(distance_from_bottom_of_holder_to_target, Kp=(1/calibration_variables[RIGHT_CONVEYOR_SPEED])))
        set_up_right_conveyor()
        move_right_conveyor(steps_to_take)
        clean_up_right_conveyor()

        # capture new image
        image = capture_image()

        # find new position of top holder
        bottom_of_top_holder_right_conveyor_x_coord, top_right_plant_id = update_top_right_plant_position(image, conveyor_threshold)

        # find new distance left to travel
        print("target location: ", target_location_for_top_tray)
        print("bottom of top holder right conveyor: ", bottom_of_top_holder_right_conveyor_x_coord)
        distance_from_bottom_of_holder_to_target = target_location_for_top_tray - bottom_of_top_holder_right_conveyor_x_coord
        print("Distance to target location to slide across: ", distance_from_bottom_of_holder_to_target)
        if(num_moves > 5): # if get stuck in loop moving up, target is probably too high
            print("STUCK IN LOOP - TARGET LIKELY WRONG")
            break
        num_moves += 1

    print("Finished moving top holder on right conveyor up close enough to slide tray across. Distance to target location now ", distance_from_bottom_of_holder_to_target)
    gc.collect() # run garbage collector to free up memory

    # --------- FIND DESIRED POSITION FOR TOP LEFT HOLDER -----------
    # get corners of each holder
    holders = find_holders(image)
    holders_divided_into_conveyors = divide_holders_into_conveyors(conveyor_threshold, holders_from_find_holders=holders) # TODO - this is a bit sus, need to check if it work
    top_holder_right = top_holder_right_conveyor(holders_divided_into_conveyors)
    top_holder_left = top_holder_left_conveyor(holders_divided_into_conveyors)
    image_with_contours = image.copy()

    print('finding corners for right holder')
    corners_right = extract_holder_corners(image, top_holder_right['contour'], 20, 0.04, 45)

    gc.collect() # run garbage collector to free up memory

    print('finding corners for left contour')
    corners_left = extract_holder_corners(image, top_holder_left['contour'], 8, 0.02, 20)

    gc.collect() # run garbage collector to free up memory

    print('got corners - drawing')

    # Draw the corners on the image
    for corner in corners_right:
        x, y = corner.ravel()
        cv2.circle(image_with_contours, (x, y), 10, (255, 0, 0), -1)  # Green circle for right corners

    for corner in corners_left:
        x, y = corner.ravel()
        cv2.circle(image_with_contours, (x, y), 10, (0, 0, 255), -1)  # Red circle for left corners

    # Save the image with detected corners
    cv2.imwrite("image_with_corners.jpg", image_with_contours)
    print("Image with corners saved as image_with_corners.jpg")

    del image_with_contours

    bottom_left_corner_left_holder = get_bottom_left_corner(corners_left)
    del corners_left

    # get two corners with lowest y value on right contour
    top_left_corner_right_holder = get_top_left_corner(corners_right) 

    target_x_value = top_left_corner_right_holder[0]
    print("Target x value: ", target_x_value)

    # visualize positions on image
    cv2.circle(image, (bottom_left_corner_left_holder[0], bottom_left_corner_left_holder[1]), 10, (0, 255, 255), -1)  # Yellow circle for left edge
    cv2.circle(image, (top_left_corner_right_holder[0], top_left_corner_right_holder[1]), 10, (0, 255, 255), -1)  # Yellow circle for right edge
    cv2.imwrite("image_before_move_left_holder.jpg", image)

    distance_below_target = target_x_value - bottom_left_corner_left_holder[0]

    print("Distance between holders: ", distance_below_target)

    # ------ USE PID CONTROL TO MOVE LEFT HOLDER TO ALIGN WITH RIGHT HOLDER -----------
    while(distance_below_target > DISTANCE_BELOW_TARGET_HOLDER_TO_SLIDE_ACROSS or distance_below_target < 0):
        if (distance_below_target < 0):
            steps_to_take = int(-20)
        else:
            steps_to_take = int(pid_control(distance_below_target, Kp=(1/calibration_variables[LEFT_CONVEYOR_SPEED])))
        if(steps_to_take == 0):
            print("No steps to take")
            break
        print("Steps to take: ", steps_to_take)
        
        # move conveyor
        set_up_left_conveyor()
        move_left_conveyor(steps_to_take)
        clean_up_left_conveyor()

        #take new image
        del image
        gc.collect() # run garbage collector to free up memory
        image = capture_image()

        # find new left holder position
        holders = find_holders(image)
        holders_divided_into_conveyors = divide_holders_into_conveyors(conveyor_threshold, holders_from_find_holders=holders) # TODO - this is a bit sus, need to check if it work
        top_holder_left = top_holder_left_conveyor(holders_divided_into_conveyors)

        print('finding corners for left contour')
        corners_left = extract_holder_corners(image, top_holder_left['contour'], 8, 0.02, 20)
        bottom_left_corner_left_holder = get_bottom_left_corner(corners_left)

        del corners_left

        # visualize on image
        cv2.circle(image, (bottom_left_corner_left_holder[0], bottom_left_corner_left_holder[1]), 10, (0, 255, 255), -1)  # Yellow circle for left edge
        cv2.circle(image, (top_left_corner_right_holder[0], top_left_corner_right_holder[1]), 10, (0, 255, 255), -1)  # Yellow circle for right edge
        cv2.imwrite("image_before_move_left_holder.jpg", image)

        distance_below_target = target_x_value - bottom_left_corner_left_holder[0]
        print("Distance between holders: ", distance_below_target)

    print('finished moving holders together')

    # ------- ROTATE TOP CONVEYOR TO SLIDE TRAY ACROSS -----------
    set_up_top_conveyor()
    additional_distance_to_push_tray_across = 140
    target = bottom_left_corner_left_holder[1] - additional_distance_to_push_tray_across
    distance_from_target = top_conveyor_leg_top_left_y - target
    # draw a horizontal line at conveyor_threshold
    cv2.line(image, (0, conveyor_threshold), (image.shape[1], conveyor_threshold), (0, 255, 0), 2)  # Green line
    # draw a horizontal line at top_conveyor_leg_top_left_y
    cv2.line(image, (0, top_conveyor_leg_top_left_y), (image.shape[1], top_conveyor_leg_top_left_y), (0, 0, 255), 2)  # Red line
    cv2.imwrite("before_move_top_conveyor.jpg", image)

    while(distance_from_target > 0):
        steps_to_take = int(pid_control(distance_from_target, Kp=(1/calibration_variables[TOP_CONVEYOR_SPEED_FORWARD])))
        if(steps_to_take == 0):
            print("No steps to take")
            break
        print("Steps to take: ", steps_to_take)
        step_top_conveyor_forward(steps_to_take)

        image = capture_image()

        # find new position of top conveyor leg
        leg_contours = find_leg_contours(image)
        top_conveyor_leg_top_left_x, top_conveyor_leg_top_left_y = find_leg_top_conveyor(leg_contours)
        distance_from_target = top_conveyor_leg_top_left_y - target

        print("Distance from top conveyor target: ", distance_from_target)

    print('finished moving top conveyor to target')

    # --------- MOVE TOP CONVEYOR LEG OUT OF THE WAY OF CONVEYORS -----------
    target_location = get_rightmost_corner(corners_right)[1] + 5
    del corners_right
    gc.collect()
    # draw a horizontal line at target
    cv2.line(image, (0, target_location), (image.shape[1], target_location), (255, 0, 0), 2)  
    cv2.imwrite("before_move_top_conveyor_leg.jpg", image)
    num_moves = 0
    
    while(top_conveyor_leg_top_left_y > target_location):
        distance_to_target = (target_location - top_conveyor_leg_top_left_y)
        print("Distance to target location: ", distance_to_target)
        steps_to_take = abs(int(distance_to_target // calibration_variables[TOP_CONVEYOR_SPEED_BACKWARD]))
        if(steps_to_take == 0):
            print("No steps to take")
            break
        print("Steps to take: ", steps_to_take)
        step_top_conveyor_backward(steps_to_take)

        image = capture_image()

        # find new position of top conveyor leg
        leg_contours = find_leg_contours(image)
        top_conveyor_leg_top_left_x, top_conveyor_leg_top_left_y = find_leg_top_conveyor(leg_contours)
        
        if(num_moves > 5): # if get stuck in loop moving up, target is probably too high
            print("STUCK IN LOOP - TARGET LIKELY WRONG")
            break
        num_moves += 1
        
    clean_up_top_conveyor()
    print("Finished moving top conveyor leg out of the way")

    # check tray has moved to other conveyor
    print("Was top plant on right ", top_right_plant_id) 
    new_top_plant_left_conveyor = get_top_qr_left_conveyor(image, conveyor_threshold)
    print("New top plant on left ", new_top_plant_left_conveyor) 
    if(new_top_plant_left_conveyor[0] == top_right_plant_id):
        print("Tray moved successfully")
    else:
        print("Error: Tray not moved successfully")

    # -------- FIND BOTTOM PLANT LEFT CONVEYOR AND TARGET LOCATION ----------
    bottom_conveyor_leg_top_right_x, bottom_conveyor_leg_top_right_y  = find_leg_bottom_conveyor(leg_contours)
    target_location_for_bottom_tray = int(bottom_conveyor_leg_top_right_x - 550) 
    
    bottom_of_bottom_holder_left_conveyor_x_coord, bottom_left_plant_id = update_bottom_left_plant_position(image, conveyor_threshold)
    distance_from_bottom_of_holder_to_target = target_location_for_bottom_tray - bottom_of_bottom_holder_left_conveyor_x_coord

    print("Moving left conveyor down close enough to slide tray across.")
    print("Distance to target location to slide across: ", distance_from_bottom_of_holder_to_target)

    # ------ USE PID CONTROL TO MOVE BOTTOM HOLDER ON LEFT CONVEYOR DOWN CLOSE ENOUGH TO SLIDE TRAY ACROSS -----------
    while(distance_from_bottom_of_holder_to_target < -50): # TODO: base target location on end of top conveyor leg for better relability
        # Visualise current (red) and target (green) location
        cv2.line(image, (target_location_for_bottom_tray, 0), (target_location_for_bottom_tray, image.shape[0]), (0, 255, 0), 2)  
        cv2.line(image, (int(bottom_of_bottom_holder_left_conveyor_x_coord), 0), (int(bottom_of_bottom_holder_left_conveyor_x_coord), image.shape[0]), (0, 0, 255), 2) 
        cv2.imwrite("before_move_left_holder_to_bottom.jpg", image)

        # move conveyor
        steps_to_take = int(pid_control(distance_from_bottom_of_holder_to_target, Kp=(1/calibration_variables[LEFT_CONVEYOR_SPEED])))
        set_up_left_conveyor()
        move_left_conveyor(steps_to_take)
        clean_up_left_conveyor()

        # capture new image
        image = capture_image()

        # find new position of top holder
        bottom_of_bottom_holder_left_conveyor_x_coord, bottom_left_plant_id = update_bottom_left_plant_position(image, conveyor_threshold)

        # find new distance left to travel
        print("target location: ", target_location_for_bottom_tray)
        print("bottom of bottom holder left conveyor: ",bottom_of_bottom_holder_left_conveyor_x_coord)
        distance_from_bottom_of_holder_to_target = target_location_for_bottom_tray - bottom_of_bottom_holder_left_conveyor_x_coord
        print("Distance to target location to slide across: ", distance_from_bottom_of_holder_to_target)

    print("Finished moving bottom holder on left conveyor close enough to slide tray across. Distance to target location now ", distance_from_bottom_of_holder_to_target)
    gc.collect() # run garbage collector to free up memory

    # --------- FIND DESIRED POSITION FOR BOTTOM RIGHT HOLDER -----------
    image = capture_image()

    # get corners of each holder
    holders = find_holders(image)
    holders_divided_into_conveyors = divide_holders_into_conveyors(conveyor_threshold, holders_from_find_holders=holders) # TODO - this is a bit sus, need to check if it work
    bottom_holder_right = bottom_holder_right_conveyor(holders_divided_into_conveyors)
    bottom_holder_left = bottom_holder_left_conveyor(holders_divided_into_conveyors)
    image_with_contours = image.copy()

    print('finding corners for right holder')
    corners_right = extract_holder_corners(image, bottom_holder_right['contour'], 8, 0.02, 10)

    gc.collect() # run garbage collector to free up memory

    print('finding corners for left contour')
    corners_left = extract_holder_corners(image, bottom_holder_left['contour'], 20, 0.04, 45)

    gc.collect() # run garbage collector to free up memory

    print('got corners - drawing')

    # Draw the corners on the image
    for corner in corners_right:
        x, y = corner.ravel()
        cv2.circle(image_with_contours, (x, y), 10, (255, 0, 0), -1)  # Green circle for right corners

    for corner in corners_left:
        x, y = corner.ravel()
        cv2.circle(image_with_contours, (x, y), 10, (0, 0, 255), -1)  # Red circle for left corners

    # Save the image with detected corners
    cv2.imwrite("image_with_corners.jpg", image_with_contours)
    print("Image with corners saved as image_with_corners.jpg")

    del image_with_contours

    bottom_left_corner_left_holder = get_bottom_left_corner(corners_left)

    top_left_corner_right_holder = get_top_left_corner(corners_right)
    del corners_right

    target_x_value = bottom_left_corner_left_holder[0]
    print("Target x value: ", target_x_value)
    print("Top left corner right holder: ", top_left_corner_right_holder[0])

    # visualize positions on image
    cv2.circle(image, (bottom_left_corner_left_holder[0], bottom_left_corner_left_holder[1]), 10, (0, 255, 255), -1)  # Yellow circle for left edge
    cv2.circle(image, (top_left_corner_right_holder[0], top_left_corner_right_holder[1]), 10, (0, 255, 255), -1)  # Yellow circle for right edge
    cv2.imwrite("image_before_move_left_holder.jpg", image)

    distance_below_target = target_x_value - top_left_corner_right_holder[0]

    print("Distance between holders: ", distance_below_target)

    # ------ USE PID CONTROL TO MOVE RIGHT HOLDER TO ALIGN WITH LEFT HOLDER -----------
    while(distance_below_target < -DISTANCE_BELOW_TARGET_HOLDER_TO_SLIDE_ACROSS or distance_below_target > 0):
        steps_to_take = int(pid_control(distance_below_target, Kp=(1/calibration_variables[RIGHT_CONVEYOR_SPEED])))
        if(steps_to_take == 0):
            print("No steps to take")
            break
        print("Steps to take: ", steps_to_take)
        
        # move conveyor
        set_up_right_conveyor()
        move_right_conveyor(steps_to_take)
        clean_up_right_conveyor()

        #take new image
        del image
        gc.collect() # run garbage collector to free up memory
        image = capture_image()

        # find new left holder position
        holders = find_holders(image)
        holders_divided_into_conveyors = divide_holders_into_conveyors(conveyor_threshold, holders_from_find_holders=holders) # TODO - this is a bit sus, need to check if it work
        bottom_holder_right = bottom_holder_right_conveyor(holders_divided_into_conveyors)

        print('finding corners for right contour')
        corners_right = extract_holder_corners(image, bottom_holder_right['contour'], 8, 0.02, 10)
        top_left_corner_right_holder = get_top_left_corner(corners_right)

        # visualize on image
        cv2.circle(image, (bottom_left_corner_left_holder[0], bottom_left_corner_left_holder[1]), 10, (0, 255, 255), -1)  # Yellow circle for left edge
        cv2.circle(image, (top_left_corner_right_holder[0], top_left_corner_right_holder[1]), 10, (0, 255, 255), -1)  # Yellow circle for right edge
        cv2.imwrite("image_before_move_right_holder.jpg", image)

        distance_below_target = target_x_value - top_left_corner_right_holder[0]
        print("Distance between holders: ", distance_below_target)

    print('finished moving holders together')

        # ------- ROTATE BOTTOM CONVEYOR TO SLIDE TRAY ACROSS -----------
    set_up_bottom_conveyor()
    additional_distance_to_push_tray_across = 130
    target = top_left_corner_right_holder[1] + additional_distance_to_push_tray_across
    distance_from_target = target - bottom_conveyor_leg_top_right_y
    # draw a horizontal line at target
    cv2.line(image, (0, target), (image.shape[1], target), (0, 255, 0), 2)  # Green line
    # draw a horizontal line at top_conveyor_leg_top_left_y
    cv2.line(image, (0, bottom_conveyor_leg_top_right_y), (image.shape[1], bottom_conveyor_leg_top_right_y), (0, 0, 255), 2)  # Red line
    cv2.imwrite("before_move_bottom_conveyor.jpg", image)

    while(distance_from_target > 0):
        steps_to_take = int(pid_control(distance_from_target, Kp=(1/calibration_variables[BOTTOM_CONVEYOR_SPEED_FORWARD])))
        if(steps_to_take == 0):
            print("No steps to take")
            break
        print("Steps to take: ", steps_to_take)
        step_bottom_conveyor_forward(steps_to_take)

        image = capture_image()

        # find new position of top conveyor leg
        leg_contours = find_leg_contours(image)
        bottom_conveyor_leg_top_right_x, bottom_conveyor_leg_top_right_y  = find_leg_bottom_conveyor(leg_contours)
        distance_from_target = target - bottom_conveyor_leg_top_right_y

        print("Distance from bottom conveyor target: ", distance_from_target)

    print('finished moving bottom conveyor to target')

    # --------- MOVE BOTTOM CONVEYOR LEG OUT OF THE WAY OF CONVEYORS -----------
    bottom_conveyor_leg_top_right_x, bottom_conveyor_leg_top_right_y  = find_leg_bottom_conveyor(leg_contours)
    target_location = get_leftmost_corner(corners_left)[1] + 10
    del corners_left
    gc.collect()
    num_moves = 0
    while(bottom_conveyor_leg_top_right_y < target_location):
        steps_to_take = abs(int((target_location - top_conveyor_leg_top_left_y) // calibration_variables[BOTTOM_CONVEYOR_SPEED_BACKWARD]))
        if(steps_to_take == 0):
            print("No steps to take")
            break
        print("Steps to take: ", steps_to_take)
        step_bottom_conveyor_backward(steps_to_take)

        image = capture_image()

        # find new position of top conveyor leg
        leg_contours = find_leg_contours(image)
        bottom_conveyor_leg_top_right_x, bottom_conveyor_leg_top_right_y  = find_leg_bottom_conveyor(leg_contours)
        if(num_moves > 5): # if get stuck in loop moving up, target is probably too high
            print("STUCK IN LOOP - TARGET LIKELY WRONG")
            break
        num_moves += 1
        
    clean_up_bottom_conveyor()
    print("Finished moving bottom conveyor leg out of the way")

    # check tray has moved to other conveyor
    print("Was bottom plant on left ", bottom_left_plant_id) 
    new_bottom_plant_right_conveyor = get_bottom_qr_right_conveyor(image, conveyor_threshold)
    print("New bottom plant on right ", new_bottom_plant_right_conveyor) 
    if(new_bottom_plant_right_conveyor[0] == bottom_left_plant_id):
        print("Tray moved successfully")
    else:
        print("Error: Tray not moved successfully")

    # --------- WHEN FINISHED, STOP THREAD SPINNING SERVO MOTOR ---------- 
    # servo_motor_code.sweeping = False
    # servo_thread.join()
    # clean_up_servo(pi) # Clean up servo motor
except KeyboardInterrupt:
        print("Caught Ctrl+C, exiting gracefully.")
        GPIO.cleanup()  # Clean up GPIO settings
        print("Cleaned up GPIO")
        gc.collect()  # Run garbage collector to free up memory
finally:
    # Clean up GPIO settings
    GPIO.cleanup()  # Clean up GPIO settings
    # os.system("sudo killall pigpiod")  # Stop pigpio daemon
    print("Cleaned up GPIO and stopped pigpio daemon")
    gc.collect()  # Run garbage collector to free up memory


# trickier version - multiple plants on each conveyor. note space plant holders evenly and with few enough plants that when a plant is at the top there's an empty holder at the bottom (and vice versa for right conveyor)
# step 1: check location of top plant on left conveyor (barcode in top left position) - note distance from top
# step 2: check location of bottom plant on right conveyor (bottom right position) - note distance from bottom
# step 3: check which has a shorter distance to the top/bottom. call the above simpler fns to move that plant to the other conveyor
# step 4: whichever side you didn't move, call the fn to move that plant across
