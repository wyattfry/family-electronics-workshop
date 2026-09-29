# Shared helper for the HC-SR04: TRIG on GP19, ECHO on GP20 via a 1k/2k divider.
from machine import Pin, time_pulse_us
import time

SPEED_OF_SOUND_CM_PER_US = 0.0343  # at ~20 C; try measuring it yourself!

trig = Pin(19, Pin.OUT, value=0)
echo = Pin(20, Pin.IN)


def distance_cm():
    """Distance in cm, or None if nothing echoed back within ~5 m."""
    trig.low()
    time.sleep_us(2)
    trig.high()
    time.sleep_us(10)  # a 10 us pulse tells the sensor to "chirp"
    trig.low()
    t = time_pulse_us(echo, 1, 30000)  # how long ECHO stays high, in us
    if t < 0:
        return None
    return t * SPEED_OF_SOUND_CM_PER_US / 2  # there AND back, so halve it
