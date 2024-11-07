import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import time

# Initialize the keyboard
kbd = Keyboard(usb_hid.devices)

# Set up buttons with internal pull-up resistors
button_A = digitalio.DigitalInOut(board.D1)  # Replace D1 with actual pin
button_A.direction = digitalio.Direction.INPUT
button_A.pull = digitalio.Pull.UP

button_B = digitalio.DigitalInOut(board.D2)  # Replace D2 with actual pin
button_B.direction = digitalio.Direction.INPUT
button_B.pull = digitalio.Pull.UP

# Add more buttons as needed for other controls

# Track button states and debounce times
button_states = {
    "A": {"pressed": False, "last_press_time": 0},
    "B": {"pressed": False, "last_press_time": 0},
    # Add entries for additional buttons here
}

# Set debounce delay in seconds
DEBOUNCE_DELAY = 0.01  # 10 milliseconds

def send_key_on_press(button, keycode, state_name):
    """Send a keycode when button is pressed, and release on button release with debounce."""
    current_time = time.monotonic()

    # Check if button is pressed (LOW) and debounce time has passed
    if not button.value and not button_states[state_name]["pressed"]:
        if (current_time - button_states[state_name]["last_press_time"]) > DEBOUNCE_DELAY:
            kbd.press(keycode)
            button_states[state_name]["pressed"] = True
            button_states[state_name]["last_press_time"] = current_time

    # Check if button is released (HIGH)
    elif button.value and button_states[state_name]["pressed"]:
        kbd.release(keycode)
        button_states[state_name]["pressed"] = False
        button_states[state_name]["last_press_time"] = current_time

def check_buttons():
    """Check each button and send corresponding keycodes if pressed."""
    send_key_on_press(button_A, Keycode.A, "A")
    send_key_on_press(button_B, Keycode.B, "B")
    # Continue mapping other buttons with send_key_on_press
    # e.g., Up, Down, Left, Right, etc.
