import time
import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib

# Define GPIO pins (change these according to your wiring)
pins = [26, 19, 13, 6]  # Adjust based on wiring

# Create a stepper motor instance
motor = RpiMotorLib.BYJMotor("MyStepper", "28BYJ")

# Run motor forward
motor.motor_run(pins, .002, 512, False, False, "full", 0)

# Run motor backward
motor.motor_run(pins, .002, 512, True, False, "full", 0)

# Cleanup GPIO
GPIO.cleanup()

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
