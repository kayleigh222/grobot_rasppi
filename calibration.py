import json
from image_analysis import top_barcode_right_conveyor, top_barcode_left_conveyor
import os
import cv2
from vertical_conveyor_left_motor_code import move_left_conveyor_up, move_left_conveyor_down, set_up_left_conveyor, clean_up_left_conveyor
from vertical_conveyor_right_motor_code import move_right_conveyor_up, move_right_conveyor_down, set_up_right_conveyor, clean_up_right_conveyor

# File to store variables
FILE_PATH = "calibration_variables.json"

# Save variables
def save_variables(data):
    with open(FILE_PATH, "w") as file:
        json.dump(data, file)

# Load variables
def load_variables():
    try:
        with open(FILE_PATH, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return empty dict if file doesn't exist or is corrupted

def calibrate_right_conveyor_motor(num_steps_to_test=100):  # to use, put one barcode on left conveyor somewhere in the middle
  image_path = "captured_image.jpg"
  os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
  image = cv2.imread(image_path) # read the captured image with opencv
  top_barcode_right_conveyor_original = top_barcode_right_conveyor(image)

  set_up_right_conveyor()

  # move motor up
  move_right_conveyor_up(num_steps_to_test)

  # measure new position
  os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
  image = cv2.imread(image_path) # read the captured image with opencv
  top_barcode_right_conveyor_new = top_barcode_right_conveyor(image)
  # calculate num pixels moved
  pixels_moved = abs(top_barcode_right_conveyor_new[0] - top_barcode_right_conveyor_original[0])
  pixels_moved_per_step_up = pixels_moved/num_steps_to_test

  # prepare for downward test
  top_barcode_right_conveyor_original = top_barcode_right_conveyor_new

  # move motor down
  move_right_conveyor_down(num_steps_to_test)

  # measure new position
  os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
  image = cv2.imread(image_path) # read the captured image with opencv
  top_barcode_right_conveyor_new = top_barcode_right_conveyor(image)
  # calculate num pixels moved
  pixels_moved = abs(top_barcode_right_conveyor_new[0] - top_barcode_right_conveyor_original[0])
  pixels_moved_per_step_down = pixels_moved/num_steps_to_test

  # save new calibration variables
  data = {"right_conveyor_motor_pixels_per_step_up": pixels_moved_per_step_up, "right_conveyor_motor_pixels_per_step_down": pixels_moved_per_step_down}
  print(data)
  save_variables(data)  # Save

# loaded_data = load_variables()  # Load
# print(loaded_data["motor_speed"])  # 120

def calibrate_left_conveyor_motor():
