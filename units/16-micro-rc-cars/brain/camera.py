"""Small helper: grab frames from the Pi camera as OpenCV (BGR) arrays."""
from picamera2 import Picamera2


class Camera:
    def __init__(self, width: int = 320, height: int = 240):
        self.cam = Picamera2()
        # libcamera's "RGB888" is laid out B,G,R in memory: exactly what OpenCV expects.
        config = self.cam.create_video_configuration(main={"size": (width, height), "format": "RGB888"})
        self.cam.configure(config)
        self.cam.start()

    def frame(self):
        return self.cam.capture_array()

    def close(self) -> None:
        self.cam.stop()
