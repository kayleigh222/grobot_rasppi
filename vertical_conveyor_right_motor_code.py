import RPi.GPIO as GPIO
import time

# Define GPIO pins based on new wiring
DIR_PIN = 21     # Direction control
STEP_PIN = 20   # Step signal
SLEEP_PIN = 16   # Sleep mode control
RESET_PIN = 12   # Reset control

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(SLEEP_PIN, GPIO.OUT)
GPIO.setup(RESET_PIN, GPIO.OUT)

# Enable driver by pulling SLEEP and RESET HIGH
GPIO.output(SLEEP_PIN, GPIO.HIGH)
GPIO.output(RESET_PIN, GPIO.HIGH)

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

try:
    while True:
        print("Moving Forward")
        move_stepper(200, "CW")  # Move 200 steps clockwise
        time.sleep(1)
        
        print("Moving Backward")
        move_stepper(200, "CCW") # Move 200 steps counterclockwise
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping motor and cleaning up GPIO")
    GPIO.cleanup()