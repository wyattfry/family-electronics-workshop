# Lesson 1: blink the Pico's onboard LED.
from machine import Pin
import time

led = Pin("LED", Pin.OUT)

while True:
    led.toggle()
    time.sleep(0.5)  # try 0.1 or 2 -- what changes?
