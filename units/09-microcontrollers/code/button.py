# Lesson 3: button on GP16 (other side to GND) lights the red LED on GP13.
# PULL_UP means the pin reads 1 when nothing is pressed, and 0 when the button
# connects it to ground.
from machine import Pin
import time

button = Pin(16, Pin.IN, Pin.PULL_UP)
led = Pin(13, Pin.OUT)

while True:
    pressed = button.value() == 0
    led.value(pressed)
    time.sleep(0.01)
