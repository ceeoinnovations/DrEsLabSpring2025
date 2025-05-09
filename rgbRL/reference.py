"""
File: main.py
Authors: Chris Rogers, Milan Dahal, Tanushree Burman
Modified By: Adin Lamport, Amanda-Lexine Sunga, Amanda Yan (Aug 2024)
Purpose: MicroPython program to load Reinforcement Learning activity onto Smart Motors using I2C color sensor
*** For Engineering with Artificial Intelligence Pre-College Program at Tufts University ***
"""
from machine import Pin, SoftI2C, Timer, unique_id
from files import *
import time, ubinascii, urandom, math
import servo, icons, sensors
import machine, os, sys

# Initialize sensor object
sens = sensors.SENSORS()

# Generate a unique ID for the device
ID = ubinascii.hexlify(machine.unique_id()).decode()

# Get the number of icons for each screen
numberofIcons = [len(icons.iconFrames[i]) for i in range(len(icons.iconFrames))]  # [homescreen, trainscreen, playscreen, playthefilesscreen, settingsscreen]
highlightedIcon = []
for numberofIcon in numberofIcons:
    highlightedIcon.append([0, numberofIcon])

# Initialize variables for screen and icon states
screenID = 1
lastPressed = 0
previousIcon = 0
filenumber = 0

currentlocaltime = 0
oldlocaltime = 0

# list to hold measured rgb values
points = []

# Define all flags
flags = [False, False, False, False, False]
playFlag = False
triggered = False
LOGGING = True

# Switch states and flags
switch_state_up = False
switch_state_down = False
switch_state_select = False

last_switch_state_up = False
last_switch_state_down = False
last_switch_state_select = False

switched_up = False
switched_down = False
switched_select = False

# Main loop flags
clearscreen = False

# Define buttons, sensors, and motors
s = servo.Servo(Pin(2)) # define servo

# Navigation switches
switch_down = Pin(8, Pin.IN)
switch_select = Pin(9, Pin.IN)
switch_up = Pin(10, Pin.IN)

# I2C interface and display
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
display = icons.SSD1306_SMART(128, 64, i2c, switch_up)

# Screen and icon mappings
# SCREENID
# 0 - HOMESCREEN
# 1 - PlaySCREEN
# 2 - TrainSCREEN
# 3 - Playthefiles
# 4 - ConnectSCREEN

# Handle down button press
def downpressed(count=-1):
    global playFlag
    global triggered
    playFlag = False
    time.sleep(0.05)
    if time.ticks_ms() - lastPressed > 200:
        displayselect(count)
    triggered = True  # log file

# Handle up button press
def uppressed(count=1):
    global playFlag
    global triggered
    playFlag = False
    time.sleep(0.05)
    if time.ticks_ms() - lastPressed > 200:
        displayselect(count)
    triggered = True  # log file

# Handle icon selection display
def displayselect(selectedIcon):
    global screenID
    global highlightedIcon
    global lastPressed
    global previousIcon
    
    highlightedIcon[screenID][0] = (highlightedIcon[screenID][0] + selectedIcon) % highlightedIcon[screenID][1]
    display.selector(screenID, highlightedIcon[screenID][0], previousIcon)  # draw circle at selection position, and remove from the previous position
    previousIcon = highlightedIcon[screenID][0]
    lastPressed = time.ticks_ms()

# Handle select button press
def selectpressed():
    global flags
    global triggered
    time.sleep(0.05)
    flags[highlightedIcon[screenID][0]] = True    
    triggered = True  # log file

# Reset to home screen
def resettohome():
    global screenID
    global highlightedIcon
    global previousIcon
    global clearscreen
    screenID = 0
    previousIcon = 0
    for numberofIcon in numberofIcons:
        highlightedIcon.append([0, numberofIcon])
    display.selector(screenID, highlightedIcon[screenID][0], 0)
    clearscreen = True

