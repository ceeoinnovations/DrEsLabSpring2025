"""
File: sensor_driver.py
Authors: Amanda-Lexine Sunga (Feb 2025)
         --> Modified from original Smart Motors code and Seeed Studios Sensor Code
Purpose: MicroPython program to load Reinforcement Learning activity onto Smart Motors using I2C color sensor
*** For Engineering with Artificial Intelligence Pre-College Program at Tufts University ***
"""

from machine import Pin, SoftI2C
import time

# set constant bytes
_CMD = 0x80
_AUTO = 0x20

_ENABLE = 0x00
_ATIME = 0x01
_WTIME = 0x03
_AILT = 0x04
_AIHT = 0x06
_PERS = 0x0C
_CONFIG = 0x0D
_CONTROL = 0x0F
_ID = 0x12
_STATUS = 0x13
_CDATA = 0x14
_RDATA = 0x16
_GDATA = 0x18
_BDATA = 0x1A

_AIEN = 0x10
_WEN = 0x08
_AEN = 0x02
_PON = 0x01

_GAINS = (1, 4, 16, 60)

class GroveI2cColorSensorV2:
    def __init__(self, bus=None, address=0x29, scl_pin=7, sda_pin=6):
        self.address = address
        if bus is None:
            self.i2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin), freq=100000)
        else:
            self.i2c = bus

        self.awake = False

        if self.id not in (0x44, 0x4D):
            raise ValueError('Not find a Grove I2C Color Sensor V2')

        self.set_integration_time(24)
        self.set_gain(4)

    def wakeup(self):
        enable = self._read_byte(_ENABLE)
        self._write_byte(_ENABLE, enable | _PON | _AEN)
        time.sleep(0.0024)
        self.awake = True

    def sleep(self):
        enable = self._read_byte(_ENABLE)
        self._write_byte(_ENABLE, enable & ~_PON)
        self.awake = False

    def is_awake(self):
        return self._read_byte(_ENABLE) & _PON

    @property
    def id(self):
        return self._read_byte(_ID)

    @property
    def integration_time(self):
        steps = 256 - self._read_byte(_ATIME)
        return steps * 2.4

    def set_integration_time(self, t):
        t = max(2.4, min(t, 614.4))
        steps = int(t / 2.4)
        self._integration_time = steps * 2.4
        self._write_byte(_ATIME, 256 - steps)

    @property
    def gain(self):
        return _GAINS[self._read_byte(_CONTROL)]

    def set_gain(self, gain):
        if gain in _GAINS:
            self._write_byte(_CONTROL, _GAINS.index(gain))

    @property
    def raw(self):
        if not self.awake:
            self.wakeup()
        while not self._valid():
            time.sleep(0.0024)
        return tuple(self._read_word(reg) for reg in (_RDATA, _GDATA, _BDATA, _CDATA))
    
    # actual color sensing code -- still a bit wonky (refer to spreadsheet to see outputted values)
    @property
    def rgb(self):
        r, g, b, clear = self.raw

        if clear == 0:
            return 0, 0, 0

        # normalize relative to clear val
        norm_r = r / clear
        norm_g = g / clear
        norm_b = b / clear

        # scale to 0–255 space (with dynamic brightness boost)
        # boost based on how dim the scene is
        brightness_base = 255
        boost = 1.7 if clear < 1000 else 1.4 if clear < 3000 else 1.2

        r = norm_r * brightness_base * boost
        g = norm_g * brightness_base * boost
        b = norm_b * brightness_base * boost

        # apply per-channel correction matrix
        # empirically tuned values to correct red/blue/green overlap (cross-talk)
        corrected_r = 1.1 * r - 0.05 * g - 0.05 * b
        corrected_g = -0.02 * r + 1.0 * g - 0.02 * b
        corrected_b = -0.03 * r - 0.03 * g + 1.2 * b

        r = corrected_r
        g = corrected_g
        b = corrected_b

        # stretch contrast toward vivid range
        def stretch(channel, factor=1.6):
            mid = 127.5
            return (channel - mid) * factor + mid

        r = stretch(r)
        g = stretch(g)
        b = stretch(b)

        # clip to valid range
        r = int(min(255, max(0, r)))
        g = int(min(255, max(0, g)))
        b = int(min(255, max(0, b)))

        return r, g, b

    def _valid(self):
        return self._read_byte(_STATUS) & 0x01

    def _read_byte(self, address):
        self.i2c.writeto(self.address, bytes([_CMD | address]))
        return self.i2c.readfrom(self.address, 1)[0]

    def _read_word(self, address):
        self.i2c.writeto(self.address, bytes([_CMD | _AUTO | address]))
        data = self.i2c.readfrom(self.address, 2)
        return data[1] << 8 | data[0]

    def _write_byte(self, address, data):
        self.i2c.writeto(self.address, bytes([_CMD | address, data]))
