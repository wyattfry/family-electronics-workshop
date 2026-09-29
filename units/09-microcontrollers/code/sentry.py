# Lesson 10: SENTRY. Guards a doorway.
#   PIR notices motion -> ultrasonic measures how close -> servo raises a flag,
#   LCD reports, buzzer warns (louder/faster the closer they get).
# Press the button to disarm / re-arm.
from machine import I2C, Pin, PWM
import time
from lcd_i2c import LCD
from ultrasonic import distance_cm
from servo import set_angle

FLAG_DOWN, FLAG_UP = 20, 110
ALARM_CM = 150

pir = Pin(17, Pin.IN)
button = Pin(16, Pin.IN, Pin.PULL_UP)
red, green = Pin(13, Pin.OUT), Pin(15, Pin.OUT)
buzzer = PWM(Pin(18))
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100_000)
lcd = LCD(i2c, addr=i2c.scan()[0])


def beep(freq, ms):
    buzzer.freq(freq)
    buzzer.duty_u16(32768)
    time.sleep_ms(ms)
    buzzer.duty_u16(0)


shown = None


def show(top, bottom):
    """Only redraw the LCD when the text changes (avoids flicker)."""
    global shown
    if (top, bottom) != shown:
        lcd.show(top, bottom)
        shown = (top, bottom)


armed = True
set_angle(FLAG_DOWN)
lcd.show("SENTRY", "warming up...")
time.sleep(30)

while True:
    if button.value() == 0:  # toggle arm/disarm
        armed = not armed
        beep(1200 if armed else 600, 150)
        time.sleep(0.5)

    if not armed:
        red.off(); green.off()
        set_angle(FLAG_DOWN)
        show("SENTRY", "disarmed")
        time.sleep(0.3)
        continue

    d = distance_cm() if pir.value() else None
    if d is not None and d < ALARM_CM:
        red.on(); green.off()
        set_angle(FLAG_UP)
        show("INTRUDER!", "at %d cm" % d)
        beep(2000 - int(d * 8), 80)  # higher pitch when closer
        time.sleep(0.05 + d / 1000)
    else:
        red.off(); green.on()
        set_angle(FLAG_DOWN)
        show("SENTRY", "all clear")
        time.sleep(0.3)
