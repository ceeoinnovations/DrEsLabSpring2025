from machine import SoftI2C, Pin
import ssd1306
import time

# === Display Setup ===
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# === Graph Drawing Function ===
def draw_graph(bounds, points, cursor_pos, alphas):
    display.fill(0)
    width, height = display.width, display.height

    x_min, x_max, y_min, y_max = bounds

    def scale_x(x):
        return int((x - x_min) / (x_max - x_min) * (width - 1))

    def scale_y(y):
        return int((1 - (y - y_min) / (y_max - y_min)) * (height - 1))

    def poly(x):
        return sum(alphas[i] * (x ** i) for i in range(len(alphas)))

    # Draw axes if origin is visible
    if x_min <= 0 <= x_max:
        display.vline(scale_x(0), 0, height, 1)
    if y_min <= 0 <= y_max:
        display.hline(0, scale_y(0), width, 1)

    # Plot points
    for x, y in points:
        sx, sy = scale_x(x), scale_y(y)
        if 0 <= sx < width and 0 <= sy < height:
            display.fill_rect(sx - 1, sy - 1, 3, 3, 1)

    # Draw polynomial curve
    prev_x = scale_x(x_min)
    prev_y = scale_y(poly(x_min))
    step = (x_max - x_min) / width

    for i in range(1, width):
        x_val = x_min + i * step
        y_val = poly(x_val)
        sx = scale_x(x_val)
        sy = scale_y(y_val)
        if 0 <= sx < width and 0 <= sy < height:
            display.line(prev_x, prev_y, sx, sy, 1)
        prev_x, prev_y = sx, sy

    # Cursor crosshair
    cx, cy = scale_x(cursor_pos[0]), scale_y(cursor_pos[1])
    if 0 <= cx < width and 0 <= cy < height:
        display.hline(cx - 2, cy, 5, 1)
        display.vline(cx, cy - 2, 5, 1)

    display.show()

# === Example Usage ===

# Graph bounds (coordinate space shown on screen)
bounds = [-10, 10, -5, 5]  # x_min, x_max, y_min, y_max

# List of plotted points
points = [(-5, -2), (0, 0), (3, 4)]

# Current cursor position (could be updated live)
cursor = [2, 1]

# Polynomial coefficients for f(x) = 1 + 0.5x - 0.05x²
alphas = [1, 0.5, -0.05]

# Draw the graph
draw_graph(bounds, points, cursor, alphas)
