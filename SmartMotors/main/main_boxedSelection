from machine import Pin, SoftI2C, PWM, ADC
import time
import machine
import ssd1306
from files import *

# === Input Pins ===
switch_down = Pin(8, Pin.IN, Pin.PULL_UP)
switch_select = Pin(9, Pin.IN, Pin.PULL_UP)
switch_up = Pin(10, Pin.IN, Pin.PULL_UP)

# === OLED and I2C Setup ===
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
screen = ssd1306.SSD1306_I2C(128, 64, i2c)

# === Potentiometer for horizontal scroll ===
pot = ADC(Pin(3))
pot.atten(ADC.ATTN_11DB)

# === Menu Items and UI State ===
menu_items = [
    "Standalone",
    "Web Connect",
    "This is a long menu item that should scroll horizontally",
    "Exit"
]
selected_index = 0
scroll_index = 0
max_visible_items = 3
row_height = 16
line_width_chars = 16  # ~96 pixels wide
scroll_offset_chars = 0

# === UI Helpers ===
def flash_message(msg, duration=0.3):
    screen.fill(0)
    screen.text(msg, 10, 25, 1)
    screen.show()
    time.sleep(duration)

# === Scroll Update from Potentiometer ===
def update_scroll():
    global scroll_offset_chars
    label = menu_items[selected_index] + "    "
    max_offset = max(len(label) - line_width_chars, 0)

    if max_offset == 0:
        scroll_offset_chars = 0
        return

    pot_value = pot.read()
    normalized = pot_value / 4095
    scroll_offset_chars = int(normalized * max_offset)
    scroll_offset_chars = min(scroll_offset_chars, max_offset)

# === Display Menu with Scroll Bar and Highlight Box ===
def display_menu():
    screen.fill(0)
    screen.text("Choose Mode", 25, 0, 1)
    screen.hline(0, 10, 128, 1)

    for i in range(max_visible_items):
        idx = scroll_index + i
        if idx >= len(menu_items):
            break

        y = 12 + i * row_height
        raw_label = str(menu_items[idx])
        padded_label = raw_label + "    "

        if idx == selected_index:
            # Draw an outlined rectangle (transparent look)
            screen.rect(0, y, 128, row_height, 1)
            max_offset = max(len(padded_label) - line_width_chars, 0)
            scroll_safe = min(scroll_offset_chars, max_offset)
            visible = padded_label[scroll_safe:scroll_safe + line_width_chars]
            screen.text("> " + visible, 0, y, 1)  # White text inside outline
        else:
            visible = raw_label[:line_width_chars]
            if len(visible) < line_width_chars:
                visible += " " * (line_width_chars - len(visible))
            screen.text("  " + visible, 0, y, 1)

    # === Draw vertical scroll bar (2 pixels wide) ===
    if len(menu_items) > max_visible_items:
        menu_area_height = max_visible_items * row_height
        scroll_bar_height = int(menu_area_height * (max_visible_items / len(menu_items)))
        scroll_bar_y = 12 + int((menu_area_height - scroll_bar_height) * (scroll_index / max(len(menu_items) - max_visible_items, 1)))
        scroll_bar_x = 126

        screen.vline(scroll_bar_x, 12, menu_area_height, 0)
        screen.vline(scroll_bar_x + 1, 12, menu_area_height, 0)
        screen.fill_rect(scroll_bar_x, scroll_bar_y, 2, scroll_bar_height, 1)

    screen.show()

# === Move selection up/down ===
def move_selection(direction):
    global selected_index, scroll_index, scroll_offset_chars
    new_index = selected_index + direction
    if 0 <= new_index < len(menu_items):
        selected_index = new_index
        scroll_offset_chars = 0
        if selected_index >= scroll_index + max_visible_items:
            scroll_index = selected_index - max_visible_items + 1
        elif selected_index < scroll_index:
            scroll_index = selected_index

# === SET MODE (Edge-detection logic) ===
def setmode():
    mode = 0
    prev_up = 1
    prev_down = 1
    prev_select = 1

    while True:
        current_up = switch_up.value()
        current_down = switch_down.value()
        current_select = switch_select.value()

        if prev_up == 1 and current_up == 0:
            move_selection(1)

        if prev_down == 1 and current_down == 0:
            move_selection(-1)

        if prev_select == 1 and current_select == 0:
            selection = str(menu_items[selected_index])
            flash_message("Selected: " + selection, 1)

            if selection == "Standalone":
                return 0
            elif selection == "Web Connect":
                return 1
            elif "scroll" in selection:
                return 2
            elif selection == "Exit":
                return -1

        update_scroll()
        display_menu()

        prev_up = current_up
        prev_down = current_down
        prev_select = current_select

        time.sleep(0.01)

# === Main Function ===
def main():
    print("SmartMotor booted.")
    flash_message("Welcome!", 1.5)
    mode = 0
    prev_up = 1
    prev_down = 1

    while True:
        current_up = switch_up.value()
        current_down = switch_down.value()

        # Detect combo press to enter menu
        if prev_up == 1 and current_up == 0 and prev_down == 1 and current_down == 0:
            mode = setmode()
            if mode == -1:
                flash_message("Welcome!", 1.5)
                mode = 0

        prev_up = current_up
        prev_down = current_down

        # Show active mode
        if mode == 0:
            screen.fill(0)
            screen.text("Standalone Mode", 10, 20, 1)
            screen.text("Press Select to exit", 0, 45, 1)
            screen.show()

        elif mode == 1:
            screen.fill(0)
            screen.text("Web Connect Mode", 5, 20, 1)
            screen.text("Press Select to exit", 0, 45, 1)
            screen.show()

        elif mode == 2:
            screen.fill(0)
            screen.text("Long Mode Label", 5, 20, 1)
            screen.text("Press Select to exit", 0, 45, 1)
            screen.show()

        # Select goes back to menu
        if switch_select.value() == 0:
            while switch_select.value() == 0:
                time.sleep(0.01)
            mode = setmode()
            if mode == -1:
                flash_message("Welcome!", 1.5)
                mode = 0

# === Run on Boot ===
if __name__ == "__main__":
    main()