# Check switch states and handle presses
def check_switch(p):
    global switch_state_up
    global switch_state_down
    global switch_state_select
    
    global switched_up
    global switched_down
    global switched_select
    
    global last_switch_state_up
    global last_switch_state_down
    global last_switch_state_select
    
    switch_state_up = switch_up.value()
    switch_state_down = switch_down.value()
    switch_state_select = switch_select.value()
         
    if switch_state_up != last_switch_state_up:
        switched_up = True
    elif switch_state_down != last_switch_state_down:
        switched_down = True
    elif switch_state_select != last_switch_state_select:
        switched_select = True
                
    if switched_up:
        if switch_state_up == 0:
            uppressed()
        switched_up = False
    elif switched_down:
        if switch_state_down == 0:
            downpressed()
        switched_down = False
    elif switched_select:
        if switch_state_select == 0:
            selectpressed()
        switched_select = False
    
    last_switch_state_up = switch_state_up
    last_switch_state_down = switch_state_down
    last_switch_state_select = switch_state_select

# Display battery status
def displaybatt(p):
    batterycharge = sens.readbattery()
    display.showbattery(batterycharge)
    if LOGGING:
        savetolog(time.time(), screenID, highlightedIcon, point, points) 
    return batterycharge

# Reset all flags
def resetflags():
    global flags
    for i in range(len(flags)):
        flags[i] = False

# Shake motor to a specific point
def shakemotor(point):
    motorpos = point[1]
    for i in range(2):
        s.write_angle(min(180, motorpos + 5))
        time.sleep(0.1)
        s.write_angle(max(0, motorpos - 5))
        time.sleep(0.1)

# Read data points from a file
def readdatapoints():
    datapoints = readfile()        
    if datapoints:
        numberofdata = len(datapoints)
        return datapoints[-1]    
    else:
        return []

# Set logging mode based on switch states
def setloggingmode():
    # Sets preference to log by default
    if not switch_down.value() and not switch_up.value() and not switch_select.value():
        resetlog()  # delete all the previous logs
        setprefs()  # sets preference file to True 
        display.showmessage("LOG: ON")
        print("resetting the log file")
        
    # Resets preference to not log by default
    if not switch_down.value() and not switch_up.value() and switch_select.value():
        resetprefs()  # resets preference file to False
        print("turn OFF the logging")
        display.showmessage("LOG: OFF")

    # Default logging mode
    if switch_down.value() and switch_up.value() and switch_select.value():
        print("default: turn ON the logging")
        
    import prefs
    return prefs.log

# Initialize points and set up timers
points = readdatapoints()
if points == []:
    highlightedIcon[1][0] = 1  # go to add if there are no data saved

# Setting up timers for switch and battery checks
tim = Timer(0)
tim.init(period=50, mode=Timer.PERIODIC, callback=check_switch)
batt = Timer(2)
batt.init(period=3000, mode=Timer.PERIODIC, callback=displaybatt)

# Display welcome message
display.welcomemessage()

LOGGING = setloggingmode()

# Setup with homescreen, starts with screenID=0
display.selector(screenID, highlightedIcon[screenID][0], -1)
oldpoint = [-1, -1]

# Color Sensors
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

