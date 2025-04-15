from machine import Pin, SoftI2C
import ssd1306
import time
import math

# Initialize the OLED screen
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))  # I2C pins for SmartMotor
screen = ssd1306.SSD1306_I2C(128, 64, i2c)

# Ball properties
ball_x = 10
ball_y = 10
ball_dx = 2  # Change in x (velocity)
ball_dy = 2  # Change in y (velocity)
ball_radius = 3

# Screen boundaries
width = 128
height = 64

def draw_circle(x, y, r, color):
    """ Draws a simple circle using the midpoint circle algorithm. """
    for angle in range(0, 360, 10):  # Draw circle outline in steps of 10 degrees
        rad = math.radians(angle)
        x_pos = int(x + r * math.cos(rad))
        y_pos = int(y + r * math.sin(rad))
        screen.pixel(x_pos, y_pos, color)

while True:
    screen.fill(0)  # Clear screen

    # Update ball position
    ball_x += ball_dx
    ball_y += ball_dy

    # Collision detection with screen edges
    if ball_x - ball_radius <= 0 or ball_x + ball_radius >= width:
        ball_dx = -ball_dx  # Reverse direction on x-axis
    if ball_y - ball_radius <= 0 or ball_y + ball_radius >= height:
        ball_dy = -ball_dy  # Reverse direction on y-axis

    # Draw the ball
    draw_circle(ball_x, ball_y, ball_radius, 1)  # Draw the ball
    screen.show()  # Update display

    time.sleep(0.05)  # Control speed of animation
