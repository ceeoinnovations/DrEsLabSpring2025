from machine import Pin, SoftI2C
import ssd1306
import sensors
import time

class PointPlotter:
    def __init__(self, display, sensor, button_up, button_down, button_select):
        self.display = display
        self.sens = sensor
        self.button_up = button_up
        self.button_down = button_down
        self.button_select = button_select

        self.cursor_y = 32
        self.cursor_x = 64
        self.plotted_points = []

    def draw_best_fit_line(self):
        points = self.plotted_points
        if len(points) < 2:
            return

        n = len(points)
        sum_x = sum(p[0] for p in points)
        sum_y = sum(p[1] for p in points)
        sum_xy = sum(p[0] * p[1] for p in points)
        sum_x2 = sum(p[0] ** 2 for p in points)

        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return

        m = (n * sum_xy - sum_x * sum_y) / denominator
        b = (sum_y - m * sum_x) / n

        # Dotted best-fit line
        for x in range(0, 128):
            if x % 6 < 3:
                y = int(m * x + b)
                if 0 <= y < 64:
                    self.display.pixel(x, y, 1)

    def draw_screen(self):
        self.display.fill(0)

        # Only draw center X and Y axes
        self.display.hline(0, 32, 128, 1)  # Horizontal center line
        self.display.vline(64, 0, 64, 1)   # Vertical center line

        # Plotted points
        for x, y in self.plotted_points:
            self.display.pixel(x, y, 1)

        # Best-fit line
        self.draw_best_fit_line()

        # Cursor crosshair
        self.display.hline(self.cursor_x - 2, self.cursor_y, 5, 1)
        self.display.vline(self.cursor_x, self.cursor_y - 2, 5, 1)

        self.display.show()

    def update(self):
        point = self.sens.readpoint()
        self.cursor_x = min(127, max(0, int(point[1])))

        if not self.button_up.value():
            self.cursor_y = max(0, self.cursor_y - 1)
            self.draw_screen()
            time.sleep(0.05)

        if not self.button_down.value():
            self.cursor_y = min(63, self.cursor_y + 1)
            self.draw_screen()
            time.sleep(0.05)

        if not self.button_select.value():
            self.plotted_points.append((self.cursor_x, self.cursor_y))
            self.draw_screen()
            time.sleep(0.2)

        self.draw_screen()
        time.sleep(0.05)

# --- Main code ---
if __name__ == "__main__":
    # Display
    i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
    display = ssd1306.SSD1306_I2C(128, 64, i2c)

    # Buttons
    button_up = Pin(8, Pin.IN, Pin.PULL_UP)     # Top button = move up
    button_down = Pin(10, Pin.IN, Pin.PULL_UP)  # Bottom button = move down
    button_select = Pin(9, Pin.IN, Pin.PULL_UP) # Middle = plot

    # Sensors
    sens = sensors.SENSORS()

    # Start plotter
    plotter = PointPlotter(display, sens, button_up, button_down, button_select)

    while True:
        plotter.update()

