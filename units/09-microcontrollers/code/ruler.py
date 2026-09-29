# Lesson 6: ultrasonic ruler. Prints distance twice a second.
# Challenge: put a box exactly 100 cm away. Use the echo time to work out
# the speed of sound. (Hint: print the raw time from time_pulse_us.)
import time
from ultrasonic import distance_cm

while True:
    d = distance_cm()
    print("nothing there" if d is None else "%.1f cm" % d)
    time.sleep(0.5)
