"""
File: ui.py
Authors: Amanda-Lexine Sunga (Feb 2025)
         --> Modified from original Smart Motors code
Purpose: Handles all user interface aspects of activity
*** For Engineering with Artificial Intelligence Pre-College Program at Tufts University ***
"""

import time
from state import screenID, highlightedIcon, previousIcon, lastPressed, flags

# Display icon selection change
def displayselect(display, selectedIcon):
    global screenID, highlightedIcon, lastPressed, previousIcon
    highlightedIcon[screenID][0] = (highlightedIcon[screenID][0] + selectedIcon) % highlightedIcon[screenID][1]
    display.selector(screenID, highlightedIcon[screenID][0], previousIcon)
    previousIcon = highlightedIcon[screenID][0]
    lastPressed = time.ticks_ms()

# Handle up button press
def uppressed(display, count=1):
    from state import playFlag, triggered
    playFlag = False
    time.sleep(0.05)
    if time.ticks_ms() - lastPressed > 200:
        displayselect(display, count)
    triggered = True

# Handle down button press
def downpressed(display, count=-1):
    from state import playFlag, triggered
    playFlag = False
    time.sleep(0.05)
    if time.ticks_ms() - lastPressed > 200:
        displayselect(display, count)
    triggered = True

# Handle select button press
def selectpressed():
    from state import triggered
    time.sleep(0.05)
    flags[highlightedIcon[screenID][0]] = True
    triggered = True

# Reset to home screen
def resettohome(display):
    from state import screenID, highlightedIcon, previousIcon, numberofIcons, clearscreen
    screenID = 0
    previousIcon = 0
    highlightedIcon.clear()
    for numberofIcon in numberofIcons:
        highlightedIcon.append([0, numberofIcon])
    display.selector(screenID, highlightedIcon[screenID][0], 0)
    clearscreen = True
