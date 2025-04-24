from machine import Pin, SoftI2C, ADC
import ssd1306
import time

# Setup screen
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
screen = ssd1306.SSD1306_I2C(128, 64, i2c)

# Setup select button
switch_select = Pin(9, Pin.IN, Pin.PULL_UP)

# Setup rotary potentiometer
pot = ADC(Pin(3))
pot.atten(ADC.ATTN_11DB)  # Full 0-3.3V range

# Menu options
menu_items = ["Option 1", "Option 2", "Option 3", "Option 4"]
selected_index = 0

def get_pot_index():
    """Maps potentiometer value to menu index (0 to len(menu_items)-1)."""
    pot_value = pot.read()  # Read potentiometer value (0-4095)
    index = int((pot_value / 4095) * len(menu_items))  # Scale to menu range
    return min(index, len(menu_items) - 1)  # Ensure index is within bounds

def display_menu():
    """Display the menu with '>' pointing to the current selection and a steady highlight."""
    screen.fill(0)  # Clear screen
    for i, item in enumerate(menu_items):
        if i == selected_index:
            screen.fill_rect(0, i * 12, 128, 12, 1)  # Highlight background
            screen.text("> " + item, 2, i * 12, 0)  # White text on black background
        else:
            screen.text("  " + item, 2, i * 12, 1)  # Normal text
    screen.show()

def display_selected_option():
    """Show the selected option and wait for the switch to return."""
    screen.fill(0)  # Clear screen
    screen.text("You selected:", 10, 10, 1)
    screen.text(menu_items[selected_index], 10, 30, 1)  # Show selected option
    screen.text("Press switch", 10, 50, 1)  # Instruction to return
    screen.show()

    # Wait for switch press to return
    while switch_select.value() == 1:
        time.sleep(0.1)  # Prevent CPU overuse
    while switch_select.value() == 0:
        time.sleep(0.1)  # Debounce

# Initial display
display_menu()

# Main loop
while True:
    new_index = get_pot_index()  # Get potentiometer index

    if new_index != selected_index:  # Update only when the value changes
        selected_index = new_index
        display_menu()

    # If switch is pressed, go to the selected option page
    if switch_select.value() == 0:  # Button is pressed (active low)
        while switch_select.value() == 0:
            time.sleep(0.1)  # Debounce
        display_selected_option()
        display_menu()  # Return to menu after switch press
