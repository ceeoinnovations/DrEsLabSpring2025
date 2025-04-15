from machine import Pin, SoftI2C, ADC
import ssd1306
import time

class SmartMotorTable:
    def __init__(self, columns, rows, selected=0):
        """Creates a selectable table on the SmartMotor OLED screen with clean bottom text."""
        self.columns = columns
        self.rows = [list(row) for row in rows]  # Convert tuples to mutable lists
        self.selected = selected
        self.scroll_index = 0
        self.max_visible_rows = 3  # Reduced to fit "Editing Mode" properly
        self.previous_pot_value = -1  # Track last potentiometer reading
        self.editing_left = True  # Tracks whether modifying Left (True) or Right (False)

        # Setup OLED screen
        self.i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
        self.screen = ssd1306.SSD1306_I2C(128, 64, self.i2c)

        # Setup buttons
        self.button_down = Pin(10, Pin.IN, Pin.PULL_UP)  
        self.button_up = Pin(8, Pin.IN, Pin.PULL_UP)  
        self.button_select = Pin(9, Pin.IN, Pin.PULL_UP)  

        # Setup rotary potentiometer
        self.pot = ADC(Pin(3))
        self.pot.atten(ADC.ATTN_11DB)

    def draw_table(self):
        """Redraws the table on the OLED screen with a clean layout."""
        self.screen.fill(0)

        # Draw header
        self.screen.text(f"{self.columns[0]:<6} {self.columns[1]:>4} {self.columns[2]:>4}", 0, 0, 1)
        self.screen.hline(0, 10, 128, 1)  

        # Draw table rows
        for i in range(self.max_visible_rows):
            row_idx = self.scroll_index + i
            if row_idx < len(self.rows):
                state, left, right = self.rows[row_idx]
                y_pos = (i + 1) * 12  # Shifted up to make room for "Editing Mode"
                row_text = f"{state:<6} {left:>4} {right:>4}"

                if row_idx == self.selected:
                    self.screen.fill_rect(0, y_pos, 128, 12, 1)  
                    self.screen.text(row_text, 0, y_pos, 0)  
                else:
                    self.screen.text(row_text, 0, y_pos, 1)

        # Create a dedicated space for "Editing Mode"
        self.screen.fill_rect(0, 46, 128, 18, 0)  # Clear area at the bottom
        self.screen.hline(0, 46, 128, 1)  # Separate table from Editing Mode
        mode_text = f"Editing: {'L' if self.editing_left else 'R'}"
        text_width = len(mode_text) * 8  
        x_centered = (128 - text_width) // 2  
        self.screen.text(mode_text, x_centered, 52, 1)  

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
            delta = -1 if up_pressed else 1  
            self.rows[self.selected][1] = str(int(self.rows[self.selected][1]) + delta)
        else:
            delta = 1 if up_pressed else -1  
            self.rows[self.selected][2] = str(int(self.rows[self.selected][2]) + delta)

        self.draw_table()

    def toggle_edit_mode(self):
        """Toggles between editing Left and Right column values."""
        self.editing_left = not self.editing_left  
        self.draw_table()  

    def run(self):
        """Runs the table selection interface."""
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
                self.update_value(True)  

            if self.button_down.value() == 0:
                while self.button_down.value() == 0:
                    time.sleep(0.1)
                self.update_value(False)  

            # Toggle Left/Right column when select button is pressed
            if self.button_select.value() == 0:
                while self.button_select.value() == 0:
                    time.sleep(0.1)
                self.toggle_edit_mode()  

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
