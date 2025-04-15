from machine import Pin, SoftI2C, ADC
import ssd1306
import time

class SmartMotorTable:
    def __init__(self, columns, rows, selected=0):
        """Creates a selectable table on the OLED screen."""
        self.columns = columns
        self.rows = rows
        self.selected = selected
        self.scroll_index = 0
        self.max_visible_rows = 4
        self.previous_pot_value = -1  # Track last potentiometer reading
        self.view_mode = "table"
        self.last_update_time = time.ticks_ms()  # Track last update time
        self.editing_left = True  # True = Editing L, False = Editing R
        self.increment_mode = True  # True = Increment, False = Decrement

        # Setup SmartMotor OLED screen
        self.i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
        self.screen = ssd1306.SSD1306_I2C(128, 64, self.i2c)

        # Setup buttons
        self.button_down = Pin(10, Pin.IN, Pin.PULL_UP)  # Toggle between L/R
        self.button_up = Pin(8, Pin.IN, Pin.PULL_UP)  # Toggle between L/R
        self.button_select = Pin(9, Pin.IN, Pin.PULL_UP)  # Toggle between increment/decrement

        # Setup rotary potentiometer
        self.pot = ADC(Pin(3))
        self.pot.atten(ADC.ATTN_11DB)

    def draw_table(self):
        """Redraws the table on the OLED screen."""
        self.screen.fill(0)

        # Draw column headers
        self.screen.text(f"{self.columns[0]:<6} {self.columns[1]:>4} {self.columns[2]:>4}", 0, 0, 1)
        self.screen.hline(0, 10, 128, 1)  # Persistent horizontal line under headers

        # Adjust row positioning
        row_start_y = 12
        row_spacing = 11

        for i in range(self.max_visible_rows):
            row_idx = self.scroll_index + i
            if row_idx < len(self.rows):
                state, left, right = self.rows[row_idx]
                y_pos = row_start_y + (i * row_spacing)
                row_text = f"{state:<6} {left:>4} {right:>4}"

                if row_idx == self.selected:
                    self.screen.fill_rect(0, y_pos, 128, row_spacing, 1)
                    self.screen.text(row_text, 0, y_pos, 0)
                else:
                    self.screen.text(row_text, 0, y_pos, 1)

        # Editing Mode display
        self.screen.hline(0, 54, 128, 1)
        mode_text = f"Editing: {'L' if self.editing_left else 'R'} ({'+' if self.increment_mode else '-'})"
        text_width = len(mode_text) * 8
        x_centered = (128 - text_width) // 2
        self.screen.text(mode_text, x_centered, 57, 1)

        self.screen.show()

    def move_selection(self):
        """Reads the potentiometer and moves the selected row exactly based on input."""
        pot_value = self.pot.read()
        new_pot_position = int((pot_value / 4095) * (len(self.rows) - 1))

        # No buffer, update immediately
        if new_pot_position != self.selected:
            self.selected = new_pot_position

            if self.selected >= self.scroll_index + self.max_visible_rows:
                self.scroll_index = self.selected - self.max_visible_rows + 1

            if self.selected < self.scroll_index:
                self.scroll_index = self.selected

            self.draw_table()

    def update_selected_value(self):
        """Automatically updates the selected column (`L` or `R`) every second based on increment mode."""
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_update_time) >= 1000:
            if self.editing_left:
                delta = -1 if self.increment_mode else 1
                self.rows[self.selected][1] = str(int(self.rows[self.selected][1]) + delta)
            else:
                delta = 1 if self.increment_mode else -1
                self.rows[self.selected][2] = str(int(self.rows[self.selected][2]) + delta)

            self.last_update_time = current_time
            self.draw_table()

    def toggle_edit_mode(self):
        """Toggles between modifying Left (L) and Right (R) values."""
        self.editing_left = not self.editing_left
        self.draw_table()

    def toggle_increment_mode(self):
        """Toggles between incrementing and decrementing values."""
        self.increment_mode = not self.increment_mode
        self.draw_table()

    def run(self):
        """Runs the table selection interface."""
        self.draw_table()

        while True:
            if self.view_mode == "table":
                self.move_selection()  # Read potentiometer instantly
                self.update_selected_value()  # Update values every second

                # Handle button presses
                if self.button_up.value() == 0:
                    while self.button_up.value() == 0:
                        time.sleep(0.1)
                    self.toggle_edit_mode()

                if self.button_down.value() == 0:
                    while self.button_down.value() == 0:
                        time.sleep(0.1)
                    self.toggle_edit_mode()

                if self.button_select.value() == 0:
                    while self.button_select.value() == 0:
                        time.sleep(0.1)
                    self.toggle_increment_mode()

# --- Run as a standalone script for testing ---
if __name__ == "__main__":
    # Define table structure
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

    # Create menu instance and run
    menu = SmartMotorTable(columns, rows)
    menu.run()
