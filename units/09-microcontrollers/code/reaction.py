# Lesson 11: reaction-time game. Wait for the green LED, then press fast!
# Pressing early is a false start.
from machine import Pin, PWM
import time
import random

button = Pin(16, Pin.IN, Pin.PULL_UP)
red, green = Pin(13, Pin.OUT), Pin(15, Pin.OUT)
buzzer = PWM(Pin(18))
best = None


def pressed():
    return button.value() == 0


while True:
    print("Get ready... (release the button)")
    while pressed():
        pass
    red.on()
    wait_until = time.ticks_add(time.ticks_ms(), random.randint(1500, 5000))
    false_start = False
    while time.ticks_diff(wait_until, time.ticks_ms()) > 0:
        if pressed():
            false_start = True
            break
    red.off()
    if false_start:
        print("False start!")
        buzzer.freq(200); buzzer.duty_u16(32768); time.sleep(0.4); buzzer.duty_u16(0)
        time.sleep(1)
        continue

    green.on()
    start = time.ticks_us()
    while not pressed():
        pass
    ms = time.ticks_diff(time.ticks_us(), start) / 1000
    green.off()
    best = ms if best is None else min(best, ms)
    print("%d ms   (best %d ms)" % (ms, best))
    time.sleep(1.5)
