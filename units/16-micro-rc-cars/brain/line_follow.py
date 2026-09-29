"""Brain demo 1: follow a dark tape line on a light floor with the camera.

Run on the Pi:  python3 line_follow.py
Then choose BRAIN mode on the controller. Wiggle a stick to take over at any time.
"""
import time

import cv2

from camera import Camera
from carlink import MODE_BRAIN, CarLink

SPEED = 35          # % throttle while following
KP, KD = 90.0, 25.0  # steering gains: tune these!
LOST_TIMEOUT = 0.5  # s without seeing the line -> stop
STOP_MM = 200       # stop if something is in the way


def line_offset(frame):
    """Return where the line is across the bottom of the image: -1 (left) .. +1 (right), or None."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    roi = gray[int(h * 0.65):, :]                      # only look just ahead of the car
    roi = cv2.GaussianBlur(roi, (5, 5), 0)
    _, mask = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)  # dark = line
    m = cv2.moments(mask)
    if m["m00"] < 255 * 200:                           # fewer than ~200 line pixels: lost it
        return None
    cx = m["m10"] / m["m00"]
    return (cx - w / 2) / (w / 2)


def main():
    car, cam = CarLink(), Camera()
    last_err, last_seen = 0.0, 0.0
    try:
        while True:
            t = car.telemetry
            err = line_offset(cam.frame())
            now = time.monotonic()
            if err is not None:
                last_seen = now
                steer = KP * err + KD * (err - last_err)
                last_err = err
                throttle = SPEED
            else:
                steer, throttle = 0, 0
            if now - last_seen > LOST_TIMEOUT:
                throttle = 0
            if t.distance_mm is not None and t.distance_mm < STOP_MM:
                throttle = 0
            if t.mode == MODE_BRAIN:
                car.drive(throttle, steer)
            else:
                car.stop()
            time.sleep(0.03)
    finally:
        car.close()
        cam.close()


if __name__ == "__main__":
    main()
