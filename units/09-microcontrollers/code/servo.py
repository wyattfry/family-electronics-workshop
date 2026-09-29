# Lesson 8: servo on GP22. Servo power comes from a separate 5 V supply;
# its ground MUST be joined to the Pico's ground.
from machine import Pin, PWM
import time

MIN_US, MAX_US = 500, 2500  # check your servo's range; stay off the end stops

servo = PWM(Pin(22))
servo.freq(50)  # one pulse every 20 ms


def set_angle(deg):
    deg = max(0, min(180, deg))
    us = MIN_US + (MAX_US - MIN_US) * deg / 180
    servo.duty_ns(int(us * 1000))


def ease_to(start, end, seconds=1.0, steps=50):
    """Move smoothly: slow start, fast middle, slow finish."""
    for i in range(steps + 1):
        t = i / steps
        smooth = t * t * (3 - 2 * t)
        set_angle(start + (end - start) * smooth)
        time.sleep(seconds / steps)


if __name__ == "__main__":
    set_angle(90)
    time.sleep(1)
    while True:
        ease_to(30, 150)
        ease_to(150, 30)
