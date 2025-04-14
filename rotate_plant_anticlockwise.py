import os
import cv2
import pigpio
import numpy as np
import time
import threading
from image_analysis import divide_holders_into_conveyors, find_holders, find_left_and_right_of_conveyors, find_leg_top_conveyor, find_top_and_bottom_of_conveyors, get_top_barcode_left_conveyor, get_top_barcode_right_conveyor, top_holder_left_conveyor, top_holder_right_conveyor, get_conveyor_threshold, get_right_edge_of_holder, get_left_edge_of_holder, top_holder_with_barcode_right_conveyor, get_bottom_edge_of_holder
from calibration import TOP_CONVEYOR_SPEED_BACKWARD, TOP_CONVEYOR_SPEED_FORWARD, calibrate_top_conveyor_motor, calibrate_vertical_conveyor_motors, load_variables, LEFT_CONVEYOR_SPEED, RIGHT_CONVEYOR_SPEED
from servo_motor_code import clean_up_servo, set_up_servo, sweep_servo
import servo_motor_code
from top_conveyor_motor_code import clean_up_top_conveyor, set_up_top_conveyor, step_top_conveyor_backward, step_top_conveyor_forward
from vertical_conveyor_left_motor_code import move_left_conveyor, set_up_left_conveyor, clean_up_left_conveyor
from vertical_conveyor_right_motor_code import move_right_conveyor, set_up_right_conveyor, clean_up_right_conveyor

DISTANCE_BELOW_TARGET_HOLDER_TO_SLIDE_ACROSS = 50 # pixels - max vertical distance between holders to be able to slide across

# variables for PID control - used to move conveyor to align holders before sliding tray across
previous_error = 0
integral = 0

def pid_control(error, Kp=0.7, Ki=0.01, Kd=0.05): # error is the difference between the target value and the current value
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

# ----------- TURN ON LIGHTS BY RUNNING SERVO MOTOR IN SEPARATE THREAD TO TRIGGER MOTION SENSOR --------
os.system("sudo pigpiod")
time.sleep(1)  # Give it a second to start
pi = pigpio.pi() # Connect to pigpio daemon
set_up_servo(pi) # Set up servo motor
servo_motor_code.sweeping = True # Control flag
servo_thread = threading.Thread(target=sweep_servo, args=(pi,)) # Create thread to run servo motor
servo_thread.start()

# calibrate conveyor motors
# calibrate_vertical_conveyor_motors()
# calibrate_top_conveyor_motor() # calibrate top conveyor motor

# # ----------- TAKE INITIAL IMAGE AND LOAD CALIBRATION VARIABLES ------------------
image_path = "captured_image.jpg"
os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
image = cv2.imread(image_path) # read the captured image with opencv

calibration_variables = load_variables() 

# # ---------- FIND OUTLINES OF CONVEYOR TO GET TARGET LOCATION FOR TOP TRAY -----------
conveyor_threshold, conveyors_left, conveyors_right = get_conveyor_threshold(image) # find threshold between left and right conveyor
top_conveyor, bottom_conveyor = find_top_and_bottom_of_conveyors(image)
conveyor_height = top_conveyor - bottom_conveyor
top_conveyor_leg_top_left_x, top_conveyor_leg_top_left_y  = find_leg_top_conveyor(image)
target_location_for_top_tray = int(top_conveyor_leg_top_left_x - 150) # TODO- currently hardcoding this, probably want a better way 

# # ----------- FIND TOP HOLDER ON RIGHT CONVEYOR ------------------
# top_holder_with_barcode_on_right_conveyor = top_holder_with_barcode_right_conveyor(image, conveyor_threshold, conveyors_left, conveyors_right)
# bottom_of_top_holder_right_conveyor = get_bottom_edge_of_holder(top_holder_with_barcode_on_right_conveyor['contour'], image)
# bottom_of_top_holder_right_conveyor_x_coord = bottom_of_top_holder_right_conveyor[0][0]
# distance_from_bottom_of_holder_to_target = target_location_for_top_tray - bottom_of_top_holder_right_conveyor_x_coord

