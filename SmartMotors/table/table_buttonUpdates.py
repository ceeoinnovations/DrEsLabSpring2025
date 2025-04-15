from machine import Pin, SoftI2C, ADC
import ssd1306
import time

class SmartMotorTable:
    def __init__(self, columns, rows, selected=0):
        """Creates a selectable table on the SmartMotor OLED screen."""
        self.columns = columns
        self.rows = [list(row) for row in rows]  # Convert tuples to mutable lists
        self.selected = selected
        self.scroll_index = 0
        self.max_visible_rows = 4
        self.previous_pot_value = -1  # Track last potentiometer reading
        self.editing_left = True  # Tracks whether we're modifying Left (True) or Right (False)
        self.show_editing = False  # Flag to temporarily show "Editing" mode text

        # Setup SmartMotor OLED screen
        self.i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
        self.screen = ssd1306.SSD1306_I2C(128, 64, self.i2c)

        # Setup buttons
        self.button_down = Pin(10, Pin.IN, Pin.PULL_UP)  # Used to increase/decrease based on mode
        self.button_up = Pin(8, Pin.IN, Pin.PULL_UP)  # Used to increase/decrease based on mode
        self.button_select = Pin(9, Pin.IN, Pin.PULL_UP)  # Toggles Left/Right editing

        # Setup rotary potentiometer
        self.pot = ADC(Pin(3))
        self.pot.atten(ADC.ATTN_11DB)

    def draw_table(self):
        """Redraws the table on the OLED screen with real-time updates."""
        self.screen.fill(0)

        # Always draw the header and horizontal bar
        header_text = f"{self.columns[0]:<6} {self.columns[1]:>4} {self.columns[2]:>4}"
        self.screen.text(header_text, 0, 0, 1)
        self.screen.hline(0, 10, 128, 1)  # Persistent horizontal bar under header

        # Display Editing Mode over the header (temporarily)
        if self.show_editing:
            mode_text = "Editing: L" if self.editing_left else "Editing: R"
            self.screen.fill_rect(0, 0, 128, 10, 1)  # Black out the header
            self.screen.text(mode_text, 0, 0, 0)  # White text on black background

        # Display table rows
        for i in range(self.max_visible_rows):
            row_idx = self.scroll_index + i
            if row_idx < len(self.rows):
                state, left, right = self.rows[row_idx]
                y_pos = (i + 1) * 12
                row_text = f"{state:<6} {left:>4} {right:>4}"

                if row_idx == self.selected:
                    self.screen.fill_rect(0, y_pos, 128, 12, 1)  # Highlight selected row
                    self.screen.text(row_text, 0, y_pos, 0)  # White text on black
                else:
                    self.screen.text(row_text, 0, y_pos, 1)

        self.screen.show()

    def move_selection(self, direction):
        """Moves the highlighted selection and scrolls the table when needed."""
        new_selected_index = self.selected + direction

        if 0 <= new_selected_index < len(self.rows):
            self.selected = new_selected_index

            if self.selected >= self.scroll_index + self.max_visible_rows:
                if self.scroll_index < len(self.rows) - self.max_visible_rows:
                    self.scroll_index += 1

            if self.selected < self.scroll_index:
                if self.scroll_index > 0:
                    self.scroll_index -= 1

            self.draw_table()

    def update_value(self, up_pressed):
        """Updates the Left or Right column value for the selected row."""
        if self.editing_left:
            delta = -1 if up_pressed else 1  # Top button decreases, Bottom button increases
            self.rows[self.selected][1] = str(int(self.rows[self.selected][1]) + delta)
        else:
            delta = 1 if up_pressed else -1  # Top button increases, Bottom button decreases
            self.rows[self.selected][2] = str(int(self.rows[self.selected][2]) + delta)

        self.draw_table()

    def toggle_edit_mode(self):
        """Toggles between editing Left and Right column values."""
        self.editing_left = not self.editing_left
        self.show_editing = True  # Show "Editing" mode temporarily
        self.draw_table()
        time.sleep(1)  # Show "Editing" message for 1 second
        self.show_editing = False  # Hide the message after timeout
        self.draw_table()

    def run(self):
        """Runs the table selection interface with potentiometer and button input."""
        self.draw_table()

        while True:
            # Use potentiometer to scroll up/down
            pot_value = self.pot.read()
            pot_position = int((pot_value / 4095) * (len(self.rows) - 1))

            if pot_position != self.previous_pot_value:
                self.previous_pot_value = pot_position
                self.selected = pot_position

                if self.selected >= self.scroll_index + self.max_visible_rows:
                    self.scroll_index = self.selected - self.max_visible_rows + 1

                if self.selected < self.scroll_index:
                    self.scroll_index = self.selected

                self.draw_table()

            # Modify value based on button press
            if self.button_up.value() == 0:
                while self.button_up.value() == 0:
                    time.sleep(0.1)
                self.update_value(True)  # Top button pressed

            if self.button_down.value() == 0:
                while self.button_down.value() == 0:
                    time.sleep(0.1)
                self.update_value(False)  # Bottom button pressed

            # Toggle Left/Right column when select button is pressed
            if self.button_select.value() == 0:
                while self.button_select.value() == 0:
                    time.sleep(0.1)
                self.toggle_edit_mode()  # Switch between Left/Right editing

# --- Run as a standalone script for testing ---
if __name__ == "__main__":
    columns = ["Color", "L", "R"]
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

    menu = SmartMotorTable(columns, rows)
    menu.run()
