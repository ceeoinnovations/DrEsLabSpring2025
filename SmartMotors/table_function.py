from machine import Pin, SoftI2C, ADC
import ssd1306
import time

def displayTable(columns, rows, selected=0):
    """
    Displays a selectable table on the SmartMotor OLED screen.

    Parameters:
    - columns (list): Column headers (e.g., ["State", "Left", "Right"])
    - rows (list of lists): Table data (e.g., [["Red", "-90", "90"], ["Green", "-45", "45"]])
    - selected (int): Initially selected row index

    Returns:
    - list: The selected row (e.g., ["Green", "-45", "45"])
    """
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

    scroll_index = 0  # Tracks the top row displayed
    max_visible_rows = 4  # Number of rows visible at a time
    previous_pot_value = -1  # Track potentiometer position
    view_mode = "table"  # Either "table" or "selected_color"

    def draw_table():
        """Redraws the table on the OLED screen with proper spacing."""
        screen.fill(0)  # Clear screen

        # Adjust column widths to fit within 128 pixels
        screen.text(f"{columns[0]:<6} {columns[1]:>4} {columns[2]:>4}", 0, 0, 1)  # Header row
        screen.hline(0, 10, 128, 1)  # Draw line under headers

        # Draw rows with adjusted spacing
        for i in range(max_visible_rows):
            row_idx = scroll_index + i
            if row_idx < len(rows):
                state, left, right = rows[row_idx]
                y_pos = (i + 1) * 12  # Position text below the header

                row_text = f"{state:<6} {left:>4} {right:>4}"  # Adjust column spacing

                if row_idx == selected:  # Highlight selected row
                    screen.fill_rect(0, y_pos, 128, 12, 1)  # Black background
                    screen.text(row_text, 0, y_pos, 0)  # White text
                else:
                    screen.text(row_text, 0, y_pos, 1)  # Normal text

        screen.show()

    def draw_selected_color():
        """Displays the selected color name on the screen."""
        screen.fill(0)  # Clear screen
        selected_color = rows[selected][0]  # Get selected color
        screen.text("Selected Color:", 10, 10, 1)
        screen.text(selected_color, 40, 30, 1)  # Display color name
        screen.show()

    # Initial display
    draw_table()

    while True:
        if view_mode == "table":
            # Read potentiometer value and smoothly update scroll position
            pot_value = pot.read()
            pot_position = int((pot_value / 4095) * (len(rows) - 1))  # Scale to table range

            # **If potentiometer moved to a new position, update selection**
            if pot_position != previous_pot_value:
                previous_pot_value = pot_position  # Store new position
                selected = pot_position  # Directly set highlight to new position

                # **Ensure scrolling happens if necessary**
                if selected >= scroll_index + max_visible_rows:
                    scroll_index = selected - max_visible_rows + 1  # Adjust scroll position

                if selected < scroll_index:
                    scroll_index = selected  # Adjust scroll position

                draw_table()  # **Update screen immediately after potentiometer movement**

            # Move highlighted selection UP (top button)
            if button_up.value() == 0:
                while button_up.value() == 0:  # Wait for button release
                    time.sleep(0.1)
                selected = max(0, selected - 1)
                if selected < scroll_index:
                    scroll_index -= 1
                draw_table()

            # Move highlighted selection DOWN (bottom button)
            if button_down.value() == 0:
                while button_down.value() == 0:  # Wait for button release
                    time.sleep(0.1)
                selected = min(len(rows) - 1, selected + 1)
                if selected >= scroll_index + max_visible_rows:
                    scroll_index += 1
                draw_table()

            # **Select button pressed – Switch to color selection screen**
            if button_select.value() == 0:
                while button_select.value() == 0:  # Wait for button release
                    time.sleep(0.1)
                view_mode = "selected_color"
                draw_selected_color()

        elif view_mode == "selected_color":
            # **Wait for one button press before returning to table view**
            while True:
                if button_select.value() == 0:  # Wait for second press
                    while button_select.value() == 0:  # Wait for button release
                        time.sleep(0.1)
                    view_mode = "table"
                    draw_table()
                    break  # Exit the loop after returning to the table


if __name__ == "__main__":
    # Define table structure
    columns = ["Color", "L", "R"]  # Shortened column names to save space
    rows = [
        ["Red", "-90", "90"],
        ["Green", "-45", "45"],
        ["Blue", "-30", "30"],
        ["Yellow", "-60", "60"],
        ["White", "-15", "15"],
        ["Black", "-120", "120"],
        ["Purple", "-75", "75"],
        ["Orange", "-50", "50"],
    ]

    # Call menu function
    selected_row = displayTable(columns, rows)

    print("You selected:", selected_row)  # Example output: ["Green", "-45", "45"]