# # Draw a vertical line at the target location
# cv2.line(image, (target_location_for_top_tray, 0), (target_location_for_top_tray, image.shape[0]), (0, 255, 0), 2)  # Green line
# # Draw a vertical line at bottom of top_barcode_right_conveyor
# cv2.line(image, (int(bottom_of_top_holder_right_conveyor_x_coord), 0), (int(bottom_of_top_holder_right_conveyor_x_coord), image.shape[0]), (0, 0, 255), 2)  # Red line
# cv2.imwrite("before_move_right_holder_to_top.jpg", image)

# print("Moving right conveyor up close enough to slide tray across.")

# # ------ USE PID CONTROL TO MOVE TOP HOLDER ON RIGHT CONVEYOR UP CLOSE ENOUGH TO SLIDE TRAY ACROSS -----------
# while(distance_from_bottom_of_holder_to_target > 100): # TODO: base target location on end of top conveyor leg for better relability
#     print("Distance to target location to slide across: ", distance_from_bottom_of_holder_to_target)

#     # Draw a vertical line at the target location
#     cv2.line(image, (target_location_for_top_tray, 0), (target_location_for_top_tray, image.shape[0]), (0, 255, 0), 2)  # Green line

#     # Draw a vertical line at bottom of top_barcode_right_conveyor
#     cv2.line(image, (int(bottom_of_top_holder_right_conveyor_x_coord), 0), (int(bottom_of_top_holder_right_conveyor_x_coord), image.shape[0]), (0, 0, 255), 2)  # Red line

#     # Save the image
#     cv2.imwrite("before_move_right_holder_to_top.jpg", image)

#     print('right conveyor speed ', calibration_variables[RIGHT_CONVEYOR_SPEED])
#     print('feeding in kp ', (1/calibration_variables[RIGHT_CONVEYOR_SPEED]))

#     # move conveyor
#     steps_to_take = int(pid_control(distance_from_bottom_of_holder_to_target, Kp=(1/calibration_variables[RIGHT_CONVEYOR_SPEED])))
#     set_up_right_conveyor()
#     move_right_conveyor(steps_to_take)
#     clean_up_right_conveyor()

#     # capture new image
#     os.system(f"rpicam-still --output {image_path} --nopreview") 
#     image = cv2.imread(image_path)

#     # find new position of top holder
#     top_holder_with_barcode_on_right_conveyor = top_holder_with_barcode_right_conveyor(image, conveyor_threshold, conveyors_left, conveyors_right)
#     bottom_of_top_holder_right_conveyor = get_bottom_edge_of_holder(top_holder_with_barcode_on_right_conveyor['contour'], image)
#     bottom_of_top_holder_right_conveyor_x_coord = bottom_of_top_holder_right_conveyor[0][0]

#     # find new distance left to travel
#     distance_from_bottom_of_holder_to_target = target_location_for_top_tray - bottom_of_top_holder_right_conveyor_x_coord

# print("Finished moving top holder on right conveyor up close enough to slide tray across.")

# --------- FIND DESIRED POSITION FOR LEFT HOLDER -----------

# TODO - fix references to top holders so find holders and holders divided into conveyors first
#take new image
os.system(f"rpicam-still --output {image_path} --nopreview") 
image = cv2.imread(image_path) 

print('detecting corners')

# get bounding edges (next to each other) of each holder
holders = find_holders(image)
holders_divided_into_conveyors = divide_holders_into_conveyors(image, conveyor_threshold, holders_from_find_holders=holders) # TODO - this is a bit sus, need to check if it work
top_holder_right = top_holder_right_conveyor(holders_divided_into_conveyors) # TODO - this detects all holders twice, make more efficient
top_holder_left = top_holder_left_conveyor(holders_divided_into_conveyors)
top_holder_right_contour = top_holder_right['contour']
top_holder_left_contour = top_holder_left['contour']
# simplify contours
top_holder_right_contour = cv2.approxPolyDP(top_holder_right_contour, 0.02 * cv2.arcLength(top_holder_right_contour, True), True)
top_holder_left_contour = cv2.approxPolyDP(top_holder_left_contour, 0.01 * cv2.arcLength(top_holder_left_contour, True), True)
print('got top holder contours')
image_with_right_contour = np.zeros_like(image)
image_with_left_contour = np.zeros_like(image)
cv2.drawContours(image_with_right_contour, [top_holder_right_contour], -1, (255, 255, 255), 1)
cv2.drawContours(image_with_left_contour, [top_holder_left_contour], -1, (255, 255, 255), 1)
right_gray = cv2.cvtColor(image_with_right_contour, cv2.COLOR_BGR2GRAY)
left_gray = cv2.cvtColor(image_with_left_contour, cv2.COLOR_BGR2GRAY)
print('converted contours to gray')
corners_right = cv2.goodFeaturesToTrack(right_gray, maxCorners=16, qualityLevel=0.01, minDistance=10)
corners_left = cv2.goodFeaturesToTrack(left_gray, maxCorners=4, qualityLevel=0.01, minDistance=10)
print('got corners')
# Convert corners to integer values
corners_right = np.intp(corners_right)
corners_left = np.intp(corners_left)
print('converted corners to int')
# Draw the corners on the image
image_with_contours = image.copy()
for corner in corners_right:
    x, y = corner.ravel()
    cv2.circle(image_with_contours, (x, y), 10, (255, 0, 0), -1)  # Green circle for right corners

