import RPi.GPIO as GPIO
import time

# Define GPIO pins
DIR_PIN = 21     # Direction control
STEP_PIN = 20   # Step signal
SLEEP_PIN = 16   # Sleep mode control
RESET_PIN = 12   # Reset control

def move_right_conveyor(steps): # steps positive for up, negative for down
    if(steps > 0):
        move_stepper(steps, "CW") # move up
    else:
        print("Moving down")
        steps = abs(steps)
        move_stepper(steps, "CCW") # move down

def set_up_right_conveyor():
    # Setup GPIO
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DIR_PIN, GPIO.OUT)
    GPIO.setup(STEP_PIN, GPIO.OUT)
    GPIO.setup(SLEEP_PIN, GPIO.OUT)
    GPIO.setup(RESET_PIN, GPIO.OUT)
    
    # Enable driver by pulling SLEEP and RESET HIGH
    GPIO.output(SLEEP_PIN, GPIO.HIGH)
    GPIO.output(RESET_PIN, GPIO.HIGH)

def clean_up_right_conveyor():
    # Disable driver by pulling SLEEP and RESET LOW
    GPIO.output(SLEEP_PIN, GPIO.LOW)
    GPIO.output(RESET_PIN, GPIO.LOW)
    GPIO.cleanup()

# Function to move the stepper motor
def move_stepper(steps, direction="CW", delay=0.001):
    # Set direction
    GPIO.output(DIR_PIN, GPIO.HIGH if direction == "CW" else GPIO.LOW)

    # Pulse the STEP pin
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(delay)

if __name__ == "__main__":
    set_up_right_conveyor()
    move_right_conveyor(1000) # Move up 1000 steps