"""Tests for the car <-> brain line protocol (run anywhere: python3 -m pytest)."""
from carlink import format_command, parse_line


def test_telemetry():
    kind, t = parse_line("T 3912 68 245 0 3\n")
    assert kind == "T"
    assert (t.battery_mv, t.battery_pct, t.distance_mm, t.charging, t.mode) == (3912, 68, 245, False, 3)


def test_no_distance():
    _, t = parse_line("T 4100 93 -1 1 0")
    assert t.distance_mm is None and t.charging


def test_shutdown_and_junk():
    assert parse_line("S\n") == ("S", None)
    assert parse_line("garbage") is None
    assert parse_line("T 1 2 x 4 5") is None


def test_command_clamps_and_rounds():
    assert format_command(150, -30.6, 2) == b"C 100 -31 2\n"