### Driver for Grove I2C Color Sensor (TCS34725) ###
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

    def set_wait_time(self, t):
        pass

    @property
    def id(self):
        return self._read_byte(_ID)

    @property
    def integration_time(self):
        steps = 256 - self._read_byte(_ATIME)
        return steps * 2.4

    def set_integration_time(self, t):
        """Set the integration time of the sensor"""
        if t < 2.4:
            t = 2.4
        elif t > 614.4:
            t = 614.4
        
        steps = int(t / 2.4)
        self._integration_time = steps * 2.4
        self._write_byte(_ATIME, 256 - steps)

    @property
    def gain(self):
        """The gain control. Should be 1, 4, 16, or 60."""
        return _GAINS[self._read_byte(_CONTROL)]

    def set_gain(self, gain):
        if gain in _GAINS:
            self._write_byte(_CONTROL, _GAINS.index(gain))

    @property
    def raw(self):
        """Read RGBC registers return 16 bits red, green, blue and clear data"""

        if not self.awake:
            self.wakeup()

        while not self._valid():
            time.sleep(0.0024)

        data = tuple(self._read_word(reg) for reg in (_RDATA, _GDATA, _BDATA, _CDATA))
        return data

    @property
    def rgb(self):
        """Read the RGB color detected by the sensor. Returns a 3-tuple of red, green, blue component values as bytes (0-255)."""
        r, g, b, clear = self.raw
        if clear:
            # make sure values do not exceede 255
            r = min(255, r)
            g = min(255, g)
            b = min(255, b)
        else:
            r, g, b = 0, 0, 0
        return r, g, b

    def _valid(self):
        """Check if RGBC is valid"""
        return self._read_byte(_STATUS) & 0x01

    def _read_byte(self, address):
        command = _CMD | address
        self.i2c.writeto(self.address, bytes([command]))
        return self.i2c.readfrom(self.address, 1)[0]

    def _read_word(self, address):
        command = _CMD | _AUTO | address
        self.i2c.writeto(self.address, bytes([command]))
        data = self.i2c.readfrom(self.address, 2)
        return data[1] << 8 | data[0]

    def _write_byte(self, address, data):
        command = _CMD | address
        self.i2c.writeto(self.address, bytes([command, data]))

    def _write_word(self, address, data):
        command = _CMD | _AUTO | address
        data = [(data >> 8) & 0xFF, data & 0xFF]
        self.i2c.writeto(self.address, bytes([command] + data))

sensor = GroveI2cColorSensorV2() # create instance of sensor

### Agent Class ###
class QLearningAgent:
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.qtable = self.initialize_qtable()
        self.actions = ["LEFT", "RIGHT"]
    
    # initializes a q table with all 0s
    def initialize_qtable(self):
        table = {}
        for key, val in enumerate(self.env.states):
            qvalue = [0] * 2
            table[val] = qvalue 
        return table

    # uses EPSILON GREEDY to make an actions
    def choose_action(self, state):
        k = urandom.uniform(0, 1)
        
        if self.epsilon > k:
            print("Random action chosen")
            action = urandom.choice(self.actions)
        else:
            # Pick the best action from Q table
            actions = self.qtable[state]
            max_val = max(actions)
            indices = []
            for ind, val in enumerate(actions):
                if(val == max_val):
                    indices.append(ind)
            
            action = self.actions[urandom.choice(indices)]

        # Roll over current state, action for next step
        self.last_state = state
        self.last_action = self.actions.index(action)
        return action

    def learn(self, reward, next_state):
        predict = self.qtable[self.last_state][self.last_action]
        target = reward + self.gamma * max(self.qtable[next_state])  # Q-Learning update rule
        self.qtable[self.last_state][self.last_action] += self.alpha * (target - predict)  # Update Q value

        print(f'Reward: {reward}, Q-table: {self.qtable}')  # Print reward and Q-table after each learning step

