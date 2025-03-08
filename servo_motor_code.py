import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
SERVO_PIN = 18
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz PWM
pwm.start(0)

def set_duty_cycle(dc):
    """Set raw duty cycle for testing"""
    pwm.ChangeDutyCycle(dc)
    time.sleep(1)  # Wait for the servo to move
    pwm.ChangeDutyCycle(0)  # Stop sending signal to avoid jitter

try:
    print("Setting servo to 0° (approx. 2% duty cycle)...")
    set_duty_cycle(2)  # Adjust between 2 and 2.5 if needed
    time.sleep(5)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    pwm.stop()
    GPIO.cleanup()


# import RPi.GPIO as GPIO
# import time

# # Set GPIO mode
# GPIO.setmode(GPIO.BCM)

# # Define the servo pin
# SERVO_PIN = 18

# # Set up the pin as an output
# GPIO.setup(SERVO_PIN, GPIO.OUT)

# # Set PWM frequency to 50Hz (Standard for SG90 servos)
# pwm = GPIO.PWM(SERVO_PIN, 50)

# # Start PWM with 0-degree position
# pwm.start(0)

# def set_angle(angle):
#     """ Move the servo to a specific angle (0 to 180). """
#     duty_cycle = (angle / 18) + 2  # Convert angle to duty cycle
#     pwm.ChangeDutyCycle(duty_cycle)
#     time.sleep(0.5)  # Give the servo time to reach position
#     pwm.ChangeDutyCycle(0)  # Prevent jitter

# try:
#     while True:
#         angle = int(input("Enter angle (0-180): "))
#         if 0 <= angle <= 180:
#             set_angle(angle)
#         else:
#             print("Invalid angle! Enter a value between 0 and 180.")

# except KeyboardInterrupt:
#     print("\nExiting...")

# finally:
#     pwm.stop()
#     GPIO.cleanup()
