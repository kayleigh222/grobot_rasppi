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
