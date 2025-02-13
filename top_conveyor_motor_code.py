import RPi.GPIO as GPIO
import time

# Define GPIO pins for ULN2003 driver
IN1 = 26
IN2 = 19
IN3 = 13
IN4 = 6

# Set GPIO mode and configure pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Define constants
DEG_PER_STEP = 1.8
STEPS_PER_REVOLUTION = int(360 / DEG_PER_STEP)

# Define sequence for 28BYJ-48 stepper motor (8-step sequence for smoother movement)
seq = [
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1]
]

# Function to move the stepper motor one step
def step(delay, step_sequence):
    """Activates motor coils for a single step."""
    GPIO.output(IN1, step_sequence[0])
    GPIO.output(IN2, step_sequence[1])
    GPIO.output(IN3, step_sequence[2])
    GPIO.output(IN4, step_sequence[3])
    time.sleep(delay)

# Function to move the stepper motor forward
def step_forward(delay, steps):
    """Moves the motor forward by a given number of steps."""
    for _ in range(steps):
        for step_seq in seq:  # Iterate through the sequence
            step(delay, step_seq)

# Function to move the stepper motor backward
def step_backward(delay, steps):
    """Moves the motor backward by a given number of steps."""
    for _ in range(steps):
        for step_seq in reversed(seq):  # Iterate in reverse
            step(delay, step_seq)

try:
    delay = 0.001  # Adjust speed (lower = faster)
    
    while True:
        # Rotate one full revolution forward (clockwise)
        print("Rotating forward...")
        step_forward(delay, 7*STEPS_PER_REVOLUTION)
        
        # Pause for 2 seconds
        time.sleep(2)

        # Rotate one full revolution backward (anticlockwise)
        print("Rotating backward...")
        step_backward(delay, 7*STEPS_PER_REVOLUTION)

        # Pause for 2 seconds
        time.sleep(2)

except KeyboardInterrupt:
    print("\nExiting the script.")

finally:
    GPIO.cleanup()  # Clean up GPIO settings


# #!/usr/bin/python3
# import RPi.GPIO as GPIO
# import time

# in1 = 26
# in2 = 19
# in3 = 13
# in4 = 6

# # careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
# step_sleep = 0.002

# step_count = 4096 # 5.625*(1/64) per step, 4096 steps is 360°

# direction = False # True for clockwise, False for counter-clockwise

# # defining stepper motor sequence (found in documentation http://www.4tronix.co.uk/arduino/Stepper-Motors.php)
# step_sequence = [[1,0,0,1],
#                  [1,0,0,0],
#                  [1,1,0,0],
#                  [0,1,0,0],
#                  [0,1,1,0],
#                  [0,0,1,0],
#                  [0,0,1,1],
#                  [0,0,0,1]]

# # setting up
# GPIO.setmode( GPIO.BCM )
# GPIO.setup( in1, GPIO.OUT )
# GPIO.setup( in2, GPIO.OUT )
# GPIO.setup( in3, GPIO.OUT )
# GPIO.setup( in4, GPIO.OUT )

# # initializing
# GPIO.output( in1, GPIO.LOW )
# GPIO.output( in2, GPIO.LOW )
# GPIO.output( in3, GPIO.LOW )
# GPIO.output( in4, GPIO.LOW )

# motor_pins = [in1,in2,in3,in4]
# motor_step_counter = 0 ;

# def cleanup():
#     GPIO.output( in1, GPIO.LOW )
#     GPIO.output( in2, GPIO.LOW )
#     GPIO.output( in3, GPIO.LOW )
#     GPIO.output( in4, GPIO.LOW )
#     GPIO.cleanup()

