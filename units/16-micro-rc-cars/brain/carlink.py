"""Serial link between the Pi "brain" and the car's XIAO "spinal cord".

Pi  -> car   C <throttle -100..100> <steer -100..100> <flags>\\n   (send >= 10 Hz or the car stops)
car -> Pi    T <battery_mv> <battery_pct> <distance_mm or -1> <charging 0/1> <mode>\\n   (10 Hz)
car -> Pi    S\\n   battery low: shut down now (the car cuts the Pi's power ~20 s later)

The car only obeys the brain in BRAIN mode (chosen on the controller), and any
stick movement on the controller overrides the brain instantly.
"""
from __future__ import annotations

import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Callable

MODE_MANUAL, MODE_AVOID, MODE_AUTO, MODE_BRAIN = range(4)
FLAG_CLOSE_OK = 1 << 1  # docking: allow creeping up to walls, slowly


@dataclass
class Telemetry:
    battery_mv: int = 0
    battery_pct: int = 0
    distance_mm: int | None = None
    charging: bool = False
    mode: int = MODE_MANUAL
    received_at: float = 0.0  # time.monotonic() of the last update; 0 = never

    @property
    def fresh(self) -> bool:
        return self.received_at > 0 and time.monotonic() - self.received_at < 0.5


def parse_line(line: str) -> tuple[str, Telemetry | None] | None:
    """Parse one line from the car. Returns ("T", Telemetry), ("S", None) or None."""
    parts = line.strip().split()
    if parts == ["S"]:
        return "S", None
    if len(parts) == 6 and parts[0] == "T":
        try:
            mv, pct, dist, chg, mode = (int(p) for p in parts[1:])
        except ValueError:
            return None
        return "T", Telemetry(mv, pct, None if dist < 0 else dist, bool(chg), mode, time.monotonic())
    return None


def format_command(throttle: float, steer: float, flags: int = 0) -> bytes:
    t = max(-100, min(100, round(throttle)))
    s = max(-100, min(100, round(steer)))
    return f"C {t} {s} {flags}\n".encode()


def _shutdown() -> None:
    subprocess.run(["sudo", "shutdown", "-h", "now"], check=False)


class CarLink:
    def __init__(self, port: str = "/dev/serial0", baud: int = 115200,
                 on_shutdown: Callable[[], None] = _shutdown):
        import serial  # pyserial; imported here so parse_line() is testable without it

        self._ser = serial.Serial(port, baud, timeout=0.1)
        self._on_shutdown = on_shutdown
        self._lock = threading.Lock()
        self._telemetry = Telemetry()
        self._running = True
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self) -> None:
        while self._running:
            raw = self._ser.readline()
            if not raw:
                continue
            msg = parse_line(raw.decode(errors="replace"))
            if msg is None:
                continue
            kind, telem = msg
            if kind == "T":
                with self._lock:
                    self._telemetry = telem
            elif kind == "S":
                self.stop()
                self._on_shutdown()

    @property
    def telemetry(self) -> Telemetry:
        with self._lock:
            return self._telemetry

    def drive(self, throttle: float, steer: float, flags: int = 0) -> None:
        self._ser.write(format_command(throttle, steer, flags))

    def stop(self) -> None:
        self.drive(0, 0)

    def close(self) -> None:
        self.stop()
        self._running = False
        self._ser.close()