for corner in corners_left:
    x, y = corner.ravel()
    cv2.circle(image_with_contours, (x, y), 10, (0, 0, 255), -1)  # Red circle for left corners

# Save the image with detected corners
cv2.imwrite("image_with_corners.jpg", image_with_contours)
print("Image with corners saved as image_with_corners.jpg")


simplified_right_contour = cv2.approxPolyDP(top_holder_right_contour, 0.01 * cv2.arcLength(top_holder_right_contour, True), True)
simplified_left_contour = cv2.approxPolyDP(top_holder_left_contour, 0.01 * cv2.arcLength(top_holder_left_contour, True), True)


# left_edge_right = get_left_edge_of_holder(top_holder_right['contour'], image)
# right_edge_left = get_right_edge_of_holder(top_holder_left['contour'], image)

# target_x_value = left_edge_right[0][0]

# # visualize positions on image
# cv2.line(image, (target_x_value, 0), (target_x_value, image.shape[0]), (0, 255, 0), 2)  # Green line
# cv2.line(image, right_edge_left[0], right_edge_left[1], (0, 0, 255), 3)  # Red line
# cv2.circle(image, right_edge_left[0], 5, (0, 255, 0), -1) # draw a dot to mark bottom of left holder
# cv2.imwrite("image_before_move_left_holder.jpg", image)

# distance_below_target = target_x_value - right_edge_left[0][0]

# print('Right edge of left holder: ', right_edge_left)
# print("Distance between holders: ", distance_below_target)

# # ------ USE PID CONTROL TO MOVE LEFT HOLDER TO ALIGN WITH RIGHT HOLDER -----------
# while(distance_below_target > DISTANCE_BELOW_TARGET_HOLDER_TO_SLIDE_ACROSS or distance_below_target < 0):
#     steps_to_take = int(pid_control(distance_below_target, Kp=(1/calibration_variables[LEFT_CONVEYOR_SPEED])))
#     if(steps_to_take == 0):
#         print("No steps to take")
#         break
#     print("Steps to take: ", steps_to_take)

#     # move conveyor
#     set_up_left_conveyor()
#     move_left_conveyor(steps_to_take)
#     clean_up_left_conveyor()

#     #take new image
#     os.system(f"rpicam-still --output {image_path} --nopreview") 
#     image = cv2.imread(image_path)

#     # find new left holder position
#     top_holder_left = top_holder_left_conveyor(image, conveyor_threshold, conveyors_left, conveyors_right)
#     right_edge_left = get_right_edge_of_holder(top_holder_left['contour'], image)

#     # visualize on image
#     cv2.line(image, (target_x_value, 0), (target_x_value, image.shape[0]), (0, 255, 0), 2)  # Green line
#     cv2.line(image, right_edge_left[0], right_edge_left[1], (0, 0, 255), 3)  # Red line
#     cv2.circle(image, right_edge_left[0], 5, (0, 255, 0), -1) # draw a circle to mark bottom of left holder

#     cv2.imwrite("image_before_move_left_holder.jpg", image)

#     distance_below_target = target_x_value - right_edge_left[0][0]
#     print("Distance between holders: ", distance_below_target)

# print('finished moving holders together')

