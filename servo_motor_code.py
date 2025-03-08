import RPi.GPIO as GPIO
import time

# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the servo pin
SERVO_PIN = 18

# Set up the pin as an output
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Set PWM frequency to 50Hz (Standard for SG90 servos)
pwm = GPIO.PWM(SERVO_PIN, 50)

# Start PWM with 0-degree position
pwm.start(0)

def set_angle(angle):
    """ Move the servo to a specific angle (0 to 180). """
    duty_cycle = (angle / 18) + 2  # Convert angle to duty cycle
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)  # Give the servo time to reach position
    pwm.ChangeDutyCycle(0)  # Prevent jitter

try:
    set_angle(90)
    time.sleep(0.5)  # Give the servo time to reach position
    set_angle(0)


except KeyboardInterrupt:
    print("\nExiting...")

# finally:
#     pwm.stop()
#     GPIO.cleanup()
