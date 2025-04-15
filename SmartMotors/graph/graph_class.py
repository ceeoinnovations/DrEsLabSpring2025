from machine import Pin, SoftI2C
import ssd1306
import sensors
import time

# Display setup
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# Button wiring (corrected for physical position)
button_up = Pin(8, Pin.IN, Pin.PULL_UP)     # Physical top = move up
button_down = Pin(10, Pin.IN, Pin.PULL_UP)  # Physical bottom = move down
switch_select = Pin(9, Pin.IN, Pin.PULL_UP)

# Sensor module
sens = sensors.SENSORS()

# Cursor + storage
cursor_y = 32
plotted_points = []

def draw_best_fit_line(points):
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

    # Draw dotted line across the screen
    for x in range(0, 128):
        if x % 6 < 3:
            y = int(m * x + b)
            if 0 <= y < 64:
                display.pixel(x, y, 1)

def draw_screen(cursor_x):
    display.fill(0)

    # Axes
    display.hline(4, 60, 120, 1)
    display.vline(4, 4, 56, 1)

    for x, y in plotted_points:
        display.pixel(x, y, 1)

    draw_best_fit_line(plotted_points)

    display.hline(cursor_x - 2, cursor_y, 5, 1)
    display.vline(cursor_x, cursor_y - 2, 5, 1)

    display.show()

# Main loop
while True:
    point = sens.readpoint()
    cursor_x = min(127, max(0, int(point[1])))

    # Top button = move up
    if not button_up.value():
        cursor_y = max(0, cursor_y - 1)
        draw_screen(cursor_x)
        time.sleep(0.05)  # faster response

    # Bottom button = move down
    if not button_down.value():
        cursor_y = min(63, cursor_y + 1)
        draw_screen(cursor_x)
        time.sleep(0.05)  # faster response

    # SELECT button = plot point
    if not switch_select.value():
        plotted_points.append((cursor_x, cursor_y))
        draw_screen(cursor_x)
        time.sleep(0.2)

    draw_screen(cursor_x)
    time.sleep(0.05)
