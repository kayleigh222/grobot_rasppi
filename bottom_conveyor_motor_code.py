import RPi.GPIO as GPIO
import time

# Define GPIO pins for ULN2003 driver
IN1 = 14
IN2 = 15
IN3 = 18
IN4 = 23

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

def set_up_bottom_conveyor():
    # Set GPIO mode and configure pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)

# Function to move the stepper motor one step
def step(delay, step_sequence):
    """Activates motor coils for a single step."""
    GPIO.output(IN1, step_sequence[0])
    GPIO.output(IN2, step_sequence[1])
    GPIO.output(IN3, step_sequence[2])
    GPIO.output(IN4, step_sequence[3])
    time.sleep(delay)

# Function to move the stepper motor forward
def step_bottom_conveyor_backward(steps, delay=0.001):
    """Moves the motor forward by a given number of steps."""
    for _ in range(steps):
        for step_seq in seq:  # Iterate through the sequence
            step(delay, step_seq)

# Function to move the stepper motor backward
def step_bottom_conveyor_forward(steps, delay=0.001):
    """Moves the motor backward by a given number of steps."""
    for _ in range(steps):
        for step_seq in reversed(seq):  # Iterate in reverse
            step(delay, step_seq)

def clean_up_bottom_conveyor():
    GPIO.cleanup()  # Clean up GPIO settings
    
if __name__ == "__main__":
    print("Moving bottom conveyor backward")
    clean_up_bottom_conveyor()  # Clean up any previous settings
    set_up_bottom_conveyor()
    step_bottom_conveyor_backward(500)
    clean_up_bottom_conveyor()
