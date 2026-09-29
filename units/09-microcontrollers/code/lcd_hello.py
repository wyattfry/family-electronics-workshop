# Lesson 9: LCD on I2C0 (SDA GP4, SCL GP5). Needs lcd_i2c.py saved on the Pico.
from machine import I2C, Pin
import time
from lcd_i2c import LCD

i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100_000)
found = i2c.scan()
print("I2C devices:", [hex(a) for a in found])  # expect 0x27 or 0x3f
lcd = LCD(i2c, addr=found[0])

messages = [  # write your own! 16 characters per line max
    ("Hello, world!", "I'm a Pico :)"),
    ("Soldered by", "our family"),
]

while True:
    for top, bottom in messages:
        lcd.show(top, bottom)
        time.sleep(3)
