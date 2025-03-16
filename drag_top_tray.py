import pigpio
import time

PWM_PIN = 18
duration_per_unit = 1 # this duration of movement (seconds) per unit distance for top conveyor (might be mm or cm or pixels - idk, will depend on measurement unit from opencv/barcode scanner). should be stored somewhere global in the rasppi at calibration. currently just a random value

def drag_top_tray(distance: int):
    """
    Controls the top servo and motor to drag across a certain distance left to right.
    
    :param distance: the number of distance units to drag the top conveyor motor to move the tray across
    """
    # set up servo motor
    pi = pigpio.pi()  # Connect to pigpio daemon

    if not pi.connected:
        raise RuntimeError("pigpio daemon is not running!")

    print(f"Setting PWM on GPIO {pin} ({pulsewidth}us pulse)...")
    pi.set_PWM_frequency(PWM_PIN, 50)  # Set 50Hz frequency

  
    pi.set_servo_pulsewidth(PWM_PIN, 1500)  # Move to 90 degrees
  

    # clean up servo motor
    pi.set_servo_pulsewidth(PWM_PIN, 0)  # Stop signal
    pi.stop()

# Example usage:
if __name__ == "__main__":
    drag_top_tray(2)
