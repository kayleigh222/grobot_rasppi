import pigpio
import time
import RPi.GPIO as GPIO

# TODO - fill in distance per revolution
# TODO - figure out whether stepping top conveyor forward is to the right or to the left
# TODO - test

# SERVO MOTOR VARIABLES
PWM_PIN = 18

# TOP CONVEYOR VARIABLES
# GPIO pins for ULN2003 driver
IN1 = 26
IN2 = 19
IN3 = 13
IN4 = 6

# Define constants
DEG_PER_STEP = 1.8
STEPS_PER_REVOLUTION = int(360 / DEG_PER_STEP)
distance_per_revolution = 1 # the distance travelled by the drag leg  per revolution of the top conveyor motor (might be mm or cm or pixels - idk, will depend on measurement unit from opencv/barcode scanner). should be stored somewhere global in the rasppi at calibration. currently just a random value

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

# Function to move the top conveyor stepper motor one step
def step(delay, step_sequence):
    """Activates motor coils for a single step."""
    GPIO.output(IN1, step_sequence[0])
    GPIO.output(IN2, step_sequence[1])
    GPIO.output(IN3, step_sequence[2])
    GPIO.output(IN4, step_sequence[3])
    time.sleep(delay)

# Function to move the top conveyor stepper motor forward
def step_forward(delay, steps):
    """Moves the motor forward by a given number of steps."""
    for _ in range(steps):
        for step_seq in seq:  # Iterate through the sequence
            step(delay, step_seq)

# Function to move the top conveyor stepper motor backward
def step_backward(delay, steps):
    """Moves the motor backward by a given number of steps."""
    for _ in range(steps):
        for step_seq in reversed(seq):  # Iterate in reverse
            step(delay, step_seq)

def drag_top_tray(distance: int):
    """
    Controls the top servo and motor to drag across a certain distance left to right.
    
    :param distance: the number of distance units to drag the top conveyor motor to move the tray across
    """
    # SET UP SERVO MOTOR
    pi = pigpio.pi()  # Connect to pigpio daemon

    if not pi.connected:
        raise RuntimeError("pigpio daemon is not running!")

    pi.set_PWM_frequency(PWM_PIN, 50)  # Set 50Hz frequency

    # SET UP TOP CONVEYOR
    # Set GPIO mode and configure pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)

    # DRAG MOVEMENT
    pi.set_servo_pulsewidth(PWM_PIN, 1500)  # Move to 90 degrees

    # calculate how many steps to move the given distance
    steps_to_take = distance/distance_per_revolution
    
    step_forward(delay, steps_to_take) # TODO - might be backward, depends on direction that's left to right

    # CLEAN UP
    # return to initial position
    step_backward(delay, steps_to_take) # TODO - might be forward, depends on direction that's left to right
    
    # clean up servo motor
    pi.set_servo_pulsewidth(PWM_PIN, 0)  # Stop signal
    pi.stop()

# Example usage:
if __name__ == "__main__":
    drag_top_tray(2)
