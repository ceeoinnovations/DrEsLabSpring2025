# RGB Reinforcement Learning Activity
This folder holds the code needed for the 1D-Array RGB Reinforcement Learning Activity for the Engineering with Artificial Intelligence Pre-College Program.
## Purpose
Provide a hands-on activity for students using Smart Motors to explore the Reinforcement Learning algorithm in Machine Learning and experiment with different factors that affect how an agent's ability to learn from its environment.
## Files
### Activity Code
- `main.py`: Main file that combines the below files to successfully run the activity
>[!NOTE]
>Be sure to import and include the following files, which hold code for differnet aspects of the activity.
- `agent.py`: Handles behavior of agent and contains experimental variables (alpha, gamma, epsilon) that can be modified to change how the agent chooses its actions as well as computations for Q-Table.
- `environment.py`: Contains code to manage environment for agent, such as determining what color/state the sensor is on and calculations necessary for each step.
- `hardware.py`: Initializes hardware for Smart Motor (i.e. switches, display, etc.)
- `sensor_driver.py`: Contains initialization and properties of I2C RGB sensor, including how the sensor reads in the values and translates to an RGB array.
- `state.py`: Handles state/mode of Smart Motor display.
- `ui.py`: Handles selection of state/mode on display and interactions with buttons.
### Other Resources
For reference of how this activity is run, please refer to this [Master Doc.](https://docs.google.com/document/d/1am97O51nxhJtHALXA4zfBTZ1LcMTMlWCX30zijSaE38/edit?usp=sharing)

`ref.py` is also included as an initial test program in case the other files cannot be imported in the MicroPython interpreter.