"""
Environment class below:
    Assumes backmost state is index 0
    Assumes GOAL state is the last color on the map
"""
### Environment Class (Physically Moves Motor) ###
class Environment:
    def __init__(self, points, index):
        self.states = dict(zip(index, points))
        self.goal_state = [len(points) - 1] # change depending on goal
        self.end_state = [0, len(index)-1] # change depending on # of colors
        self.reward_default = -1 # amount for taking a step
        self.reward_goal = 10 # amount for reaching the end
        self.current_state = None
        self.action_space = ["LEFT", "RIGHT"] # goal -> move all the way left
        self.current_angle = 0
        self.angle = 180 // len(points)

    def reset(self):
        s.write_angle(self.angle) # set angle to 36 degrees
        time.sleep(2)
        self.current_state = self.nearestNeighbor(sensor.rgb)
        return self.current_state 

    def reset_cur_angle(self, reset_angle):
        self.current_angle = reset_angle

    # finds the distance between two 3d points
    def euclidean_distance(self, color1, color2):
        return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)))

    def nearestNeighbor(self, current_rgb):
        # Find the closest color
        closest_color = None
        min_distance = float('inf')
    
        for color_name, color_value in self.states.items():
            distance = self.euclidean_distance(current_rgb, color_value)
            if distance < min_distance:
                min_distance = distance
                closest_color = color_name

        print("The closest color is:", closest_color)
        return closest_color

    def step(self, action):
        # action is "LEFT" or "RIGHT"
        if action == self.action_space[0]: # if action == "LEFT":
            # one step is 36 degrees since we have 5 colors
            # can not exceede 1800 degrees
            self.current_angle = min(180, self.current_angle + self.angle)
            s.write_angle(self.current_angle)
            time.sleep(2) # Wait 2 seconds
        elif action == self.action_space[1]: # elif action == "RIGHT":
            # can move left only if the state is not the leftmost
            if(self.current_state != self.end_state[0]):
                self.current_angle = max(0, self.current_angle - self.angle)
                s.write_angle(self.current_angle)
            time.sleep(2) # Wait two seconds

        # Read current color from sensor
        self.current_state = self.nearestNeighbor(sensor.rgb)

        # Determine reward based on current color
        if self.current_state in self.goal_state:
            reward = self.reward_goal # REACHED THE END (GOAL)
            done = True
        else:
            reward = self.reward_default
            done = False

        return self.current_state, reward, done
 
def main():    
    numStates = 5       # number of colors
    indices = [i for i in range(0, numStates)]

    # read in rgb values for each state
    while numStates != 0:
        r, g, b = sensor.rgb

        if flags[1]:    # user needs to push button to log the color # user needs to push button to log the color
            numStates -= 1
            points.append([r, g, b])
            print("Current state: " + str(len(points) - 1) + " | Color added: " + str(points))
            resetflags()

    env = Environment(points, indices)

    """
    Suggestions:
    -- Change the GOAL state of the SmartMotor
    -- Change the end states of the SmartMotor
    -- Change the epsilon value
    -- Change the reward function in the Environment class
    -- How can you test your robot using the Qtable and choose only the action with the maximum qvalue? 
    """
    
    EPSILON = 0.1 
    agent = QLearningAgent(env, epsilon=EPSILON)
    
    rewards_history = []
    timesteps = []
    
    EPISODES = 5
    TIMESTEPS = 15
    
    for i in range(EPISODES):
        print("EPISODE " + str(i) + "... Waiting to reset robot to START STATE (move to Play State and press button) ")
        while not flags[0]: 
            continue
        time.sleep(1)
        rew = 0
        ti = 0
        print("Episode " + str(i) + " Beginning...")
        state = env.reset()
        for j in range(TIMESTEPS):
            print("TIMESTEP " + str(j))
            print("- Current State: " + str(env.states[state]))
            action = agent.choose_action(state)
            print("- Action chosen: " + str(action))
            new_state, reward, done = env.step(action)
            print("- New State: " + str(env.states[new_state]))
            print("- Reward: " + str(reward))
            agent.learn(reward, new_state)
            rew += reward
            state = new_state
            ti += 1
            if(done):
                print("Goal State reached... ")
                break
        s.write_angle(180 // len(points))
        env.reset_cur_angle(180 // len(points))
        rewards_history.append(rew)
        timesteps.append(ti)    
        print("- Episode " + str(i)+ " Reward total " + str(rew))
        print("- Rewards History...")
        print(rewards_history)
        print("- Timesteps History...")
        print(timesteps)
        resetflags()
        
            
if __name__ == '__main__':
    main()
