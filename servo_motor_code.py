import time

PWM_PIN = 13
sweeping = False

def set_up_servo(pi):
    if not pi.connected:
        raise Exception("pigpio is not running!")

    # Set frequency for servo (50Hz typical)
    pi.set_PWM_frequency(PWM_PIN, 50)


def sweep_servo(pi):
    global sweeping  # Reference the global sweeping variable
    print("Starting sweep between 0° and 180°...")
    while sweeping:
        pi.set_servo_pulsewidth(PWM_PIN, 500) # move to 0 degrees
        time.sleep(0.5)  # Delay between moves
        pi.set_servo_pulsewidth(PWM_PIN, 2500) # move to 180 degrees
        time.sleep(0.5)

    print("Stopping servo...")
    pi.set_servo_pulsewidth(PWM_PIN, 0)  # Stop signal

def clean_up_servo(pi):
    pi.set_servo_pulsewidth(PWM_PIN, 0)  # Stop signal
    pi.stop()  # Stop pigpio


