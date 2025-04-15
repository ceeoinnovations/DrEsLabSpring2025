from machine import Pin, SoftI2C
import ssd1306
import time
import math

# Initialize the OLED screen
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))  # Adjust pins if needed
screen = ssd1306.SSD1306_I2C(128, 64, i2c)

# Screen boundaries
width = 128
height = 64

# Lasso properties for 3D effect
base_lasso_radius = 15   # Base size of the lasso
lasso_speed = 0.15       # Rotation speed
depth_variation = 10     # How much the size changes for depth

# Stick figure position
cowboy_x = 64  # Center of the screen
cowboy_y = 40

# Helper: Draw Circle (for head and lasso)
def draw_circle(x0, y0, r, color):
    """Midpoint circle algorithm."""
    x = r
    y = 0
    decision_over2 = 1 - x

    while y <= x:
        screen.pixel(x0 + x, y0 + y, color)
        screen.pixel(x0 + y, y0 + x, color)
        screen.pixel(x0 - x, y0 + y, color)
        screen.pixel(x0 - y, y0 + x, color)
        screen.pixel(x0 - x, y0 - y, color)
        screen.pixel(x0 - y, y0 - x, color)
        screen.pixel(x0 + x, y0 - y, color)
        screen.pixel(x0 + y, y0 - x, color)
        y += 1
        if decision_over2 <= 0:
            decision_over2 += 2 * y + 1
        else:
            x -= 1
            decision_over2 += 2 * (y - x) + 1

# Helper: Draw Line (for arms/legs/lasso)
def draw_line(x0, y0, x1, y1, color):
    """Bresenham's line algorithm."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    while True:
        screen.pixel(x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

# Function to draw the cowboy
def draw_cowboy(x, y, lasso_angle):
    # Head
    draw_circle(x, y - 10, 3, 1)  # Head

    # Body
    draw_line(x, y - 7, x, y, 1)

    # Legs
    draw_line(x, y, x - 4, y + 7, 1)  # Left leg
    draw_line(x, y, x + 4, y + 7, 1)  # Right leg

    # Arms (one raised to spin the lasso)
    draw_line(x, y - 5, x - 5, y - 2, 1)  # Left arm
    draw_line(x, y - 5, x + 5, y - 10, 1)  # Right arm raised

    # Lasso center point (above head)
    lasso_center_x = x
    lasso_center_y = y - 15

    # 3D effect: Adjust radius based on lasso angle
    depth = math.sin(lasso_angle) * depth_variation
    lasso_radius = base_lasso_radius + depth

    # Calculate lasso loop position
    lasso_x = int(lasso_center_x + lasso_radius * math.cos(lasso_angle))
    lasso_y = int(lasso_center_y + lasso_radius * math.sin(lasso_angle))

    # Draw lasso loop with depth effect
    draw_circle(lasso_x, lasso_y, 3, 1)

    # Draw lasso rope from hand to the loop
    draw_line(x + 5, y - 10, lasso_x, lasso_y, 1)

# Main loop
lasso_angle = 0  # Starting angle for lasso rotation
while True:
    screen.fill(0)  # Clear screen

    # Draw cowboy with lasso swinging in 3D
    draw_cowboy(cowboy_x, cowboy_y, lasso_angle)

    # Update lasso angle for rotation
    lasso_angle += lasso_speed
    if lasso_angle >= 2 * math.pi:
        lasso_angle = 0  # Reset angle after full rotation

    # Show updated frame
    screen.show()
    time.sleep(0.05)  # Control animation speed
