# Tiny driver for a 16x2 (or 20x4) HD44780 LCD on a PCF8574 I2C backpack.
# Backpack wiring (the common one): P0=RS P1=RW P2=E P3=backlight P4-P7=D4-D7.
import time

_ROW_ADDR = (0x00, 0x40, 0x14, 0x54)


class LCD:
    def __init__(self, i2c, addr=0x27, cols=16, rows=2):
        self.i2c, self.addr, self.cols, self.rows = i2c, addr, cols, rows
        self.backlight = 0x08
        time.sleep_ms(50)
        for nibble in (0x30, 0x30, 0x30, 0x20):  # wake up, switch to 4-bit mode
            self._write4(nibble, 0)
            time.sleep_ms(5)
        for cmd in (0x28, 0x0C, 0x06):  # 2 lines; display on; cursor moves right
            self.command(cmd)
        self.clear()

    def _write4(self, nibble, rs):
        b = (nibble & 0xF0) | self.backlight | rs
        self.i2c.writeto(self.addr, bytes([b | 0x04, b]))  # pulse E high then low

    def _send(self, value, rs):
        self._write4(value & 0xF0, rs)
        self._write4((value << 4) & 0xF0, rs)

    def command(self, cmd):
        self._send(cmd, 0)
        if cmd in (0x01, 0x02):
            time.sleep_ms(2)

    def clear(self):
        self.command(0x01)

    def move_to(self, col, row):
        self.command(0x80 | (col + _ROW_ADDR[row]))

    def write(self, text):
        for ch in text:
            self._send(ord(ch), 1)

    def show(self, line1="", line2=""):
        """Clear and write up to two lines."""
        self.clear()
        self.write(line1[: self.cols])
        self.move_to(0, 1)
        self.write(line2[: self.cols])
