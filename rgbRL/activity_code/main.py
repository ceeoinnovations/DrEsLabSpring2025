"""
File: main.py
Authors: Chris Rogers, Milan Dahal, Tanushree Burman
Modified By: Adin Lamport, Amanda-Lexine Sunga, Amanda Yan (Aug 2024)
Purpose: MicroPython program to load Reinforcement Learning activity onto Smart Motors using I2C color sensor
*** For Engineering with Artificial Intelligence Pre-College Program at Tufts University ***
"""

from machine import Timer
import time
from files import readfile, resetlog, setprefs, resetprefs, savetolog
from prefs import log as prefs_log

from state import *
from agent import QLearningAgent
from environment import Environment
from sensor_driver import GroveI2cColorSensorV2
from hardware import setup_servo, setup_display, setup_switches
from ui import uppressed, downpressed, selectpressed, resettohome

# setting up hardware -- importing functions from other files
servo = setup_servo()
display, switch_up = setup_display()
switches = setup_switches()
sensor = GroveI2cColorSensorV2()

# initialize display state
numberofIcons = [5, 4, 2, 1, 1]  # example icon counts
highlightedIcon.extend([[0, n] for n in numberofIcons])
display.welcomemessage()

# handle different switch states -- used for different modes
def check_switch(p):
    global switch_state_up, switch_state_down, switch_state_select
    global last_switch_state_up, last_switch_state_down, last_switch_state_select
    global switched_up, switched_down, switched_select

    switch_state_up = switches["up"].value()
    switch_state_down = switches["down"].value()
    switch_state_select = switches["select"].value()

    if switch_state_up != last_switch_state_up:
        switched_up = True
    elif switch_state_down != last_switch_state_down:
        switched_down = True
    elif switch_state_select != last_switch_state_select:
        switched_select = True

    if switched_up and switch_state_up == 0:
        uppressed(display)
        switched_up = False
    elif switched_down and switch_state_down == 0:
        downpressed(display)
        switched_down = False
    elif switched_select and switch_state_select == 0:
        selectpressed()
        switched_select = False

    last_switch_state_up = switch_state_up
    last_switch_state_down = switch_state_down
    last_switch_state_select = switch_state_select

# display the battery status
def displaybatt(p):
    batterycharge = sensor.readbattery()
    display.showbattery(batterycharge)
    if LOGGING:
        savetolog(time.time(), screenID, highlightedIcon, None, points)
    return batterycharge

# set logging preferences
def setloggingmode():
    if not switches["down"].value() and not switches["up"].value() and not switches["select"].value():
        resetlog()
        setprefs()
        display.showmessage("LOG: ON")
    elif not switches["down"].value() and not switches["up"].value() and switches["select"].value():
        resetprefs()
        display.showmessage("LOG: OFF")
    return prefs_log

# read in data points from a given file
def readdatapoints():
    datapoints = readfile()
    if datapoints:
        return datapoints[-1]
    return []

# initialize timers and run main loop
def main():
    global points
    points = readdatapoints()
    if not points:
        highlightedIcon[1][0] = 1

    tim = Timer(0)
    tim.init(period=50, mode=Timer.PERIODIC, callback=check_switch)
    batt = Timer(2)
    batt.init(period=3000, mode=Timer.PERIODIC, callback=displaybatt)

    global LOGGING
    LOGGING = setloggingmode()
    display.selector(screenID, highlightedIcon[screenID][0], -1)

    # actual RL activity code:
    numStates = 8 # CHANGE THIS BASED ON HOW MANY COLORS THERE ARE
    indices = list(range(numStates))

    # collect all the different colors
    while numStates:
        r, g, b = sensor.rgb
        currAngle = 0

        # add the colors to the possible states
        if flags[1]:
            numStates -= 1
            points.append([r, g, b])
            print(f"State {len(points)-1} | Color: {points[-1]}")
            currAngle += (180//numStates)
            servo.write_angle(currAngle)
            resetflags()

    env = Environment(points, indices, servo, sensor)
    agent = QLearningAgent(env, epsilon=0.1)

    # run the episodes
    for ep in range(5): # CHANGE NUMBER BASED ON HOW MANY EPISODES
        print(f"EPISODE {ep}: Move to START state")
        while not flags[0]: pass
        time.sleep(1)
        state = env.reset()
        reward_total, step_count = 0, 0

        # run through each episode -- has 15 steps
        for t in range(15):
            print(f"TIMESTEP {t}")
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)
            agent.learn(reward, next_state)
            state = next_state
            reward_total += reward
            step_count += 1
            if done:
                print("Goal reached!")
                break

        # reset angle of servo after each episode
        servo.write_angle(180 // len(points))
        env.reset_cur_angle(180 // len(points))
        resetflags()

if __name__ == "__main__":
    main()
