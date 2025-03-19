import os
import cv2
from image_analysis import find_top_and_bottom_of_conveyors, top_barcode_right_conveyor
from calibration import calibrate_vertical_conveyor_motors

# NOTE: have a record of how many plants there are i.e. how many barcodes are visible. therefore if a plant falls off will know because less barcodes visible and can send me a photo

# calibrate conveyor motors
calibrate_vertical_conveyor_motors()

# simpler version - move plant from right to left conveyor (do an equivalent version to move plant from left to right conveyor)
# step 1: check location of top plant on right conveyor (barcode in top left position) - note distance from top
image_path = "captured_image.jpg"
os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
image = cv2.imread(image_path) # read the captured image with opencv
top_barcode_right_conveyor = top_barcode_right_conveyor(image)

top_conveyor, bottom_conveyor = find_top_and_bottom_of_conveyors(image)
print("Top of conveyor: ", top_conveyor)

distance_from_top = top_conveyor - top_barcode_right_conveyor[0]
print("Distance between: ", distance_from_top)


# step 2: rotate right conveyor until plant at top
# step 3: check location of holder on left conveyor
# step 4: rotate left conveyor until holder at top (slightly below left conveyor)
# step 5: rotate servo motor to put down tray push leg
# step 6: rotate top conveyor to push tray right to left
# step 7: return top conveyor to right side

# trickier version - multiple plants on each conveyor. note space plant holders evenly and with few enough plants that when a plant is at the top there's an empty holder at the bottom (and vice versa for right conveyor)
# step 1: check location of top plant on left conveyor (barcode in top left position) - note distance from top
# step 2: check location of bottom plant on right conveyor (bottom right position) - note distance from bottom
# step 3: check which has a shorter distance to the top/bottom. call the above simpler fns to move that plant to the other conveyor
# step 4: whichever side you didn't move, call the fn to move that plant across
