from machine import SoftI2C, Pin
import ssd1306
import time

# === Display Setup ===
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# === Graph Function with Axes, Tick Marks, and Zoom Support ===
def draw_polynomial_graph(data_bounds, screen_rect, points, cursor_pos, alphas):
    x_min, x_max, y_min, y_max = data_bounds
    x0, y0, w, h = screen_rect

    def scale_x(x):
        return int((x - x_min) / (x_max - x_min) * (w - 1)) + x0

    def scale_y(y):
        return int((1 - (y - y_min) / (y_max - y_min)) * (h - 1)) + y0

    def poly(x):
        return sum(alphas[i] * (x ** i) for i in range(len(alphas)))

    # Clear just the graph area
    display.fill_rect(x0, y0, w, h, 0)

    # Axes and tick marks
    axis_color = 1
    tick_length = 3

    # Y-axis and ticks
    if x_min <= 0 <= x_max:
        x_axis = scale_x(0)
        display.vline(x_axis, y0, h, axis_color)
        tick_step_y = 1
        y_tick = (int(y_min // tick_step_y) + 1) * tick_step_y
        while y_tick < y_max:
            ty = scale_y(y_tick)
            if y0 <= ty <= y0 + h:
                display.hline(x_axis - tick_length // 2, ty, tick_length, axis_color)
            y_tick += tick_step_y

    # X-axis and ticks
    if y_min <= 0 <= y_max:
        y_axis = scale_y(0)
        display.hline(x0, y_axis, w, axis_color)
        tick_step_x = 1
        x_tick = (int(x_min // tick_step_x) + 1) * tick_step_x
        while x_tick < x_max:
            tx = scale_x(x_tick)
            if x0 <= tx <= x0 + w:
                display.vline(tx, y_axis - tick_length // 2, tick_length, axis_color)
            x_tick += tick_step_x

    # Plot points
    for x, y in points:
        sx, sy = scale_x(x), scale_y(y)
        if x0 <= sx < x0 + w and y0 <= sy < y0 + h:
            display.fill_rect(sx - 1, sy - 1, 3, 3, 1)

    # Plot polynomial curve
    prev_x = scale_x(x_min)
    prev_y = scale_y(poly(x_min))
    steps = w
    step = (x_max - x_min) / steps

    for i in range(1, steps):
        x_val = x_min + i * step
        y_val = poly(x_val)
        sx = scale_x(x_val)
        sy = scale_y(y_val)
        if x0 <= sx < x0 + w and y0 <= sy < y0 + h:
            display.line(prev_x, prev_y, sx, sy, 1)
        prev_x, prev_y = sx, sy

    # Draw cursor crosshair
    cx, cy = scale_x(cursor_pos[0]), scale_y(cursor_pos[1])
    if x0 <= cx < x0 + w and y0 <= cy < y0 + h:
        display.hline(cx - 2, cy, 5, 1)
        display.vline(cx, cy - 2, 5, 1)

    display.show()

# === Example Usage: Includes Negative Region ===

# Show only the 3rd quadrant
data_bounds = [-5, 0, -5, 0]

# OLED screen-space area for drawing the graph
screen_rect = [5, 5, 60, 30]  # Top-left (5,5), size 60x30

# Data points and curve that dips below x-axis
points = [(-1.5, 2), (0, 0), (1.5, -1.5)]
cursor = [1, -1]
alphas = [1, 1, -1, 0.5]  # f(x) = -x + 0.5x²

# Draw the graph
draw_polynomial_graph(data_bounds, screen_rect, points, cursor, alphas)
