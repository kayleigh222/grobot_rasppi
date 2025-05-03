import RPi.GPIO as GPIO
import time

# turns on the watering system for X seconds. to be scheduled by a cronjob.

WATERING_TIME = 30 # seconds to turn on misting system

# compressor relay setup
RELAY_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

GPIO.output(RELAY_PIN, GPIO.LOW)
print("Watering system activated")
time.sleep(WATERING_TIME)
GPIO.output(RELAY_PIN, GPIO.HIGH)
print("Watering system deactivated")
