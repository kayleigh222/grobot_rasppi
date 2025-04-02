import os
import cv2
from image_analysis import find_left_and_right_of_conveyors, find_leg_top_conveyor, find_top_and_bottom_of_conveyors, get_top_barcode_left_conveyor, get_top_barcode_right_conveyor, top_holder_left_conveyor, top_holder_right_conveyor, get_conveyor_threshold, get_bottom_edge_of_holder, get_top_edge_of_holder
from calibration import TOP_CONVEYOR_SPEED_BACKWARD, TOP_CONVEYOR_SPEED_FORWARD, calibrate_top_conveyor_motor, calibrate_vertical_conveyor_motors, load_variables, LEFT_CONVEYOR_SPEED, RIGHT_CONVEYOR_SPEED
from top_conveyor_motor_code import clean_up_top_conveyor, set_up_top_conveyor, step_top_conveyor_backward, step_top_conveyor_forward
from vertical_conveyor_left_motor_code import move_left_conveyor, set_up_left_conveyor, clean_up_left_conveyor
from vertical_conveyor_right_motor_code import move_right_conveyor, set_up_right_conveyor, clean_up_right_conveyor

DISTANCE_BETWEEN_HOLDERS_TO_SLIDE_ACROSS = 15 # pixels - max vertical distance between holders to be able to slide across
ADDITIONAL_DISTANCE_TO_PUSH_TRAY_ACROSS_THRESHOLD = 20 # pixels - additional distance to push tray across the threshold to ensure it is properly mounted on the other conveyor

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

    # Calculate how much to move the conveyor
    adjustment = Kp * error + Ki * integral + Kd * derivative
    print("Adjustment: ", adjustment)
    return adjustment

# NOTE: have a record of how many plants there are i.e. how many barcodes are visible. therefore if a plant falls off will know because less barcodes visible and can send me a photo
# calibrate conveyor motors
# calibrate_vertical_conveyor_motors()
# calibrate_top_conveyor_motor() # calibrate top conveyor motor

# step 1: check location of top plant on right conveyor (barcode in top left position) - note distance from top
image_path = "captured_image.jpg"
os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
image = cv2.imread(image_path) # read the captured image with opencv
conveyor_threshold = get_conveyor_threshold(image) # find threshold between left and right conveyor

top_barcode_right_conveyor = get_top_barcode_right_conveyor(image, conveyor_threshold)

top_conveyor, bottom_conveyor = find_top_and_bottom_of_conveyors(image)
print("Top of conveyor: ", top_conveyor)

distance_from_top = top_conveyor - top_barcode_right_conveyor[1][0]
print("Distance between: ", distance_from_top)

# Draw a vertical line at the top conveyor
cv2.line(image, (top_conveyor, 0), (top_conveyor, image.shape[0]), (0, 255, 0), 2)  # Green line

# Draw a vertical line at top_barcode_right_conveyor
cv2.line(image, (int(top_barcode_right_conveyor[1][0]), 0), (int(top_barcode_right_conveyor[1][0]), image.shape[0]), (0, 0, 255), 2)  # Red line

# Show the image
cv2.imwrite("before_move_right_holder_to_top.png", image)

# step 2: rotate right conveyor until plant at top
calibration_variables = load_variables() 

