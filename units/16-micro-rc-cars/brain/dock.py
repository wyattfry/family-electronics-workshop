"""Brain demo 2: self-parking. Find the ArUco marker on the charging garage's back
wall, drive into the garage, and stop once the car reports it's charging.

Print marker id 0 from the 4x4_50 dictionary (see make_marker.py), about 5 cm
wide, and tape it to the garage's back wall at camera height.

Run on the Pi:  python3 dock.py     then choose BRAIN mode on the controller.
"""
import time

import cv2

from camera import Camera
from carlink import FLAG_CLOSE_OK, MODE_BRAIN, CarLink

MARKER_ID = 0
APPROACH_SPEED = 35     # far away
CREEP_SPEED = 20        # inside the garage (the car caps "close" moves at 25 %)
CREEP_SIZE = 0.25       # marker width / image width at which we slow to a creep
KP = 80.0               # steering gain
SEARCH_STEER = 70       # slow circle while looking for the marker

DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
if hasattr(cv2.aruco, "ArucoDetector"):  # OpenCV >= 4.7
    _detector = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    def detect(gray):
        return _detector.detectMarkers(gray)
else:                                     # older OpenCV (e.g. Debian's 4.6)
    _params = cv2.aruco.DetectorParameters_create()
    def detect(gray):
        return cv2.aruco.detectMarkers(gray, DICT, parameters=_params)


def find_marker(frame):
    """Return (offset -1..+1, size 0..1) of the marker, or None."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detect(gray)
    if ids is None:
        return None
    for c, i in zip(corners, ids.flatten()):
        if i == MARKER_ID:
            pts = c.reshape(4, 2)
            w = gray.shape[1]
            cx = pts[:, 0].mean()
            size = (pts[:, 0].max() - pts[:, 0].min()) / w
            return (cx - w / 2) / (w / 2), size
    return None


def main():
    car, cam = CarLink(), Camera()
    try:
        while True:
            t = car.telemetry
            if t.charging:
                car.stop()
                print(f"Docked and charging at {t.battery_pct} %")
                break
            if t.mode != MODE_BRAIN:
                car.stop()
                time.sleep(0.1)
                continue
            seen = find_marker(cam.frame())
            if seen is None:
                car.drive(CREEP_SPEED, SEARCH_STEER)          # circle slowly and look
            else:
                offset, size = seen
                speed = CREEP_SPEED if size > CREEP_SIZE else APPROACH_SPEED
                flags = FLAG_CLOSE_OK if size > CREEP_SIZE else 0
                car.drive(speed, KP * offset, flags)
            time.sleep(0.03)
    finally:
        car.close()
        cam.close()


if __name__ == "__main__":
    main()
