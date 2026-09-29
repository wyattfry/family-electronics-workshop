# Lesson 2: traffic light. LEDs on GP13 (red), GP14 (yellow), GP15 (green).
from machine import Pin
import time

red = Pin(13, Pin.OUT)
yellow = Pin(14, Pin.OUT)
green = Pin(15, Pin.OUT)

# (which light, how many seconds) -- change the timing!
steps = [(green, 5), (yellow, 2), (red, 5)]

while True:
    for light, seconds in steps:
        red.off(); yellow.off(); green.off()
        light.on()
        time.sleep(seconds)
