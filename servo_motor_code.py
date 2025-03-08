import pigpio
import time

PWM_PIN = 18
pi = pigpio.pi()  # Connect to pigpio daemon

if not pi.connected:
    exit("pigpio is not running!")

print("Setting PWM on GPIO 18 (50Hz, 1.5ms pulse)...")
pi.set_PWM_frequency(PWM_PIN, 50)  # 50Hz servo frequency
pi.set_servo_pulsewidth(PWM_PIN, 1500)  # Move to center position (90 degrees)

time.sleep(2)

print("Moving to 60 degrees...")
pi.set_servo_pulsewidth(PWM_PIN, 1200)  # ~60 degrees
time.sleep(2)

print("Moving to 120 degrees...")
pi.set_servo_pulsewidth(PWM_PIN, 1800)  # ~120 degrees
time.sleep(2)

print("Stopping PWM...")
pi.set_servo_pulsewidth(PWM_PIN, 0)  # Stop signal
pi.stop()


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
#     set_angle(90)
    # time.sleep(0.5)  # Give the servo time to reach position
    # set_angle(0)


# except KeyboardInterrupt:
#     print("\nExiting...")

# # finally:
# #     pwm.stop()
# #     GPIO.cleanup()
