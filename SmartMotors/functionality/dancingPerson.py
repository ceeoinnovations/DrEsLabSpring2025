from machine import Pin, SoftI2C
import ssd1306
import time

# Initialize the OLED screen
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))  # Adjust pins if needed
screen = ssd1306.SSD1306_I2C(128, 64, i2c)

# Screen boundaries
width = 128
height = 64

# Dancer properties
dancer_x = 0    # Start at the left
dancer_y = 40   # Vertical position on the screen
step = 2        # Speed of movement
frame = 0       # To cycle through dancing frames

# Stick figure dance with 4 unique frames
def draw_dancer(x, y, frame):
    """Draws a stick figure dancer at (x, y) with a given frame."""
    # Head
    draw_circle(x, y - 10, 3, 1)  # Small circle for the head

    # Body sway for dance effect
    body_sway = [0, 2, 0, -2][frame]

    # Body
    draw_line(x, y - 7, x + body_sway, y, 1)

    # Define arm and leg positions for each dance frame
    arm_positions = [
        ((-5, -5), (5, -2)),    # Frame 0: Left arm up, right down
        ((-5, -7), (5, -7)),    # Frame 1: Both arms up
        ((-5, -2), (5, -5)),    # Frame 2: Left arm down, right up
        ((-3, -6), (3, -6)),    # Frame 3: Arms neutral
    ]

    leg_positions = [
        ((-5, 7), (5, 7)),      # Frame 0: Left leg forward, right back
        ((-3, 7), (3, 7)),      # Frame 1: Neutral stance
        ((5, 7), (-5, 7)),      # Frame 2: Right leg forward, left back
        ((-3, 7), (3, 7)),      # Frame 3: Neutral stance
    ]

    # Arms
    left_arm = arm_positions[frame][0]
    right_arm = arm_positions[frame][1]
    draw_line(x, y - 5, x + left_arm[0], y + left_arm[1], 1)
    draw_line(x, y - 5, x + right_arm[0], y + right_arm[1], 1)

    # Legs
    left_leg = leg_positions[frame][0]
    right_leg = leg_positions[frame][1]
    draw_line(x + body_sway, y, x + left_leg[0], y + left_leg[1], 1)
    draw_line(x + body_sway, y, x + right_leg[0], y + right_leg[1], 1)

# Helper: Draw Circle (for head)
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

# Helper: Draw Line (for arms/legs)
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

# Main loop
while True:
    screen.fill(0)  # Clear screen

    # Draw the dancing figure
    draw_dancer(dancer_x, dancer_y, frame)

    # Update position and frame
    dancer_x += step
    frame = (frame + 1) % 4  # Cycle through 4 dance frames

    # Wrap around when reaching right edge
    if dancer_x > width + 5:
        dancer_x = -5  # Start again from left side

    # Show updated frame
    screen.show()
    time.sleep(0.15)  # Adjust speed of the dance animation
