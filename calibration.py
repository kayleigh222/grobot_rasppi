import json
from bottom_conveyor_motor_code import set_up_bottom_conveyor, step_bottom_conveyor_backward, step_bottom_conveyor_forward
from image_analysis import find_leg_bottom_conveyor, find_leg_contours, find_leg_top_conveyor, get_conveyor_threshold, get_top_qr_right_conveyor, get_top_qr_left_conveyor
import os
import cv2
import math
from top_conveyor_motor_code import set_up_top_conveyor, step_top_conveyor_backward, step_top_conveyor_forward
from vertical_conveyor_left_motor_code import move_left_conveyor, set_up_left_conveyor, clean_up_left_conveyor
from vertical_conveyor_right_motor_code import move_right_conveyor, set_up_right_conveyor, clean_up_right_conveyor

# File to store variables
FILE_PATH = "calibration_variables.json"
RIGHT_CONVEYOR_SPEED = "right_conveyor_motor_pixels_per_step"
LEFT_CONVEYOR_SPEED = "left_conveyor_motor_pixels_per_step"
TOP_CONVEYOR_SPEED_FORWARD = "top_conveyor_motor_pixels_per_step_forward"
TOP_CONVEYOR_SPEED_BACKWARD = "top_conveyor_motor_pixels_per_step_backward"
BOTTOM_CONVEYOR_SPEED_FORWARD = "bottom_conveyor_motor_pixels_per_step_forward"
BOTTOM_CONVEYOR_SPEED_BACKWARD = "bottom_conveyor_motor_pixels_per_step_backward"

def round_down_2dp(num):
    return math.floor(num * 100) / 100

# Save variables
def save_variables(new_data):
    # Load existing data from file (if exists)
    data = load_variables()

    # Update the existing data with the new data
    data.update(new_data)

    # Save the updated data back to the JSON file
    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)

