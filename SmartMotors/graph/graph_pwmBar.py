from machine import Pin, SoftI2C, PWM
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

# === PWM output on GPIO 20 ===
pwm = PWM(Pin(20), freq=1000)  # Use GPIO 20 for PWM output (if available)

# === Cursor and point storage ===
cursor_y = 32
plotted_points = []

# === Best-fit line calculation and drawing ===
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

    for x in range(0, 128):
        if x % 6 < 3:
            y = int(m * x + b)
            if 0 <= y < 64:
                display.pixel(x, y, 1)

# === Drawing screen with axes, points, PWM bar ===
def draw_screen(cursor_x, pwm_duty):
    display.fill(0)

    # Draw axes at (4, 60) and (4, 4)
    display.hline(4, 60, 120, 1)
    display.vline(4, 4, 56, 1)

    # Draw all plotted points as 3x3 squares
    for x, y in plotted_points:
        display.fill_rect(x - 1, y - 1, 3, 3, 1)

    # Draw best-fit line
    draw_best_fit_line(plotted_points)

    # Draw cursor crosshair
    display.hline(cursor_x - 2, cursor_y, 5, 1)
    display.vline(cursor_x, cursor_y - 2, 5, 1)

    # Draw PWM duty bar graph (right edge)
    bar_height = int((pwm_duty / 1023) * 60)
    display.fill_rect(122, 64 - bar_height, 5, bar_height, 1)

    display.show()

# === Main loop ===
while True:
    point = sens.readpoint()
    cursor_x = min(127, max(0, int(point[1])))

    # Map cursor_x (0–127) to PWM duty (0–1023)
    pwm_duty = int((cursor_x / 127) * 1023)
    pwm.duty(pwm_duty)

    # Handle vertical movement
    if not button_up.value():
        cursor_y = max(0, cursor_y - 1)
        draw_screen(cursor_x, pwm_duty)
        time.sleep(0.05)

    if not button_down.value():
        cursor_y = min(63, cursor_y + 1)
        draw_screen(cursor_x, pwm_duty)
        time.sleep(0.05)

    # Plot point
    if not switch_select.value():
        plotted_points.append((cursor_x, cursor_y))
        draw_screen(cursor_x, pwm_duty)
        time.sleep(0.2)

    draw_screen(cursor_x, pwm_duty)
    time.sleep(0.05)
