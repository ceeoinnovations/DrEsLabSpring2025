"""
File: state.py
Authors: Amanda-Lexine Sunga (Feb 2025)
         --> Modified from original Smart Motors code
Purpose: Manages state of Smart Motor (for display purposes)
*** For Engineering with Artificial Intelligence Pre-College Program at Tufts University ***
"""

# Screen and display state
screenID = 1
lastPressed = 0
previousIcon = 0
filenumber = 0
highlightedIcon = []
numberofIcons = []
clearscreen = False

# Time tracking
currentlocaltime = 0
oldlocaltime = 0

# Flags
flags = [False, False, False, False, False]
playFlag = False
triggered = False
LOGGING = True

# Switch states
switch_state_up = False
switch_state_down = False
switch_state_select = False

last_switch_state_up = False
last_switch_state_down = False
last_switch_state_select = False

switched_up = False
switched_down = False
switched_select = False

# RGB points list
points = []
oldpoint = [-1, -1]

# Unique ID for device
import ubinascii, machine
ID = ubinascii.hexlify(machine.unique_id()).decode()

# Helpers

def resetflags():
    global flags
    for i in range(len(flags)):
        flags[i] = False
