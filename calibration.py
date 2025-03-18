import json
from image_analysis import barcodes_divided_into_conveyors
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

def calibrate_right_conveyor_motor():  # to use, put one barcode on left conveyor somewhere in the middle
  image_path = "captured_image.jpg"
  os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
  image = cv2.imread(image_path) # read the captured image with opencv
  left_conveyor_barcodes, right_conveyor_barcodes = barcodes_divided_into_conveyors(image)
  if right_conveyor_barcodes:
    # Find the barcode with the maximum x-coordinate in the right conveyor
    top_barcode_right_conveyor = max(right_conveyor_barcodes, key=lambda point: point[0])
  else:
    # Handle the case where there are no barcodes in the right conveyor
    top_barcode_right_conveyor = None  # or some default value/message
  print("Top barcode right conveyor:", top_barcode_right_conveyor)
  
  
  data = {"right_conveyor_motor_pixels_per_step_up": 120, "right_conveyor_motor_pixels_per_step_down": 120}
  save_variables(data)  # Save

# loaded_data = load_variables()  # Load
# print(loaded_data["motor_speed"])  # 120

def calibrate_left_conveyor_motor():