steps_to_top = int(distance_from_top // calibration_variables[RIGHT_CONVEYOR_SPEED])
set_up_right_conveyor()
move_right_conveyor(steps_to_top)
clean_up_right_conveyor()


# step 3: check location of holder on left conveyor 

#take new image
os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
image = cv2.imread(image_path) # read the captured image with opencv

top_holder_right = top_holder_right_conveyor(image, conveyor_threshold)
top_holder_left = top_holder_left_conveyor(image, conveyor_threshold)
top_edge_right = get_top_edge_of_holder(top_holder_right['contour'], image)
bottom_edge_left = get_bottom_edge_of_holder(top_holder_left['contour'], image)

target_x_value = top_edge_right[0][0]

#draw the edges on image
cv2.line(image, (target_x_value, 0), (target_x_value, image.shape[0]), (0, 255, 0), 2)  # Green line
cv2.line(image, bottom_edge_left[0], bottom_edge_left[1], (0, 0, 255), 3)  # Red line

# draw a dot to mark bottom of left holder
cv2.circle(image, bottom_edge_left[0], 5, (0, 255, 0), -1)

distance_between_holders = target_x_value - bottom_edge_left[0][0]

cv2.imwrite("image_with_holder_edges.jpg", image)
print("Distance between holders: ", distance_between_holders)

while(abs(distance_between_holders) > DISTANCE_BETWEEN_HOLDERS_TO_SLIDE_ACROSS):
    steps_to_take = int(pid_control(distance_between_holders))
    if(steps_to_take == 0):
        print("No steps to take")
        break
    print("Steps to take: ", steps_to_take)
    set_up_left_conveyor()
    move_left_conveyor(steps_to_take)
    clean_up_left_conveyor()

    #take new image
    os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
    image = cv2.imread(image_path) # read the captured image with opencv

    top_holder_left = top_holder_left_conveyor(image, conveyor_threshold)
    bottom_edge_left = get_bottom_edge_of_holder(top_holder_left['contour'], image)

    #draw the edges on image
    cv2.line(image, (target_x_value, 0), (target_x_value, image.shape[0]), (0, 255, 0), 2)  # Green line
    cv2.line(image, bottom_edge_left[0], bottom_edge_left[1], (0, 0, 255), 3)  # Red line

    #draw a circle to mark bottom of left holder
    cv2.circle(image, bottom_edge_left[0], 5, (0, 255, 0), -1)

    distance_between_holders = target_x_value - bottom_edge_left[0][0]
    cv2.imwrite("image_with_holder_edges.jpg", image)
    print("Distance between holders: ", distance_between_holders)

print('finished moving holders together')

# step 5: rotate top conveyor to push tray right to left
set_up_top_conveyor()
top_conveyor_leg_x, top_conveyor_leg_y = find_leg_top_conveyor(image)
distance_from_target = top_conveyor_leg_y - (conveyor_threshold - ADDITIONAL_DISTANCE_TO_PUSH_TRAY_ACROSS_THRESHOLD)

while(abs(distance_from_target) > DISTANCE_BETWEEN_HOLDERS_TO_SLIDE_ACROSS):
    steps_to_take = int(pid_control(distance_from_target, Kp=(1/calibration_variables[TOP_CONVEYOR_SPEED_FORWARD])))
    if(steps_to_take == 0):
        print("No steps to take")
        break
    print("Steps to take: ", steps_to_take)
    step_top_conveyor_forward(steps_to_take)

    #take new image
    os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
    image = cv2.imread(image_path) # read the captured image with opencv

    top_conveyor_leg_x, top_conveyor_leg_y = find_leg_top_conveyor(image)

    distance_from_target = top_conveyor_leg_y - (conveyor_threshold - ADDITIONAL_DISTANCE_TO_PUSH_TRAY_ACROSS_THRESHOLD)

    print("Distance between from top conveyor target: ", distance_from_target)

print('finished moving top conveyor to target')

# step 7: return top conveyor to right side
conveyors_left, conveyors_right = find_left_and_right_of_conveyors(image)
top_conveyor_leg_x, top_conveyor_leg_y = find_leg_top_conveyor(image)
target_location = conveyors_right + ADDITIONAL_DISTANCE_TO_PUSH_TRAY_ACROSS_THRESHOLD
while(top_conveyor_leg_y < target_location):
    steps_to_take = int((target_location - top_conveyor_leg_y) // calibration_variables[TOP_CONVEYOR_SPEED_BACKWARD])
    if(steps_to_take == 0):
        print("No steps to take")
        break
    print("Steps to take: ", steps_to_take)
    step_top_conveyor_backward(steps_to_take)
    
clean_up_top_conveyor()

# check tray has moved to other conveyor
print("Was top barcode on right ", top_barcode_right_conveyor) # TODO: get data from this e.g. plant 4
os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
image = cv2.imread(image_path) # read the captured image with opencv
new_top_barcode_left_conveyor = get_top_barcode_left_conveyor(image, conveyor_threshold) # TODO: get data from this e.g. plant 4
print("New top barcode on left ", new_top_barcode_left_conveyor) # TODO: get data from this e.g. plant 4
if(new_top_barcode_left_conveyor[0] == top_barcode_right_conveyor[0]):
    print("Tray moved successfully")
else:
    print("Error: Tray not moved successfully")

# trickier version - multiple plants on each conveyor. note space plant holders evenly and with few enough plants that when a plant is at the top there's an empty holder at the bottom (and vice versa for right conveyor)
# step 1: check location of top plant on left conveyor (barcode in top left position) - note distance from top
# step 2: check location of bottom plant on right conveyor (bottom right position) - note distance from bottom
# step 3: check which has a shorter distance to the top/bottom. call the above simpler fns to move that plant to the other conveyor
# step 4: whichever side you didn't move, call the fn to move that plant across
