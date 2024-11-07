import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import time

# Initialize the keyboard
kbd = Keyboard(usb_hid.devices)

# Setup buttons (replace pins with actual GPIO)
button_A = digitalio.DigitalInOut(board.D1)  # Other buttons
button_B = digitalio.DigitalInOut(board.D2)
button_rUp = digitalio.DigitalInOut(board.D5)
button_rDown = digitalio.DigitalInOut(board.D6)

# Configure as inputs with pull-ups
for btn in [button_A, button_B, button_rUp, button_rDown]:
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP

button_states = {
    "A": {"pressed": False, "last_press_time": 0},
    "B": {"pressed": False, "last_press_time": 0},
    "rUp": {"pressed": False, "last_press_time": 0},
    "rDown": {"pressed": False, "last_press_time": 0}
}

DEBOUNCE_DELAY = 0.01

def send_key_on_press(button, keycode, state_name):
    current_time = time.monotonic()
    if not button.value and not button_states[state_name]["pressed"]:
        if (current_time - button_states[state_name]["last_press_time"]) > DEBOUNCE_DELAY:
            kbd.press(keycode)
            button_states[state_name]["pressed"] = True
            button_states[state_name]["last_press_time"] = current_time
    elif button.value and button_states[state_name]["pressed"]:
        kbd.release(keycode)
        button_states[state_name]["pressed"] = False
        button_states[state_name]["last_press_time"] = current_time

def check_buttons():
    send_key_on_press(button_A, Keycode.A, "A")
    send_key_on_press(button_B, Keycode.B, "B")
    # rUp and rDown will be controlled through mode_controller based on the current mode
