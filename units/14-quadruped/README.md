# Unit 14: Quadruped

> Finish the walking robot: four plywood legs, eight servos, a Raspberry Pi brain.

**Sessions:** 6+ · **Badges:** Puppeteer, Debugger, Heat Manager
**Prerequisites:** Units 7, 8, 9, 10. Unit 5's robot ideas help.

**This unit lives in `~/legv2`, a separate family repo (not public yet).** Design, geometry analysis
and calibration are already underway there. Its README is the source of truth. This page
is the *family plan*: who does what, and what each step teaches.

## Where things stand (from `~/legv2/README.md`, 2026-09-26)

- ✅ The v2 two-servo linkage leg is designed, with a geometry notebook and 1:1 print
  templates.
- ✅ The ch2/ch3 leg is calibrated: linear gains, backlash under 1°, and the linkage
  model's G and X predictions confirmed.
- ⚠️ The ch0/ch1 leg is **not calibrated** (it inherits the ch2/ch3 values).
- ⚠️ The calf length is unresolved (built at 84 mm, being cut down; 63–70 mm under
  consideration).
- ⏭️ Two more legs, a body, power distribution, and a four-leg gait.

## Family work breakdown

| Task | What it teaches | 8 y.o. | 11 y.o. | Parent |
|---|---|---|---|---|
| **Settle the calf length** | Measurement, testing a hypothesis | Measures with calipers | Runs `legs.py --dry-run --calf N` and compares the foot paths | Decides |
| **Cut legs 3 and 4** | Templates, tools | Sands, labels the parts with the channel numbers (never sides!) | Transfers the 1:1 templates | Cuts |
| **Servo check** | Test before you install | Centers every servo with the **Unit 10 servo tester** before attaching the horns | Logs each servo's range | |
| **Power distribution board** | Current budgets, wire gauge | Solders the servo headers | Calculates the budget, designs and etches the board (Unit 6) | Checks the budget |
| **Calibrate ch0/ch1** | Closed-loop measurement | Keeps the camera rig still, holds the white backdrop | Runs the capture with the parent | Scripts, see `LEARNINGS.md` |
| **Body** | Design, center of mass | Designs the shell: the raven? (see `raven_biped_sketch.png`) | Mounts the Pi, HAT, and battery | |
| **Gait tuning** | Iteration, logging | Stopwatch, video, "is it walking or falling?" | Adjusts amp, freq, and trim in the web UI; keeps a table | |
| **Waldo control** | Kinematics | Drives the leg with the Unit 10 waldo | Adds `POST /api/pose` to `legs.py` so a Pico W can drive it over WiFi | Reviews |
| **Eyes** | Sensors | | Hooks up the ultrasonic on the Adeept HAT (GPIO24; conflicts with the SPI LCD overlay) and makes it stop before walls | |

## Power budget (an 11 y.o. worksheet)

| Load | Count | Each | Total |
|---|---|---|---|
| SG90-class servo, moving | 8 | ~150–250 mA | ~1.2–2 A |
| SG90-class servo, stalled (it happens!) | — | ~650 mA+ | |
| Raspberry Pi 3B | 1 | ~0.5–1 A at 5 V | |

**Questions:**
- What's the worst case if all 8 stall?
- What wire gauge carries that?
- Why must the servo supply be **separate** from the Pi's supply, with the grounds joined?

## Milestones

- [ ] Calf length decided and all 4 legs cut
- [ ] All 8 servos centered, installed, and range-checked
- [ ] Power board built, and the current measured with the Unit 7 supply
- [ ] ch0/ch1 calibrated
- [ ] Stands on 4 legs, powered
- [ ] First steps (video it!)
- [ ] Walks across the room
- [ ] Stops before a wall (ultrasonic)
- [ ] Radio-controlled via the Unit 12 DTMF decoder 🏆
