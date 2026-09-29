# Lesson 5: PIR motion sensor (OUT on GP17) sounds the buzzer (GP18) and red LED.
# Give the PIR ~60 s after power-up to settle before trusting it.
from machine import Pin, PWM
import time

pir = Pin(17, Pin.IN)
led = Pin(13, Pin.OUT)
buzzer = PWM(Pin(18))


def siren(times=3):
    for _ in range(times):
        for f in (880, 660):
            buzzer.freq(f)
            buzzer.duty_u16(32768)
            time.sleep(0.15)
    buzzer.duty_u16(0)


print("Warming up...")
time.sleep(30)
print("Armed!")

was_moving = False
while True:
    moving = pir.value() == 1
    led.value(moving)
    if moving and not was_moving:  # only on the *start* of motion
        print("Motion!", time.ticks_ms() // 1000, "s")
        siren()
    was_moving = moving
    time.sleep(0.05)
