from machine import Pin, SoftI2C, ADC
import ssd1306
import time

# Setup SmartMotor OLED screen
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))  # I2C setup
screen = ssd1306.SSD1306_I2C(128, 64, i2c)

# Setup buttons
button_down = Pin(10, Pin.IN, Pin.PULL_UP)  # Moves selection down
button_up = Pin(8, Pin.IN, Pin.PULL_UP)  # Moves selection up
button_select = Pin(9, Pin.IN, Pin.PULL_UP)  # Select button under potentiometer

# Setup rotary potentiometer
pot = ADC(Pin(3))
pot.atten(ADC.ATTN_11DB)  # Full 0-3.3V range

# Define the table data (State, Left, Right)
color_states = [
    ("Red", "-90", "90"),
    ("Green", "-45", "45"),
    ("Blue", "-30", "30"),
    ("Yellow", "-60", "60"),
    ("White", "-15", "15"),
    ("Black", "-120", "120"),
    ("Purple", "-75", "75"),
    ("Orange", "-50", "50"),
]

selected_index = 0  # The currently highlighted row
scroll_index = 0    # Tracks the top row displayed
max_visible_rows = 4  # Number of rows visible at a time
previous_pot_value = 0  # To track changes in potentiometer position
view_mode = "table"  # Either "table" or "selected_color"

def display_table():
    """Displays the table on the OLED screen with frozen headers and highlighted selection."""
    screen.fill(0)  # Clear screen

    # Print the frozen column headers
    screen.text("State  Left  Right", 0, 0, 1)  # Header row
    screen.hline(0, 10, 128, 1)  # Draw a horizontal line under headers

    # Display visible rows
    for i in range(max_visible_rows):
        row = scroll_index + i
        if row < len(color_states):
            state, left, right = color_states[row]
            y_position = (i + 1) * 12  # Position text below the header

            if row == selected_index:  # Highlight the selected row
                screen.fill_rect(0, y_position, 128, 12, 1)  # Black background
                screen.text(f"{state:<6} {left:<5} {right:<5}", 0, y_position, 0)  # White text
            else:
                screen.text(f"{state:<6} {left:<5} {right:<5}", 0, y_position, 1)  # Normal text

    screen.show()

def display_selected_color():
    """Displays the selected color name on the screen."""
    screen.fill(0)  # Clear screen

    # Get the selected color
    selected_color = color_states[selected_index][0]

    # Show "Selected Color" message
    screen.text("Selected Color:", 10, 10, 1)
    screen.text(selected_color, 40, 30, 1)  # Display color name in the center

    screen.show()

def move_selection(direction):
    """Moves the highlighted selection and scrolls the table when needed."""
    global selected_index, scroll_index

    new_selected_index = selected_index + direction  # Compute new index

    if 0 <= new_selected_index < len(color_states):  # Prevent going out of bounds
        selected_index = new_selected_index

        # **If highlight moves past the last visible row, shift table up immediately**
        if selected_index >= scroll_index + max_visible_rows:
            if scroll_index < len(color_states) - max_visible_rows:  # Prevent overscrolling
                scroll_index += 1  # Shift table up

        # **If highlight moves past the first visible row, shift table down**
        if selected_index < scroll_index:
            if scroll_index > 0:
                scroll_index -= 1  # Shift table down

        display_table()  # **Now the update happens instantly after scrolling**

# Initial display
display_table()

# Main loop: Use potentiometer & buttons to scroll and move selection
while True:
    if view_mode == "table":
        # Read potentiometer value and smoothly update scroll position
        pot_value = pot.read()
        pot_position = int((pot_value / 4095) * (len(color_states) - 1))  # Scale to table range

        # **If potentiometer moved to a new position, update selection**
        if pot_position != previous_pot_value:
            previous_pot_value = pot_position  # Store new position
            selected_index = pot_position  # Directly set highlight to new position

            # **Ensure scrolling happens if necessary**
            if selected_index >= scroll_index + max_visible_rows:
                scroll_index = selected_index - max_visible_rows + 1  # Adjust scroll position

            if selected_index < scroll_index:
                scroll_index = selected_index  # Adjust scroll position

            display_table()  # **Update screen immediately after potentiometer movement**

        # Move highlighted selection UP (top button)
        if button_up.value() == 0:
            while button_up.value() == 0:  # Wait for button release
                time.sleep(0.1)
            move_selection(-1)  # Move up

        # Move highlighted selection DOWN (bottom button)
        if button_down.value() == 0:
            while button_down.value() == 0:  # Wait for button release
                time.sleep(0.1)
            move_selection(1)  # Move down

        # **Select button pressed - Switch to color selection screen**
        if button_select.value() == 0:
            while button_select.value() == 0:  # Wait for button release
                time.sleep(0.1)
            view_mode = "selected_color"
            display_selected_color()

    elif view_mode == "selected_color":
        # **Press any button to return to table view**
        if button_down.value() == 0 or button_up.value() == 0 or button_select.value() == 0:
            while button_down.value() == 0 or button_up.value() == 0 or button_select.value() == 0:
                time.sleep(0.1)
            view_mode = "table"
            display_table()
