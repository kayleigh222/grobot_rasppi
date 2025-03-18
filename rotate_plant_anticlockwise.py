from barcode_scan import find_barcode_locations

# NOTE: have a record of how many plants there are i.e. how many barcodes are visible. therefore if a plant falls off will know because less barcodes visible and can send me a photo

# simpler version - move plant from left to right conveyor (do an equivalent version to move plant from right to left conveyor)
# step 1: check location of top plant on left conveyor (barcode in top left position) - note distance from top
image_path = "captured_image.jpg"
os.system(f"rpicam-still --output {image_path} --nopreview") # capture image without displaying preview
barcode_centres = find_barcode_locations(image_path)
print("Barcode centers:", barcode_centres)
# step 2: rotate left conveyor until plant at top
# step 3: check location of holder on right conveyor
# step 4: rotate right conveyor until holder at top (slightly below left conveyor)
# step 5: rotate servo motor to put down tray push leg
# step 6: rotate top conveyor to push tray left to right
# step 7: return top conveyor to left side

# trickier version - multiple plants on each conveyor. note space plant holders evenly and with few enough plants that when a plant is at the top there's an empty holder at the bottom (and vice versa for right conveyor)
# step 1: check location of top plant on left conveyor (barcode in top left position) - note distance from top
# step 2: check location of bottom plant on right conveyor (bottom right position) - note distance from bottom
# step 3: check which has a shorter distance to the top/bottom. call the above simpler fns to move that plant to the other conveyor
# step 4: whichever side you didn't move, call the fn to move that plant across
