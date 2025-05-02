from machine import SoftI2C, Pin
import ssd1306
import time

# === Display Setup ===
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# === Buttons ===
button_up = Pin(8, Pin.IN, Pin.PULL_UP)
button_down = Pin(10, Pin.IN, Pin.PULL_UP)
button_select = Pin(9, Pin.IN, Pin.PULL_UP)

# === Graphing Function ===
def draw_graph(x_min, x_max, y_min, y_max, points, cursor_pos, alphas):
    display.fill(0)
    width, height = display.width, display.height

    def scale_x(x):
        return int((x - x_min) / (x_max - x_min) * (width - 1))

    def scale_y(y):
        return int((1 - (y - y_min) / (y_max - y_min)) * (height - 1))

    def poly(x):
        return sum(alphas[i] * (x ** i) for i in range(len(alphas)))

    # Axes
    if x_min < 0 < x_max:
        display.vline(scale_x(0), 0, height, 1)
    if y_min < 0 < y_max:
        display.hline(0, scale_y(0), width, 1)

    # Points
    for x, y in points:
        sx, sy = scale_x(x), scale_y(y)
        if 0 <= sx < width and 0 <= sy < height:
            display.fill_rect(sx - 1, sy - 1, 3, 3, 1)

    # Polynomial
    prev_x = scale_x(x_min)
    prev_y = scale_y(poly(x_min))
    step = (x_max - x_min) / width

    for i in range(1, width):
        x_val = x_min + i * step
        y_val = poly(x_val)
        sx, sy = scale_x(x_val), scale_y(y_val)
        if 0 <= sx < width and 0 <= sy < height:
            display.line(prev_x, prev_y, sx, sy, 1)
        prev_x, prev_y = sx, sy

    # Cursor
    cx, cy = scale_x(cursor_pos[0]), scale_y(cursor_pos[1])
    if 0 <= cx < width and 0 <= cy < height:
        display.hline(cx - 2, cy, 5, 1)
        display.vline(cx, cy - 2, 5, 1)

    display.show()

# === Initial State ===
x_min, x_max = -10, 10
y_min, y_max = -5, 5
points = []
cursor = [0, 0]
alphas = [1, 0.5, -0.1]  # f(x) = 1 + 0.5x - 0.1x²

def test_polynomial_graphs():
    bounds = (-10, 10, -10, 10)
    points = []
    cursor = [0, 0]  # Just for display

    test_cases = [
        ("Degree 0: f(x) = 2", [2]),                 # Constant
        ("Degree 1: f(x) = x", [0, 1]),              # Line
        ("Degree 2: f(x) = x^2", [0, 0, 1]),         # Parabola
        ("Degree 2: f(x) = -x^2", [0, 0, -1]),       # Inverted parabola
        ("Degree 3: f(x) = x^3", [0, 0, 0, 0.05]),   # Cubic curve
        ("Degree 3: f(x) = x - 0.1x^3", [0, 1, 0, -0.1]),  # Wavy cubic
    ]

    for name, alphas in test_cases:
        print("Showing:", name)
        draw_graph(*bounds, points, cursor, alphas)
        time.sleep(2)  # Pause to view each graph
        
        
test_polynomial_graphs()