# # ------- ROTATE TOP CONVEYOR TO SLIDE TRAY ACROSS -----------
# set_up_top_conveyor()
# additional_distance_to_push_tray_across_threshold = 100 # (conveyors_right - conveyors_left) // 20 # move an extra quarter of a conveyor across threshold
# distance_from_target = top_conveyor_leg_top_left_y - (conveyor_threshold - additional_distance_to_push_tray_across_threshold)
# # draw a horizontal line at conveyor_threshold
# cv2.line(image, (0, conveyor_threshold), (image.shape[1], conveyor_threshold), (0, 255, 0), 2)  # Green line
# # draw a horizontal line at top_conveyor_leg_top_left_y
# cv2.line(image, (0, top_conveyor_leg_top_left_y), (image.shape[1], top_conveyor_leg_top_left_y), (0, 0, 255), 2)  # Red line
# cv2.imwrite("before_move_top_conveyor.jpg", image)

# while(distance_from_target > 0):
#     steps_to_take = int(pid_control(distance_from_target, Kp=(1/calibration_variables[TOP_CONVEYOR_SPEED_FORWARD])))
#     if(steps_to_take == 0):
#         print("No steps to take")
#         break
#     print("Steps to take: ", steps_to_take)
#     step_top_conveyor_forward(steps_to_take)

#     #take new image
#     os.system(f"rpicam-still --output {image_path} --nopreview") 
#     image = cv2.imread(image_path) 

#     # find new position of top conveyor leg
#     top_conveyor_leg_top_left_x, top_conveyor_leg_top_left_y = find_leg_top_conveyor(image)
#     distance_from_target = top_conveyor_leg_top_left_y - (conveyor_threshold - additional_distance_to_push_tray_across_threshold)

#     print("Distance from top conveyor target: ", distance_from_target)

# print('finished moving top conveyor to target')

# # --------- MOVE TOP CONVEYOR LEG OUT OF THE WAY OF CONVEYORS ----------- # TODO: do this with PID control
# top_conveyor_leg_top_left_x, top_conveyor_leg_top_left_y = find_leg_top_conveyor(image)
# target_location = conveyors_right # + additional_distance_to_push_tray_across_threshold # TODO - this is sus?
# while(top_conveyor_leg_top_left_y < target_location):
#     steps_to_take = abs(int((target_location - top_conveyor_leg_top_left_y) // calibration_variables[TOP_CONVEYOR_SPEED_BACKWARD]))
#     if(steps_to_take == 0):
#         print("No steps to take")
#         break
#     print("Steps to take: ", steps_to_take)
#     step_top_conveyor_backward(steps_to_take)

#     #take new image
#     os.system(f"rpicam-still --output {image_path} --nopreview") 
#     image = cv2.imread(image_path) 

#     # find new position of top conveyor leg
#     top_conveyor_leg_top_left_x, top_conveyor_leg_top_left_y = find_leg_top_conveyor(image)
    
# clean_up_top_conveyor()
# print("Finished moving top conveyor leg out of the way")

# # # check tray has moved to other conveyor
# # print("Was top barcode on right ", top_holder_with_barcode_on_right_conveyor) # TODO: get data from this e.g. plant 4
# # os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
# # image = cv2.imread(image_path) # read the captured image with opencv
# # new_top_barcode_left_conveyor = get_top_barcode_left_conveyor(image, conveyor_threshold, conveyors_left, conveyors_right) # TODO: get data from this e.g. plant 4
# # print("New top barcode on left ", new_top_barcode_left_conveyor) # TODO: get data from this e.g. plant 4
# # if(new_top_barcode_left_conveyor[0] == top_holder_with_barcode_on_right_conveyor[0]): # TODO - change indexing here so actually get right data?
# #     print("Tray moved successfully")
# # else:
# #     print("Error: Tray not moved successfully")



# --------- WHEN FINISHED, STOP THREAD SPINNING SERVO MOTOR ---------- 
servo_motor_code.sweeping = False
servo_thread.join()
clean_up_servo(pi) # Clean up servo motor
# trickier version - multiple plants on each conveyor. note space plant holders evenly and with few enough plants that when a plant is at the top there's an empty holder at the bottom (and vice versa for right conveyor)
# step 1: check location of top plant on left conveyor (barcode in top left position) - note distance from top
# step 2: check location of bottom plant on right conveyor (bottom right position) - note distance from bottom
# step 3: check which has a shorter distance to the top/bottom. call the above simpler fns to move that plant to the other conveyor
# step 4: whichever side you didn't move, call the fn to move that plant across
