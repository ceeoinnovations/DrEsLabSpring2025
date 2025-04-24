from machine import Pin, SoftI2C, ADC
import ssd1306
import framebuf
import time
import math

# === OLED Setup ===
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
screen = ssd1306.SSD1306_I2C(128, 64, i2c)

# === Inputs ===
pot = ADC(Pin(3))
pot.atten(ADC.ATTN_11DB)

switch_up = Pin(10, Pin.IN, Pin.PULL_UP)
switch_down = Pin(8, Pin.IN, Pin.PULL_UP)
switch_select = Pin(9, Pin.IN, Pin.PULL_UP)

# === Text Sanitization ===
def sanitize_text(s):
    return (
        s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
         .replace("–", "-").replace("—", "-").replace("…", "...")
    )

# === Agreement Paragraph ===
paragraph = sanitize_text(
    "By continuing, you agree to the terms and conditions outlined. "
    "This agreement governs your use of the device, including any features "
    "and updates. Please read carefully. Use of this device implies consent. "
    "Do not proceed unless you understand and accept the responsibilities."
)

# === Word Wrapping ===
def wrap_text(text, max_width=128, char_width=8):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = current + (" " if current else "") + word
        if len(test) * char_width <= max_width:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

lines = wrap_text(paragraph)
line_height = 10
content_height = len(lines) * line_height
scroll_height = int(math.ceil(content_height / 8) * 8) + 16

buffer = bytearray(128 * scroll_height // 8)
vscreen = framebuf.FrameBuffer(buffer, 128, scroll_height, framebuf.MONO_VLSB)

# === Render Text and Buttons in vscreen ===
vscreen.fill(0)
for i, line in enumerate(lines):
    vscreen.text(line, 0, i * line_height)
vscreen.rect(5, scroll_height - 12, 56, 10, 1)
vscreen.text("Accept", 9, scroll_height - 11)
vscreen.rect(67, scroll_height - 12, 56, 10, 1)
vscreen.text("Reject", 71, scroll_height - 11)

# === Scroll State ===
scroll_y = 0
last_scroll_y = -1
max_scroll = max(0, scroll_height - 64)
selection = 0  # 0 = Accept, 1 = Reject
paused = False
last_press_time = 0

# === Draw Function ===
def draw_window(offset):
    screen.fill(0)
    offset = min(offset, max_scroll)
    screen.blit(vscreen, 0, -offset)

    if offset >= max_scroll:
        if selection == 0:
            screen.fill_rect(5, 52, 56, 10, 1)
            screen.rect(67, 52, 56, 10, 1)
            screen.text("Accept", 9, 53, 0)
            screen.text("Reject", 71, 53, 1)
        else:
            screen.rect(5, 52, 56, 10, 1)
            screen.fill_rect(67, 52, 56, 10, 1)
            screen.text("Accept", 9, 53, 1)
            screen.text("Reject", 71, 53, 0)

    screen.show()

# === Confirm Selection (split message lines) ===
def confirm_selection(pin):
    global scroll_y, last_scroll_y, paused, last_press_time

    # Disable interrupt
    switch_select.irq(handler=None)

    now = time.ticks_ms()
    if time.ticks_diff(now, last_press_time) < 300:
        switch_select.irq(trigger=Pin.IRQ_FALLING, handler=confirm_selection)
        return
    last_press_time = now

    paused = True
    screen.fill(0)

    screen.text("You selected", 20, 24)
    if selection == 0:
        screen.text("Accept.", 40, 40)
    else:
        screen.text("Reject.", 40, 40)

    screen.show()
    time.sleep(2)

    draw_window(scroll_y)
    last_scroll_y = -1
    paused = False

    # Re-enable interrupt
    switch_select.irq(trigger=Pin.IRQ_FALLING, handler=confirm_selection)

# === Attach IRQ handler ===
switch_select.irq(trigger=Pin.IRQ_FALLING, handler=confirm_selection)

# === Main Loop ===
while True:
    # Pause screen updates during confirmation
    if paused:
        while paused:
            time.sleep(0.01)
        continue

    pot_value = pot.read()
    scroll_y = int((pot_value / 4095) * max_scroll)

    if abs(scroll_y - last_scroll_y) >= 2:
        draw_window(scroll_y)
        last_scroll_y = scroll_y

    if scroll_y >= max_scroll:
        if not switch_up.value():
            selection = 0
            draw_window(scroll_y)
            time.sleep(0.2)
        if not switch_down.value():
            selection = 1
            draw_window(scroll_y)
            time.sleep(0.2)

    time.sleep(0.01)
