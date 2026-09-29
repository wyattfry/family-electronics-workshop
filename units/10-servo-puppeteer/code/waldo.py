# Unit 10 Stage C: the Waldo. A hand-moved replica leg with pots at its joints
# drives the real ~/legv2 leg.
#
#   Hip pot  (thigh angle vs the base)  wiper -> GP26
#   Knee pot (calf angle vs the thigh)  wiper -> GP27
#   Real leg hip servo -> GP10, knee servo -> GP11 (unplugged from the PCA9685 HAT)
#   Zero button (to GND) -> GP16
#
# HOW TO USE: put the real leg AND the waldo in the same pose (the 1:1 starting-pose
# template from ~/legv2), then press ZERO. After that, move the waldo.
from machine import ADC, Pin, PWM
import time

# --- Measured on the ch2/ch3 leg, 2026-09-26 (~/legv2/calibration/cal_ch23.json) ---
HIP_GAIN = -0.936    # thigh degrees per hip-servo degree
KNEE_GAIN = -0.700   # calf degrees per knee-servo degree  (the linkage ratio G)
COUPLING = -0.111    # calf degrees per hip-servo degree, knee servo held still  (X)

# The calibration measured the calf's ABSOLUTE angle (in the camera image), not the
# knee angle relative to the thigh. Our knee pot measures the RELATIVE angle, so we
# add the thigh's motion back in. If the leg's knee moves the wrong way when you only
# swing the waldo's hip, try setting this to False, and write down which one was right.
CALF_IS_ABSOLUTE = True

# Pot direction: flip to -1 if the real joint moves opposite to the waldo's.
HIP_POT_SIGN = 1
KNEE_POT_SIGN = 1

POT_RANGE_DEG = 270          # typical rotary pot; measure yours!
SERVO_ZERO = (90, 90)        # servo commands in the starting pose
SERVO_LIMITS = ((60, 120), (60, 120))  # stay well clear of the mechanical stops
MIN_US, MAX_US = 500, 2500
SMOOTH = 0.25

hip_pot, knee_pot = ADC(Pin(26)), ADC(Pin(27))
servos = [PWM(Pin(10)), PWM(Pin(11))]
for s in servos:
    s.freq(50)
zero_btn = Pin(16, Pin.IN, Pin.PULL_UP)


def pot_deg(adc):
    return adc.read_u16() / 65535 * POT_RANGE_DEG


def write_servo(i, deg):
    lo, hi = SERVO_LIMITS[i]
    deg = max(lo, min(hi, deg))
    servos[i].duty_ns(int((MIN_US + (MAX_US - MIN_US) * deg / 180) * 1000))
    return deg


def servo_angles(d_thigh, d_knee_rel):
    """Joint motions (degrees from the zero pose) -> servo commands.

    From the calibration:
        d_thigh = HIP_GAIN * d_hip_servo
        d_calf  = KNEE_GAIN * d_knee_servo + COUPLING * d_hip_servo
    Solve the first for the hip servo, then the second for the knee servo.
    """
    d_calf = d_thigh + d_knee_rel if CALF_IS_ABSOLUTE else d_knee_rel
    d_hip_servo = d_thigh / HIP_GAIN
    d_knee_servo = (d_calf - COUPLING * d_hip_servo) / KNEE_GAIN
    return SERVO_ZERO[0] + d_hip_servo, SERVO_ZERO[1] + d_knee_servo


for i in range(2):
    write_servo(i, SERVO_ZERO[i])
print("Pose both legs to match, then press ZERO.")
while zero_btn.value():
    time.sleep_ms(20)
hip_zero, knee_zero = pot_deg(hip_pot), pot_deg(knee_pot)
s_thigh = s_knee = 0.0
print("Zeroed. Go!")

last_print = time.ticks_ms()
while True:
    d_thigh = HIP_POT_SIGN * (pot_deg(hip_pot) - hip_zero)
    d_knee = KNEE_POT_SIGN * (pot_deg(knee_pot) - knee_zero)
    s_thigh += (d_thigh - s_thigh) * SMOOTH
    s_knee += (d_knee - s_knee) * SMOOTH

    hip_cmd, knee_cmd = servo_angles(s_thigh, s_knee)
    hip_out = write_servo(0, hip_cmd)
    knee_out = write_servo(1, knee_cmd)

    if time.ticks_diff(time.ticks_ms(), last_print) > 500:
        clipped = "  (LIMIT)" if (hip_out, knee_out) != (hip_cmd, knee_cmd) else ""
        print("thigh %+5.1f knee %+5.1f -> servos %5.1f %5.1f%s"
              % (s_thigh, s_knee, hip_out, knee_out, clipped))
        last_print = time.ticks_ms()
    time.sleep_ms(20)
