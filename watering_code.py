import RPi.GPIO as GPIO
import time

from vertical_conveyor_right_motor_code import clean_up_right_conveyor, move_right_conveyor, set_up_right_conveyor

# turns on the watering system for X seconds. to be scheduled by a cronjob.

WATERING_TIME = 10 # seconds to turn on misting system

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
time.sleep(5)
move_right_conveyor(1500) # Move down 1000 steps
clean_up_right_conveyor()
