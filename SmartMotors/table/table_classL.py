from machine import Pin, SoftI2C, ADC
import ssd1306
import time

class SmartMotorTable:
    def __init__(self, columns, rows, selected=0):
        """Creates a selectable table on the SmartMotor OLED screen."""
        self.columns = columns
        self.rows = rows
        self.selected = selected
        self.scroll_index = 0
        self.max_visible_rows = 4
        self.previous_pot_value = -1
        self.view_mode = "table"
        self.last_update_time = time.ticks_ms()

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
        """Redraws the table on the OLED screen with proper spacing."""
        self.screen.fill(0)
        self.screen.text(f"{self.columns[0]:<6} {self.columns[1]:>4} {self.columns[2]:>4}", 0, 0, 1)
        self.screen.hline(0, 10, 128, 1)

        for i in range(self.max_visible_rows):
            row_idx = self.scroll_index + i
            if row_idx < len(self.rows):
                state, left, right = self.rows[row_idx]
                y_pos = (i + 1) * 12
                row_text = f"{state:<6} {left:>4} {right:>4}"

                if row_idx == self.selected:
                    self.screen.fill_rect(0, y_pos, 128, 12, 1)
                    self.screen.text(row_text, 0, y_pos, 0)
                else:
                    self.screen.text(row_text, 0, y_pos, 1)

        self.screen.show()

    def draw_selected_color(self):
        """Displays the selected color name on the screen."""
        self.screen.fill(0)
        selected_color = self.rows[self.selected][0]
        self.screen.text("Selected Color:", 10, 10, 1)
        self.screen.text(selected_color, 40, 30, 1)
        self.screen.show()

    def move_selection(self, direction):
        """Moves the highlighted selection and scrolls the table when needed."""
        new_selected_index = self.selected + direction

        if 0 <= new_selected_index < len(self.rows):
            self.selected = new_selected_index

            if self.selected >= self.scroll_index + self.max_visible_rows:
                self.scroll_index = self.selected - self.max_visible_rows + 1

            if self.selected < self.scroll_index:
                self.scroll_index = self.selected

            self.last_update_time = time.ticks_ms()
            self.draw_table()

    def update_right_value(self):
        """Automatically decreases the right value (R) every second while selected."""
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_update_time) >= 1000:
            self.rows[self.selected][2] = str(int(self.rows[self.selected][2]) - 1)  # Decrement R
            self.last_update_time = current_time
            self.draw_table()

    def run(self):
        """Runs the table selection interface and returns the selected row."""
        self.draw_table()

        while True:
            if self.view_mode == "table":
                # Read potentiometer to adjust selection
                pot_value = self.pot.read()
                pot_position = int((pot_value / 4095) * (len(self.rows) - 1))

                if pot_position != self.previous_pot_value:
                    self.previous_pot_value = pot_position
                    self.selected = pot_position

                    if self.selected >= self.scroll_index + self.max_visible_rows:
                        self.scroll_index = self.selected - self.max_visible_rows + 1

                    if self.selected < self.scroll_index:
                        self.scroll_index = self.selected

                    self.last_update_time = time.ticks_ms()
                    self.draw_table()

                # Automatically decrement R value every second
                self.update_right_value()

                # Handle button presses
                if self.button_up.value() == 0:
                    while self.button_up.value() == 0:
                        time.sleep(0.1)
                    self.move_selection(-1)

                if self.button_down.value() == 0:
                    while self.button_down.value() == 0:
                        time.sleep(0.1)
                    self.move_selection(1)

                if self.button_select.value() == 0:
                    while self.button_select.value() == 0:
                        time.sleep(0.1)
                    self.view_mode = "selected_color"
                    self.draw_selected_color()

            elif self.view_mode == "selected_color":
                while self.view_mode == "selected_color":
                    if self.button_select.value() == 0:
                        while self.button_select.value() == 0:
                            time.sleep(0.1)

                        self.view_mode = "table"
                        self.previous_pot_value = -1
                        self.draw_table()
                        break

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
    selected_row = menu.run()

    print("You selected:", selected_row)

