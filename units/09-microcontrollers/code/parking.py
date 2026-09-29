# Lesson 7: parking sensor. Beeps faster as things get closer; solid tone when
# very close. Change the numbers to tune it.
from machine import Pin, PWM
import time
from ultrasonic import distance_cm

buzzer = PWM(Pin(18))
buzzer.freq(1000)

FAR = 100    # cm: silence beyond this
CLOSE = 10   # cm: solid tone inside this


def gap_for(d):
    """Map distance to the pause between beeps (seconds)."""
    return 0.05 + (d - CLOSE) / (FAR - CLOSE) * 0.6


while True:
    d = distance_cm()
    if d is None or d > FAR:
        buzzer.duty_u16(0)
        time.sleep(0.1)
    elif d < CLOSE:
        buzzer.duty_u16(32768)
        time.sleep(0.05)
    else:
        buzzer.duty_u16(32768)
        time.sleep(0.05)
        buzzer.duty_u16(0)
        time.sleep(gap_for(d))
