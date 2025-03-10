import RPi.GPIO as GPIO
import time

# Define GPIO pins based on new wiring
DIR_PIN = 7     # Direction control
STEP_PIN = 8    # Step signal
SLEEP_PIN = 24   # Sleep mode control
RESET_PIN = 25   # Reset control

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

def move_stepper(steps, direction="CW", delay=0.001):
    if direction == "CW":
        GPIO.output(DIR_PIN, GPIO.HIGH)
        print("Direction: CW (HIGH)")
    else:
        GPIO.output(DIR_PIN, GPIO.LOW)
        print("Direction: CCW (LOW)")
    time.sleep(0.01)  # Add small delay to allow direction change

    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(delay)

try:
    while True:
        print("Moving Forward")
        move_stepper(800, "CW")  # Move 200 steps clockwise
        time.sleep(1)
        
        print("Moving Backward")
        move_stepper(800, "CCW") # Move 200 steps counterclockwise
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping motor and cleaning up GPIO")
    GPIO.cleanup()
