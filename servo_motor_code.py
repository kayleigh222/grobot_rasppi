import pigpio
import time

PWM_PIN = 13
pi = pigpio.pi()  # Connect to pigpio daemon for PWM

if not pi.connected:
    exit("pigpio is not running!")

print("Setting PWM on GPIO 13 (50Hz, 1.5ms pulse)...")
pi.set_PWM_frequency(PWM_PIN, 50)  # 50Hz servo frequency
pi.set_servo_pulsewidth(PWM_PIN, 1500)  # Move to center position (90 degrees)

time.sleep(2)

print("Moving to 0 degrees...")
pi.set_servo_pulsewidth(PWM_PIN, 500)  # ~60 degrees
time.sleep(2)

pi.set_servo_pulsewidth(PWM_PIN, 1500)  # Neutral / no movement
time.sleep(2)
pi.set_servo_pulsewidth(PWM_PIN, 1000)  # Should rotate continuously if modified

time.sleep(10)
print("Stopping PWM...")
pi.set_servo_pulsewidth(PWM_PIN, 0)  # Stop signal
pi.stop()
