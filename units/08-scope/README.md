# Unit 8: Build a Scope

> A pocket oscilloscope we soldered ourselves, so we can SEE electricity wiggle.

**Sessions:** 3–4 · **Cost:** ~$25–40 · **Badges:** Signal Spotter, (new) 🎯 Calibrator
**Prerequisites:** Units 4 and 7 (the bench supply powers it)

## What we're building

1. **Main build:** a **JYE Tech DSO138** (or DSO150) DIY oscilloscope kit.
   - Specs: 1 channel, ~200 kHz analog bandwidth, 1 MSa/s, 2.4" color screen, 9 V input.
   - Many kits ship with the SMD processor pre-soldered, leaving about 100 through-hole and
     easy SMD parts. Check the listing: "SMD pre-soldered" vs "full DIY".
2. **Level-up:** a **Raspberry Pi Pico scope** running **Scoppy** (firmware on the Pico, an
   Android app as the display), with a front end we build ourselves.

**Honest limits:** 200 kHz is plenty for audio, 555s, PWM, servo pulses and the bench
supply's ripple. It's **not** enough for radio frequencies. For Units 11 and 13 we use a
tinySA or a real scope.

## How it works (kid version)

- A multimeter tells you **one number**. A scope draws a **picture of the voltage over
  time**: left to right is time, up and down is voltage.
- Inside it, a chip measures the voltage a million times a second and draws dots.
- Now we can finally *see* the Punk Console's pulses, and the blinker's capacitor filling
  up.

## How it works (grown-up version)

**Front end.**
- A switched attenuator (1×/10× and so on), then an op-amp gain stage and an offset
  (vertical position).
- It's AC/DC coupled.
- The **trimmer caps** compensate the attenuator divider so square waves stay square. That
  is exactly what compensating a ×10 probe does.

**Digitizing.** An STM32's internal ADC samples at up to 1 MSa/s, and the firmware handles
the trigger, timebase and display.

## Jobs

| Step | 8 y.o. | 11 y.o. | Parent |
|---|---|---|---|
| Sort and identify parts against the kit list | Leads, with the meter | Checks resistors | |
| Resistors and diodes | Solders a batch | Solders the rest | Checks |
| Caps, switches, connectors, trimmers | | Solders them | |
| First power-up (bench supply, **9 V, 100 mA limit**) | Reads the meter | Measures the test points from the manual | |
| Compensation calibration | Watches the square wave "fix itself" | Adjusts the trimmers | |
| Case (acrylic kit case or a 3D print) | Assembles it | | |

## Steps

1. **Read the manual together.** JYE's assembly guide is good and includes test-point
   voltages. Build in the order it says.
2. Solder low parts first (resistors), then taller ones.
3. **First power-up on the Unit 7 supply at 9 V with the 100 mA limit.** Note the current
   draw.
   - If it sits at the limit, power off and hunt for the short.
   - Otherwise, check the test-point voltages listed in the manual.
4. **Calibrate:** connect the probe to the built-in 1 kHz test signal. Adjust the trimmer
   caps until the square wave has flat tops (no overshoot or rounding).
   → **Calibrator** badge.

## Scope lab (the payoff)

Each experiment gets a screenshot or phone photo in the build log.

| # | Look at | What you learn |
|---|---|---|
| 1 | 9 V battery, then the bench supply | DC is a flat line. Measure the supply's ripple on AC coupling. |
| 2 | Unit 1 blinker, **base of a transistor** | Negative dips! The capacitor pulls the base below ground, which is why we kept Vcc ≤ 6 V. |
| 3 | Unit 1 blinker, the capacitor charging | RC charging curve; measure the time constant |
| 4 | Unit 4 Punk Console, IC1 vs IC2 outputs | Pulse width vs frequency; the "skipped" triggers that make the steps |
| 5 | Servo signal from the Pico (Unit 9) | 50 Hz, 0.5–2.5 ms pulses; watch the width change with the angle |
| 6 | Voice into a microphone amp | What sound looks like |
| 7 | Line follower sensor (Unit 5) passing over the tape | The sensor's analog signal, and where the threshold sits |

## Level-up: Pico scope (Scoppy)

- **Scoppy** runs on a Pico and streams to an Android phone or tablet as the display. The
  free tier is limited; check the current feature list.
- **Our part to build:** a front end that makes ±10 V input safe for the Pico's 0–3.3 V ADC:
  1. a resistor divider (e.g. 10:1)
  2. a mid-rail offset, via a divider from 3V3
  3. clamp diodes to the rails
  4. a buffer op-amp (MCP6002: rail-to-rail, runs from 3.3 V)
- Design it in KiCad and etch it (Unit 6 skills). Compare it with the DSO138 on the same
  signal.

## Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| Blank screen | 9 V backwards, regulator not soldered, display connector | Test points in the manual |
| Trace stuck at the top or bottom | Offset or op-amp stage fault | Op-amp supply voltages |
| Square wave has spikes or rounded corners | Uncompensated attenuator | Trimmer caps, per the manual |
| Noisy trace | Long ground lead | Short ground clip |

## Talk about it

- What could the scope show us that the multimeter couldn't?
- Why does the 1 kHz square wave look rounded until we adjust the little trimmer?
