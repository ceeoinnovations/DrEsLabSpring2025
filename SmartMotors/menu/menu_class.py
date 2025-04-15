from machine import Pin, SoftI2C, ADC
import ssd1306
import time

class SmartMotorMenu:
    def __init__(self, menu_items, title="Main Menu"):
        self.menu_items = menu_items
        self.title = title

        self.selected_index = 0
        self.scroll_index = 0
        self.max_visible_items = 2
        self.row_height = 24
        self.line_width_chars = 21  # 128 / 6 = 21 chars on screen
        self.scroll_offset_chars = 0

        # OLED
        i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
        self.screen = ssd1306.SSD1306_I2C(128, 64, i2c)

        # Inputs
        self.button_up = Pin(8, Pin.IN, Pin.PULL_UP)
        self.button_down = Pin(10, Pin.IN, Pin.PULL_UP)
        self.button_select = Pin(9, Pin.IN, Pin.PULL_UP)

        # Potentiometer
        self.pot = ADC(Pin(3))
        self.pot.atten(ADC.ATTN_11DB)

    def update_scroll(self):
        label = self.menu_items[self.selected_index]
        max_offset = max(len(label) - self.line_width_chars, 0)

        if max_offset == 0:
            self.scroll_offset_chars = 0
            return

        pot_value = self.pot.read()
        normalized = pot_value / 4095
        self.scroll_offset_chars = int(normalized * max_offset)
        self.scroll_offset_chars = min(self.scroll_offset_chars, max_offset)

    def display_menu(self):
        self.screen.fill(0)
        self.screen.text(self.title, 35, 0, 1)
        self.screen.hline(0, 10, 128, 1)

        for i in range(self.max_visible_items):
            idx = self.scroll_index + i
            if idx >= len(self.menu_items):
                break

            y = 12 + i * self.row_height
            label = self.menu_items[idx]

            if idx == self.selected_index:
                self.screen.fill_rect(0, y, 128, self.row_height, 1)

                scroll_safe = min(self.scroll_offset_chars, max(len(label) - self.line_width_chars, 0))
                padded_label = label + " " * (self.line_width_chars + 1)
                visible = padded_label[scroll_safe:scroll_safe + self.line_width_chars]

                self.screen.text("> " + visible, 2, y, 0)
            else:
                visible = label[:self.line_width_chars]
                if len(visible) < self.line_width_chars:
                    visible += " " * (self.line_width_chars - len(visible))
                self.screen.text("  " + visible, 2, y, 1)

        self.screen.show()

    def move_selection(self, direction):
        new_index = self.selected_index + direction
        if 0 <= new_index < len(self.menu_items):
            self.selected_index = new_index
            self.scroll_offset_chars = 0  # Reset scroll
            if self.selected_index >= self.scroll_index + self.max_visible_items:
                self.scroll_index = self.selected_index - self.max_visible_items + 1
            elif self.selected_index < self.scroll_index:
                self.scroll_index = self.selected_index

    def display_message(self, msg):
        self.screen.fill(0)

        selected_text = self.menu_items[self.selected_index]

        # Center vertically (OLED height = 64, font height ≈ 8)
        center_y = (64 - 8) // 2

        self.screen.text(msg, 10, 10, 1)
        self.screen.text(selected_text, 10, center_y, 1)
        self.screen.text("Press switch", 10, 54, 1)
        self.screen.show()

        while self.button_select.value() == 1:
            time.sleep(0.1)
        while self.button_select.value() == 0:
            time.sleep(0.1)

    def run(self):
        self.display_menu()

        while True:
            if self.button_up.value() == 0:
                while self.button_up.value() == 0:
                    time.sleep(0.1)
                self.move_selection(-1)
                self.display_menu()

            if self.button_down.value() == 0:
                while self.button_down.value() == 0:
                    time.sleep(0.1)
                self.move_selection(1)
                self.display_menu()

            self.update_scroll()
            self.display_menu()

            if self.button_select.value() == 0:
                while self.button_select.value() == 0:
                    time.sleep(0.1)
                self.display_message("Selected:")
                self.display_menu()



menu_items = [
    "View Table",
    "This is a long menu item that should scroll left and right",
    "Settings",
    "Another long menu item that definitely requires scrolling",
    "Exit"
]

menu = SmartMotorMenu(menu_items)
menu.run()
