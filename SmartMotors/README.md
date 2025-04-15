### Objective
The goal of this work is to explore how we can leverage generative AI to produce code segments to run on Smart Motors. The files with _class or _function in their name can be imported to other files to create more interesting interfaces. 

### Files
The files from this work fall under five categories: testing and exploring functionality, implementing a menu, generating a table, creating a graph, and writing the startup code (in main.py). 
1. Testing and exploring functionaliity: These files test a varity of specific use cases for the Smart Motor, including ball movement and graphic generation, to better understand the capabilities of the device.
2. Menu: These files provide code for a user to select through different options of a menu. simple_menu.py allows the user to click through the different options, while updated_menu.py is more involved, with horizontal scrolling for longer menu options, menu header, and buttons to control the selected line. 
3. Table: These files were developed for the RGB Color Sensor, where the "Left" and "Right" columns describe how much the Smart Motor would have to move to land on the selected color. These values are hard-coded for now, but can be updated live. 
4. Graph: These files aim to replicate the original graph provided on startup to generate a generic graphic module. The line of best fit updates as the graph gets more data points from the user. graph_class.py plots only on the first quadrant, while graph_4quadrants.py can plot on all four quadrants. 
5. Startup code: The main.py file is run as the Smart Motor boots up. The user can simultaneously press the two side buttons to switch to the menu component, where they can select the desired mode.  
