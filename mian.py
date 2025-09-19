import motors
import time
import random
from gpiozero import DistanceSensor, DigitalInputDevice
from time import monotonic
from config import *

# Initialize HC-SR04 ultrasonic sensors
left_sensor = DistanceSensor(echo=HC_LEFT_ECHO, 
                            trigger=HC_LEFT_TRIG, 
                            max_distance=4)

right_sensor = DistanceSensor(echo=HC_RIGHT_ECHO, 
                             trigger=HC_RIGHT_TRIG, 
                             max_distance=4)

# Custom class for MB1040 sensor (PWM output)
class MB1040Sensor:
    def __init__(self, pin):
        self.pin = DigitalInputDevice(pin)
        self.pin.when_activated = self._rising_edge
        self.pin.when_deactivated = self._falling_edge
        self.start_time = 0
        self.pulse_width = 0
        self.distance = 0
        
    def _rising_edge(self):
        self.start_time = monotonic()
        
    def _falling_edge(self):
        end_time = monotonic()
        self.pulse_width = end_time - self.start_time
        # Convert pulse width to distance (in cm)
        # MB1040 has a scale factor of 58Î¼s per cm (1cm = 58Î¼s)
        self.distance = (self.pulse_width * 1000000) / 58.0
        
    def get_distance(self):
        return self.distance

# Initialize MB1040 sensor
middle_sensor = MB1040Sensor(MB_PW)

def read_all_sensors():
    """Read all three sensors and return distances in cm"""
    try:
        # Get measurements from HC-SR04 sensors
        left_dist = left_sensor.distance * 100  # Convert to cm
        right_dist = right_sensor.distance * 100  # Convert to cm
        
        # Get measurement from MB1040 sensor
        middle_dist = middle_sensor.get_distance()
        
        return left_dist, middle_dist, right_dist
    except Exception as e:
        print(f"Sensor reading error: {e}")
        return float('inf'), float('inf'), float('inf')  # Return safe values on error

def autonomous_mode():
    print("Autonomous Mode: Avoiding obstacles")
    print("Press Ctrl+C to exit")
    
    # Constants
    MIN_DISTANCE = 2  # cm
    MAX_DISTANCE = 400  # cm
    MAX_STATIONARY_TIME = 10  # seconds
    
    last_movement_time = time.time()
    
    try:
        while True:
            try:
                # Check if we've been stationary too long
                if time.time() - last_movement_time > MAX_STATIONARY_TIME:
                    print("Stationary too long, attempting recovery...")
                    motors.backward(speed=0.4)
                    time.sleep(1)
                    motors.stop()
                    last_movement_time = time.time()
                    continue
                
                # Read and filter sensor values
                left, front, right = read_all_sensors()
                left = max(MIN_DISTANCE, min(left, MAX_DISTANCE))
                front = max(MIN_DISTANCE, min(front, MAX_DISTANCE))
                right = max(MIN_DISTANCE, min(right, MAX_DISTANCE))
                
                print(f"Left: {left:.2f} cm, Front: {front:.2f} cm, Right: {right:.2f} cm")
                
                # Emergency maneuver if completely surrounded
                if all(d < SAFE_DISTANCE/2 for d in [left, front, right]):
                    motors.stop()
                    print("Completely surrounded! Attempting random turn.")
                    if random.choice([True, False]):
                        motors.left(speed=0.6)
                    else:
                        motors.right(speed=0.6)
                    time.sleep(1)
                    motors.stop()
                    time.sleep(0.5)
                    last_movement_time = time.time()
                    continue
                
                # Normal obstacle avoidance
                if front < SAFE_DISTANCE:
                    if left > right:
                        motors.left(speed=0.6)
                    else:
                        motors.right(speed=0.6)
                    time.sleep(0.5)
                    motors.stop()
                    time.sleep(0.1)
                    last_movement_time = time.time()
                elif left < SAFE_DISTANCE:
                    motors.right(speed=0.5)
                    time.sleep(0.3)
                    motors.stop()
                    time.sleep(0.1)
                    last_movement_time = time.time()
                elif right < SAFE_DISTANCE:
                    motors.left(speed=0.5)
                    time.sleep(0.3)
                    motors.stop()
                    time.sleep(0.1)
                    last_movement_time = time.time()
                else:
                    # Adjust speed based on available space
                    min_space = min(left, front, right)
                    if min_space > SAFE_DISTANCE * 2:
                        speed = 0.6
                    elif min_space > SAFE_DISTANCE * 1.5:
                        speed = 0.5
                    else:
                        speed = 0.4
                    motors.forward(speed=speed)
                    last_movement_time = time.time()

                time.sleep(0.05)
                
            except Exception as e:
                print(f"Error: {e}. Stopping motors.")
                motors.stop()
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nExiting autonomous mode...")
    finally:
        motors.cleanup()
        # Clean up sensors
        left_sensor.close()
        right_sensor.close()
        middle_sensor.pin.close()

if __name__ == "__main__":
    autonomous_mode()