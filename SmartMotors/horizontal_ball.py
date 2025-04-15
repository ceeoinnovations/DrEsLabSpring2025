from machine import Pin, SoftI2C
import ssd1306
import time

# Initialize the OLED screen
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))  # Update pins if needed
screen = ssd1306.SSD1306_I2C(128, 64, i2c)

# Ball properties
ball_x = 10   # Start near the left side
ball_y = 10   # Start from near the top
ball_dx = 0   # Horizontal velocity
ball_dy = 0   # Initial vertical speed
ball_radius = 4

# Physics constants
gravity = 0.3            # Gravity pulling ball down
bounce_strength = -5     # Initial bounce velocity
horizontal_boost = 0.5   # Amount of horizontal speed added after each bounce
max_horizontal_speed = 3 # Cap horizontal speed
energy_loss_factor = 0.9 # Lose 10% height on each bounce
friction = 0.05          # Friction applied when ball stops bouncing

# Direction flag
moving_right = True  # Start by moving right

# Screen boundaries
width = 128
height = 64

# Flag to indicate when ball stops bouncing
bouncing = True

def draw_filled_circle(x, y, r, color):
    """Draws a filled circle by plotting pixels within radius."""
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx**2 + dy**2 <= r**2:
                px = int(x + dx)
                py = int(y + dy)
                if 0 <= px < width and 0 <= py < height:
                    screen.pixel(px, py, color)

while True:
    screen.fill(0)  # Clear screen

    if bouncing:
        # Apply gravity while bouncing
        ball_dy += gravity
        ball_y += ball_dy
    else:
        # Apply friction once bouncing stops
        if ball_dx > 0:
            ball_dx -= friction
            if ball_dx < 0:
                ball_dx = 0  # Prevent negative speed
        elif ball_dx < 0:
            ball_dx += friction
            if ball_dx > 0:
                ball_dx = 0  # Prevent negative speed

    # Apply horizontal velocity
    ball_x += ball_dx

    # Check for bottom collision (pogo stick effect with energy loss)
    if bouncing and ball_y + ball_radius >= height:
        ball_y = height - ball_radius  # Keep it within bounds

        # Apply energy loss to bounce strength
        bounce_strength *= energy_loss_factor
        ball_dy = bounce_strength

        # Apply horizontal acceleration smoothly
        if moving_right:
            ball_dx += horizontal_boost
        else:
            ball_dx -= horizontal_boost

        # Cap the horizontal speed
        ball_dx = max(-max_horizontal_speed, min(ball_dx, max_horizontal_speed))

        # Stop bouncing when energy is low
        if abs(bounce_strength) < 0.5:
            bouncing = False  # Start friction phase
            ball_dy = 0

    # Bounce off right wall
    if ball_x + ball_radius >= width:
        ball_x = width - ball_radius
        moving_right = False
        ball_dx = -abs(ball_dx)  # Reverse and maintain speed

    # Bounce off left wall
    elif ball_x - ball_radius <= 0:
        ball_x = ball_radius
        moving_right = True
        ball_dx = abs(ball_dx)  # Reverse and maintain speed

    # Draw the ball
    draw_filled_circle(int(ball_x), int(ball_y), ball_radius, 1)
    screen.show()

    # Stop completely if ball comes to rest
    if not bouncing and abs(ball_dx) < 0.01:
        break  # Ball has stopped moving

    time.sleep(0.03)  # Control animation speed
