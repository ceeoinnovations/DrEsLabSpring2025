from machine import Pin, SoftI2C
import ssd1306
import time

# Initialize the OLED screen
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))  # Update pins if needed
screen = ssd1306.SSD1306_I2C(128, 64, i2c)

# Ball properties
ball_x = 64  # Center horizontally
ball_y = 0   # Start from top
ball_dy = 2  # Vertical speed
ball_radius = 4  # Circle radius

# Screen boundaries
width = 128
height = 64

def draw_filled_circle(x, y, r, color):
    """Draws a filled circle by plotting pixels within radius."""
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx**2 + dy**2 <= r**2:
                px = x + dx
                py = y + dy
                if 0 <= px < width and 0 <= py < height:
                    screen.pixel(px, py, color)

while True:
    screen.fill(0)  # Clear screen

    # Update vertical position
    ball_y += ball_dy

    # Improved boundary checks for full edge reach
    if ball_y <= ball_radius:
        ball_y = ball_radius  # Correct to stay within bounds
        ball_dy = -ball_dy    # Bounce

    elif ball_y >= height - ball_radius:
        ball_y = height - ball_radius  # Correct to stay within bounds
        ball_dy = -ball_dy             # Bounce

    # Draw the circle (the ball)
    draw_filled_circle(ball_x, ball_y, ball_radius, 1)
    screen.show()

    time.sleep(0.03)  # Control the speed
