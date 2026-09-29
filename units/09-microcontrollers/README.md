# Unit 9: Microcontrollers and Sensors

> Teach a chip to blink, play songs, notice motion, measure distance, move servos, and
> write on a screen. Then combine them into a Sentry that guards your room.

**Sessions:** 6–8 · **Cost:** ~$40 · **Badges:** Coder, Current Catcher
**Prerequisites:** Units 1 and 7. Unit 5 for the robot level-up.

We use a **Raspberry Pi Pico** (RP2040, or RP2350 on the Pico 2) with **MicroPython**,
edited in **Thonny**. Python runs line by line and gives readable errors, and Thonny's
Shell lets the kids poke at pins live. The 11 y.o. can move to Arduino C++ later; the lab
sketches in `~/legv2` already use it.

## Kit

| Qty | Part | Notes |
|---|---|---|
| 1 per kid | Raspberry Pi Pico (plain, **no headers**) | Soldering the headers on is the first job |
| 1 per kid | Breadboard, jumper wires | |
| — | LEDs (red, yellow, green), 330 Ω resistors, 2 pushbuttons | |
| 1 | Passive piezo buzzer | *Passive*, so we choose the pitch. An active buzzer only beeps one tone. |
| 1 | HC-SR501 PIR motion sensor | Runs from 5 V; its output is 3.3 V, so it's Pico-safe |
| 1 | HC-SR04 ultrasonic distance sensor | Runs from 5 V. **Its echo is 5 V: use a divider** (below), or buy the 3.3 V-capable HC-SR04P / RCWL-1601. |
| 1 | 1 kΩ + 2 kΩ resistors | Echo divider |
| 1 | SG90 or MG90S micro servo | Same family as the quadruped |
| 1 | 16×2 I2C LCD (PCF8574 backpack) | Also used in `~/legv2/lcd_love_languages.ino` |
| — | Unit 7 bench supply at 5 V | **Separate** servo power |

## Pin map (all lessons share it, so nothing gets rewired)

| Pico pin | Connects to |
|---|---|
| `LED` (onboard) | — |
| GP13 / GP14 / GP15 | Red / yellow / green LED, each through 330 Ω to GND |
| GP16 | Button to GND (internal pull-up) |
| GP17 | PIR OUT |
| GP18 | Passive buzzer (other leg to GND) |
| GP19 | HC-SR04 TRIG |
| GP20 | HC-SR04 ECHO **through the divider**: ECHO → 1 kΩ → GP20, with 2 kΩ from GP20 to GND |
| GP22 | Servo signal (orange) |
| GP4 / GP5 | LCD SDA / SCL (I2C0) |
| VBUS (pin 40) | 5 V from USB: PIR, HC-SR04, LCD |
| GND | Everything's ground, **including the servo supply's ground** |

## Lessons

Each lesson is one session. The files live in [`code/`](code/). Copy `lcd_i2c.py` onto the
Pico once, for the lessons that use the screen.

| # | File | Lesson | Concept | 8 y.o. | 11 y.o. |
|---|---|---|---|---|---|
| 1 | `blink.py` | Solder the headers, then blink | Output, loops | Holds the board, solders a few pins | Solders the rest |
| 2 | `traffic.py` | Traffic light | Sequences, `sleep` | Picks the timing | Writes it |
| 3 | `button.py` | Button → LED | Input, `if`, pull-ups | Presses the button, then tweaks the code | Explains the pull-up |
| 4 | `songs.py` | Buzzer songs | PWM frequency, lists | Composes the song as a list of notes | Writes the player |
| 5 | `motion_alarm.py` | Motion alarm | Digital sensor, events | Tests it by sneaking past | Tunes the PIR's sensitivity and time pots |
| 6 | `ruler.py` | Ultrasonic ruler | Timing a pulse, the speed of sound | Checks it against a tape measure | Calculates the speed of sound backwards from a known distance |
| 7 | `parking.py` | Parking sensor | Mapping one range onto another | Drives a toy car at it | Writes the mapping |
| 8 | `servo.py` | Servo | PWM pulse width | Types in angles | Writes the sweep and the easing |
| 9 | `lcd_hello.py` | LCD messages | I2C | Writes the messages | Wiring, `i2c.scan()` |
| 10 | `sentry.py` | **Sentry** | Everything together | Designs the flag and the alarm song | Builds it |
| 11 | `reaction.py` | Reaction-time game | Timing, randomness | Plays and tests | Builds it |

## Key facts

- **Pico GPIO is 3.3 V.** Never feed 5 V into a pin. That's the reason for the HC-SR04
  echo divider: 5 V × 2k / (1k + 2k) = 3.3 V.
- **Servos never run off the Pico's 3V3 pin.**
  - Feed the servo from a separate 5–6 V supply, with **grounds connected**.
  - Control is a PWM signal at 50 Hz: a 500–2500 µs pulse maps to 0–180°. Check the
    range on your servo; many are narrower.
- **PIR (HC-SR501):**
  - Needs about 30–60 s to settle after power-up.
  - Has two trim pots (sensitivity, hold time) and a jumper: **H** re-triggers, **L** fires
    once.
  - It sees *moving warm things*. A still person disappears.
- **HC-SR04:** measures echo time. The distance is `t × 343 m/s ÷ 2`, because the sound
  goes there and back. It's confused by soft, angled or tiny targets. Range is about
  2 cm to 4 m.
- **LCD:** the PCF8574 backpack sits at `0x27` or `0x3F`. Run `i2c.scan()` first.
  - The backpack's pull-ups go to its own Vcc, so powering it from 5 V pulls SDA and SCL
    to 5 V.
  - Most backpacks work fine powered from 3V3 with a dimmer backlight. Or remove the pull-up
    resistors and keep 5 V.

## Level-ups (bridges to later units)

- **Line follower with a brain:** put the Pico on the Unit 5 chassis.
  - Read the TCRT5000 collectors with the ADC, and drive the MOSFET gates with PWM.
  - Try proportional steering: `speed_diff = k * (left - right)`.
- **Obstacle-avoiding robot:** mount the HC-SR04 on the front of the Unit 5 chassis: "if
  distance < 15 cm, back up and turn". The quadruped's Adeept HAT already has an ultrasonic
  port. See `~/legv2/LEARNINGS.md`: it's on GPIO24, which clashes with the SPI LCD overlay.
- **Ultrasonic theremin:** distance → buzzer pitch. Five lines of change to `parking.py`.
- **Pots → servos:** that's the whole of **Unit 10**.
- **Pico W:** Sentry sends a message to a phone. Later, Unit 12's radio bridge can arm it.
