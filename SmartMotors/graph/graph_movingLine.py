from machine import Pin, SoftI2C
import ssd1306
import sensors
import time

# === Display setup ===
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# === Button setup ===
button_up = Pin(8, Pin.IN, Pin.PULL_UP)     # Top = move up
button_down = Pin(10, Pin.IN, Pin.PULL_UP)  # Bottom = move down
switch_select = Pin(9, Pin.IN, Pin.PULL_UP) # Middle = plot

# === Sensor ===
sens = sensors.SENSORS()

# === Cursor and point storage ===
cursor_y = 32
plotted_points = []

# === Dash animation offset ===
dash_offset = 0

# === Best-fit line with animated dashes ===
def draw_best_fit_line(points):
    global dash_offset
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

    # Dashed line: draw segments with offset for animation
    dash_length = 5
    gap_length = 4
    pattern_length = dash_length + gap_length
    x = dash_offset % pattern_length

    while x < 128:
        for i in range(dash_length):
            xi = x + i
            if xi >= 128:
                break
            y = int(m * xi + b)
            if 0 <= y < 64:
                display.pixel(xi, y, 1)
        x += pattern_length

# === Drawing screen with axes and data ===
def draw_screen(cursor_x):
    display.fill(0)

    # Axes at (4, 60) and (4, 4)
    display.hline(4, 60, 120, 1)  # X-axis along bottom
    display.vline(4, 4, 56, 1)    # Y-axis along left

    # Larger plotted points
    for x, y in plotted_points:
        display.fill_rect(x - 1, y - 1, 3, 3, 1)

    # Moving dashed best-fit line
    draw_best_fit_line(plotted_points)

    # Cursor
    display.hline(cursor_x - 2, cursor_y, 5, 1)
    display.vline(cursor_x, cursor_y - 2, 5, 1)

    display.show()

# === Main loop ===
while True:
    point = sens.readpoint()
    cursor_x = min(127, max(0, int(point[1])))

    if not button_up.value():
        cursor_y = max(0, cursor_y - 1)
        draw_screen(cursor_x)
        time.sleep(0.05)

    if not button_down.value():
        cursor_y = min(63, cursor_y + 1)
        draw_screen(cursor_x)
        time.sleep(0.05)

    if not switch_select.value():
        plotted_points.append((cursor_x, cursor_y))
        draw_screen(cursor_x)
        time.sleep(0.2)

    # Advance the dash pattern for animation
    dash_offset = (dash_offset + 1) % 1000

    draw_screen(cursor_x)
    time.sleep(0.05)

