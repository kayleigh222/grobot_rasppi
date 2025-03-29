import json
from image_analysis import top_barcode_right_conveyor, top_barcode_left_conveyor
import os
import cv2
from vertical_conveyor_left_motor_code import move_left_conveyor_up, move_left_conveyor_down, set_up_left_conveyor, clean_up_left_conveyor
from vertical_conveyor_right_motor_code import move_right_conveyor_up, move_right_conveyor_down, set_up_right_conveyor, clean_up_right_conveyor

# File to store variables
FILE_PATH = "calibration_variables.json"
RIGHT_CONVEYOR_SPEED = "right_conveyor_motor_pixels_per_step"
LEFT_CONVEYOR_SPEED = "left_conveyor_motor_pixels_per_step"

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

def calibrate_vertical_conveyor_motors(conveyor_threshold, num_steps_to_test=400):  # to use, put one barcode on left conveyor and one on right conveyor somewhere in the middle
    calibrate_right_conveyor_motor(conveyor_threshold, num_steps_to_test)
    calibrate_left_conveyor_motor(conveyor_threshold, num_steps_to_test)

def calibrate_right_conveyor_motor(conveyor_threshold, num_steps_to_test=400):  # to use, put one barcode on left conveyor somewhere in the middle
  # measure initial position
  image_path = "captured_image.jpg"
  os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
  image = cv2.imread(image_path) # read the captured image with opencv
  top_barcode_right_conveyor_original = top_barcode_right_conveyor(image, conveyor_threshold)

  # move motor
  set_up_right_conveyor()
  move_right_conveyor_up(num_steps_to_test)
  clean_up_right_conveyor()

  # measure new position
  os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
  image = cv2.imread(image_path) # read the captured image with opencv
  top_barcode_right_conveyor_new = top_barcode_right_conveyor(image, conveyor_threshold)
  pixels_moved = abs(top_barcode_right_conveyor_new[0] - top_barcode_right_conveyor_original[0])
  pixels_moved_per_step = pixels_moved/num_steps_to_test

  # save new calibration variables
  data = {RIGHT_CONVEYOR_SPEED: pixels_moved_per_step}
  print(data)
  save_variables(data)  # Save

def calibrate_left_conveyor_motor(conveyor_threshold, num_steps_to_test=400):  # to use, put one barcode on left conveyor somewhere in the middle
    
    # measure initial position
    image_path = "captured_image.jpg"
    os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
    image = cv2.imread(image_path) # read the captured image with opencv
    top_barcode_left_conveyor_original = top_barcode_left_conveyor(image, conveyor_threshold)

    # move motor
    set_up_left_conveyor()
    move_left_conveyor_up(num_steps_to_test)
    clean_up_left_conveyor()

    # measure new position
    os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
    image = cv2.imread(image_path) #
    top_barcode_left_conveyor_new = top_barcode_left_conveyor(image)
    # calculate num pixels moved
    pixels_moved = abs(top_barcode_left_conveyor_new[0] - top_barcode_left_conveyor_original[0])
    pixels_moved_per_step = pixels_moved/num_steps_to_test

    # save new calibration variables
    data = {"left_conveyor_motor_pixels_per_step": pixels_moved_per_step}
    print(data)
    save_variables(data)  # Save
