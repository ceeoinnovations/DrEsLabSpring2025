from machine import Pin, SoftI2C
import ssd1306
import framebuf
import time

# === I2C Display Setup (SmartMotor / ESP32) ===
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
screen = ssd1306.SSD1306_I2C(128, 64, i2c)

# === Button Inputs ===
switch_up = Pin(10, Pin.IN, Pin.PULL_UP)     # Scroll down
switch_down = Pin(8, Pin.IN, Pin.PULL_UP)    # Scroll up

# === Helper: Sanitize text for OLED-safe characters ===
def sanitize_text(s):
    return (
        s.replace("’", "'")
         .replace("‘", "'")
         .replace("“", '"')
         .replace("”", '"')
         .replace("–", "-")
         .replace("—", "-")
         .replace("…", "...")
    )

# === Long Paragraph (Sanitized) ===
paragraph = sanitize_text(
    "Eliot walked the world. He watched the sparrows. "
    "Whispers on the wind carried him from city to city. "
    "In forgotten towns, cats held meetings, clocks ticked backward, "
    "and mirrors told stories. Eliot left only footprints shaped like question marks. "
    "Perhaps you've passed him, or perhaps you are him."
)

# === Word-Wrap the Paragraph Based on Pixel Width ===
def wrap_text(text, max_width=128, char_width=8):
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if len(test_line) * char_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

lines = wrap_text(paragraph)

# === Create Virtual FrameBuffer for All Lines ===
line_height = 10  # pixels per line
scroll_height = len(lines) * line_height
buffer = bytearray(128 * scroll_height // 8)
vscreen = framebuf.FrameBuffer(buffer, 128, scroll_height, framebuf.MONO_VLSB)

# === Render Wrapped Text into Virtual FrameBuffer ===
vscreen.fill(0)  # 🚨 Clear virtual screen buffer to prevent artifacts
for i, line in enumerate(lines):
    vscreen.text(line, 0, i * line_height)

# === Scrolling Setup ===
scroll_y = 0
max_scroll = max(0, scroll_height - 64)  # Prevent overscroll

def draw_window(offset):
    screen.fill(0)  # Clear actual OLED display
    offset = min(offset, max_scroll)  # Clamp offset
    screen.blit(vscreen, 0, -offset)
    screen.show()

draw_window(scroll_y)

# === Main Loop: Smooth Vertical Scroll ===
while True:
    if not switch_up.value():  # Scroll down
        if scroll_y < max_scroll:
            scroll_y += 2
            draw_window(scroll_y)
            time.sleep(0.05)

    if not switch_down.value():  # Scroll up
        if scroll_y > 0:
            scroll_y -= 2
            draw_window(scroll_y)
            time.sleep(0.05)
