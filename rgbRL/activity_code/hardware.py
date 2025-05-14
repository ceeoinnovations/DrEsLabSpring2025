"""
File: hardware.py
Authors: Amanda-Lexine Sunga (Feb 2025)
         --> Modified from original Smart Motors code
Purpose: Initialization of hardware for Smart Motor
*** For Engineering with Artificial Intelligence Pre-College Program at Tufts University ***
"""

from machine import Pin, SoftI2C
import servo, icons

# Create and return a Servo object on pin 2
def setup_servo():
    return servo.Servo(Pin(2))

# Set up the display with I2C and return display object
def setup_display():
    switch_up = Pin(10, Pin.IN)
    i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
    return icons.SSD1306_SMART(128, 64, i2c, switch_up), switch_up

# Set up and return navigation switch objects
def setup_switches():
    return {
        "up": Pin(10, Pin.IN),
        "down": Pin(8, Pin.IN),
        "select": Pin(9, Pin.IN)
    }