# # the meat
# try:
#     GPIO.output(in1, GPIO.HIGH)
#     time.sleep( 5 )
#     GPIO.output(in1, GPIO.LOW)
#     GPIO.output(in2, GPIO.HIGH)
#     time.sleep( 5 )
#     GPIO.output(in2, GPIO.LOW)
#     GPIO.output(in3, GPIO.HIGH)
#     time.sleep( 5 )
#     GPIO.output(in3, GPIO.LOW)
#     GPIO.output(in4, GPIO.HIGH)
#     time.sleep( 5 )
#     GPIO.output(in4, GPIO.LOW)
#     # i = 0
#     # for i in range(step_count):
#     #     for pin in range(0, len(motor_pins)):
#     #         GPIO.output( motor_pins[pin], step_sequence[motor_step_counter][pin] )
#     #     if direction==True:
#     #         motor_step_counter = (motor_step_counter - 1) % 8
#     #     elif direction==False:
#     #         motor_step_counter = (motor_step_counter + 1) % 8
#     #     else: # defensive programming
#     #         print( "uh oh... direction should *always* be either True or False" )
#     #         cleanup()
#     #         exit( 1 )
#     #     time.sleep( step_sleep )

# except KeyboardInterrupt:
#     cleanup()
#     exit( 1 )

# cleanup()
# exit( 0 )

# import RPi.GPIO as GPIO
# from RpiMotorLib import RpiMotorLib

# # Use BCM mode for GPIO numbering
# GPIO.setmode(GPIO.BCM)

# # Define GPIO pins for ULN2003
# pins = [26, 19, 13, 6]  

# # Initialize the stepper motor
# motor = RpiMotorLib.BYJMotor("MyStepper", "28BYJ")

# # Try running the motor forward and backward
# print("Moving Forward...")
# motor.motor_run(pins, 0.005, 512, False, False, "full", 0)

# print("Moving Backward...")
# motor.motor_run(pins, 0.005, 512, True, False, "full", 0)

# # Cleanup GPIO
# GPIO.cleanup()
# print("Test Complete")

# import RPi.GPIO as GPIO
# import time

# # Define GPIO pins
# IN1 = 26  # ULN2003 IN1 (A)
# IN2 = 19  # ULN2003 IN2 (B)
# IN3 = 13  # ULN2003 IN3 (C)
# IN4 = 6   # ULN2003 IN4 (D)

# # Set up GPIO
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(IN1, GPIO.OUT)
# GPIO.setup(IN2, GPIO.OUT)
# GPIO.setup(IN3, GPIO.OUT)
# GPIO.setup(IN4, GPIO.OUT)

# # Define the Half-Step sequence (8 steps per full cycle)
# half_step_sequence = [
#     [1, 0, 0, 0],  # Step 1
#     [1, 1, 0, 0],  # Step 2
#     [0, 1, 0, 0],  # Step 3
#     [0, 1, 1, 0],  # Step 4
#     [0, 0, 1, 0],  # Step 5
#     [0, 0, 1, 1],  # Step 6
#     [0, 0, 0, 1],  # Step 7
#     [1, 0, 0, 1],  # Step 8
# ]

# def move_stepper(steps, direction, delay=0.002):
#     """
#     Moves the stepper motor.
    
#     :param steps: Number of steps to move
#     :param direction: 1 for clockwise, -1 for counterclockwise
#     :param delay: Step delay in seconds
#     """
#     for _ in range(steps):
#         for step in half_step_sequence[::direction]:  # Forward or Reverse
#             GPIO.output(IN1, step[0])
#             GPIO.output(IN2, step[1])
#             GPIO.output(IN3, step[2])
#             GPIO.output(IN4, step[3])
#             time.sleep(delay)

# # Run the stepper motor back and forth
# try:
#     while True:
#         print("Moving Forward ⏩")
#         move_stepper(512, 1)  # 512 half-steps ≈ 1 full revolution
#         time.sleep(1)

#         print("Moving Backward ⏪")
#         move_stepper(512, -1)  # Reverse direction
#         time.sleep(1)

# except KeyboardInterrupt:
#     print("\nStopping motor and cleaning up GPIO.")
#     GPIO.cleanup()