# Load variables
def load_variables():
    try:
        with open(FILE_PATH, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return empty dict if file doesn't exist or is corrupted

def calibrate_bottom_conveyor_motor(num_steps_to_test=800):
    print("Calibrating bottom conveyor motor...")
    set_up_bottom_conveyor()  # Set up the top conveyor motor
    # measure initial position
    image_path = "captured_image.jpg"
    os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
    image = cv2.imread(image_path) # read the captured image with opencv
    leg_contours = find_leg_contours(image)
    x_original, y_original = find_leg_bottom_conveyor(leg_contours) # find the bottom leg

    # move motor
    set_up_bottom_conveyor()
    step_bottom_conveyor_forward(num_steps_to_test)

    # measure new position
    os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
    image = cv2.imread(image_path) # read the captured image with opencv
    leg_contours = find_leg_contours(image)
    x_new, y_new = find_leg_bottom_conveyor(leg_contours) # find the top leg
    pixels_moved_forward = abs(y_new - y_original)
    pixels_moved_per_step_forward = pixels_moved_forward/num_steps_to_test
    x_original, y_original = x_new, y_new # update original position

    # move motor back
    step_bottom_conveyor_backward(num_steps_to_test)  # Move back to original position
    os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
    image = cv2.imread(image_path) # read the captured image with opencv
    leg_contours = find_leg_contours(image)
    x_new, y_new = find_leg_bottom_conveyor(leg_contours) # find the top leg
    pixels_moved_backward = abs(y_new - y_original)
    pixels_moved_per_step_backward = pixels_moved_backward/num_steps_to_test

    # save new calibration variables
    data = {BOTTOM_CONVEYOR_SPEED_FORWARD: round_down_2dp(pixels_moved_per_step_forward),
            BOTTOM_CONVEYOR_SPEED_BACKWARD: round_down_2dp(pixels_moved_per_step_backward)}  # Assuming same speed for both directions
    print(data)
    save_variables(data)  # Save

def calibrate_top_conveyor_motor(num_steps_to_test=800):
    print("Calibrating top conveyor motor...")
    set_up_top_conveyor()  # Set up the top conveyor motor
    # measure initial position
    image_path = "captured_image.jpg"
    os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
    image = cv2.imread(image_path) # read the captured image with opencv
    leg_contours = find_leg_contours(image)
    x_original, y_original = find_leg_top_conveyor(leg_contours) # find the top leg

    # move motor
    set_up_top_conveyor()
    step_top_conveyor_forward(num_steps_to_test)

    # measure new position
    os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
    image = cv2.imread(image_path) # read the captured image with opencv
    leg_contours = find_leg_contours(image)
    x_new, y_new = find_leg_top_conveyor(leg_contours) # find the top leg
    pixels_moved_forward = abs(y_new - y_original)
    pixels_moved_per_step_forward = pixels_moved_forward/num_steps_to_test
    x_original, y_original = x_new, y_new # update original position

    # move motor back
    step_top_conveyor_backward(num_steps_to_test)  # Move back to original position
    os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
    image = cv2.imread(image_path) # read the captured image with opencv
    leg_contours = find_leg_contours(image)
    x_new, y_new = find_leg_top_conveyor(leg_contours) # find the top leg
    pixels_moved_backward = abs(y_new - y_original)
    pixels_moved_per_step_backward = pixels_moved_backward/num_steps_to_test

    # save new calibration variables
    data = {TOP_CONVEYOR_SPEED_FORWARD: round_down_2dp(pixels_moved_per_step_forward),
            TOP_CONVEYOR_SPEED_BACKWARD: round_down_2dp(pixels_moved_per_step_backward)}  # Assuming same speed for both directions
    print(data)
    save_variables(data)  # Save

def calibrate_vertical_conveyor_motors(num_steps_to_test=600):  # to use, put one barcode on left conveyor and one on right conveyor somewhere in the middle
    print("Calibrating vertical conveyor motors...")
    calibrate_right_conveyor_motor(num_steps_to_test)
    calibrate_left_conveyor_motor(num_steps_to_test)

def calibrate_right_conveyor_motor(num_steps_to_test=600):  # to use, put one barcode on right conveyor somewhere in the middle
  # measure initial position
  image_path = "captured_image.jpg"
  os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
  image = cv2.imread(image_path) # read the captured image with opencv
  conveyor_threshold = get_conveyor_threshold(image)[0] # find threshold between left and right conveyor
  top_barcode_right_conveyor_original = get_top_qr_right_conveyor(image, conveyor_threshold)

  print("Original position: ", top_barcode_right_conveyor_original)

  # move motor
  set_up_right_conveyor()
  move_right_conveyor(num_steps_to_test)
  clean_up_right_conveyor()

  # measure new position
  os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
  image = cv2.imread(image_path) # read the captured image with opencv
  top_barcode_right_conveyor_new = get_top_qr_right_conveyor(image, conveyor_threshold)
  pixels_moved = abs(top_barcode_right_conveyor_new[1][0] - top_barcode_right_conveyor_original[1][0])
  pixels_moved_per_step = pixels_moved/num_steps_to_test

  # save new calibration variables
  data = {RIGHT_CONVEYOR_SPEED: round_down_2dp(pixels_moved_per_step)}
  print(data)
  save_variables(data)  # Save

def calibrate_left_conveyor_motor(num_steps_to_test=600):  # to use, put one barcode on left conveyor somewhere in the middle
    
    # measure initial position
    image_path = "captured_image.jpg"
    os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
    image = cv2.imread(image_path) # read the captured image with opencv
    conveyor_threshold = get_conveyor_threshold(image)[0] # find threshold between left and right conveyor
    top_barcode_left_conveyor_original = get_top_qr_left_conveyor(image, conveyor_threshold)

    # move motor
    set_up_left_conveyor()
    move_left_conveyor(num_steps_to_test)
    clean_up_left_conveyor()

    # measure new position
    os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
    image = cv2.imread(image_path) #
    top_barcode_left_conveyor_new = get_top_qr_left_conveyor(image, conveyor_threshold)
    # calculate num pixels moved
    pixels_moved = abs(top_barcode_left_conveyor_new[1][0] - top_barcode_left_conveyor_original[1][0])
    pixels_moved_per_step = pixels_moved/num_steps_to_test

    # save new calibration variables
    data = {"left_conveyor_motor_pixels_per_step": round_down_2dp(pixels_moved_per_step)}
    print(data)
    save_variables(data)  # Save

if __name__ == "__main__":
    print("Running motor calibration...")
    calibrate_vertical_conveyor_motors()
    calibrate_bottom_conveyor_motor()
    calibrate_top_conveyor_motor()
    print("Calibration complete.")