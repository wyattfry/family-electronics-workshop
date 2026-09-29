# Unit 10 Stage B: 3 pots -> 3 servos, with record and playback.
#   Pots: wipers on GP26/27/28, ends on 3V3 and GND.
#   Servos: signals on GP10/11/12, powered from a separate 5 V supply (grounds joined!).
#   Buttons (to GND): GP16 = hold to record, GP9 = play/stop.  Red LED on GP13.
from machine import ADC, Pin, PWM
import time

MIN_US, MAX_US = 600, 2400   # a bit inside 500..2500 to spare the end stops
LIMITS = [(0, 180), (20, 160), (30, 120)]  # per-servo angle limits: tune for your build
SMOOTH = 0.2                 # 0..1: lower = smoother but laggier
DEADBAND = 1.0               # degrees: ignore tinier changes (stops jitter)
TICK_MS = 20                 # one servo frame

pots = [ADC(Pin(p)) for p in (26, 27, 28)]
servos = [PWM(Pin(p)) for p in (10, 11, 12)]
for s in servos:
    s.freq(50)
record_btn = Pin(16, Pin.IN, Pin.PULL_UP)
play_btn = Pin(9, Pin.IN, Pin.PULL_UP)
rec_led = Pin(13, Pin.OUT)


def write_servo(i, deg):
    lo, hi = LIMITS[i]
    deg = max(lo, min(hi, deg))
    us = MIN_US + (MAX_US - MIN_US) * deg / 180
    servos[i].duty_ns(int(us * 1000))


def pot_angle(i):
    return pots[i].read_u16() / 65535 * 180


smooth = [pot_angle(i) for i in range(3)]
sent = [None, None, None]
recording = []          # list of (a0, a1, a2) frames: the robot's "memory"
playing = False
play_index = 0
last_play_btn = 1

while True:
    start = time.ticks_ms()

    # Play button toggles playback (on the press, not while held).
    pb = play_btn.value()
    if pb == 0 and last_play_btn == 1 and recording:
        playing = not playing
        play_index = 0
        print("playing" if playing else "stopped", len(recording), "frames")
    last_play_btn = pb

    if playing:
        target = recording[play_index]
        play_index = (play_index + 1) % len(recording)
    else:
        for i in range(3):
            smooth[i] += (pot_angle(i) - smooth[i]) * SMOOTH
        target = tuple(smooth)
        if record_btn.value() == 0:
            if not rec_led.value():
                recording = []   # a new press starts a new recording
                print("recording...")
            rec_led.on()
            recording.append(target)
        elif rec_led.value():
            rec_led.off()
            print("recorded", len(recording), "frames =", len(recording) * TICK_MS / 1000, "s")

    for i in range(3):
        if sent[i] is None or abs(target[i] - sent[i]) >= DEADBAND:
            write_servo(i, target[i])
            sent[i] = target[i]

    time.sleep_ms(max(0, TICK_MS - time.ticks_diff(time.ticks_ms(), start)))
