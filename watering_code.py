import RPi.GPIO as GPIO
import time

from vertical_conveyor_right_motor_code import move_right_conveyor, set_up_right_conveyor

# turns on the watering system for X seconds. to be scheduled by a cronjob.

WATERING_TIME = 5 # seconds to turn on misting system

# compressor relay setup
RELAY_PIN = 17
set_up_right_conveyor()
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

GPIO.output(RELAY_PIN, GPIO.LOW)
print("Watering system activated")
time.sleep(WATERING_TIME)
GPIO.output(RELAY_PIN, GPIO.HIGH)
print("Watering system deactivated")
move_right_conveyor(500) # Move down 1000 steps
