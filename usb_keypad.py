import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import time

# Initialize the keyboard
kbd = Keyboard(usb_hid.devices)

# Setup buttons (replace pins with actual GPIO)
button_A = digitalio.DigitalInOut(board.GP0)  # Other buttons
button_B = digitalio.DigitalInOut(board.GP1)
button_rUp = digitalio.DigitalInOut(board.GP21)
button_rDown = digitalio.DigitalInOut(board.GP23)
button_Up = digitalio.DigitalInOut(board.GP12)
button_Down = digitalio.DigitalInOut(board.GP15)
button_Left = digitalio.DigitalInOut(board.GP14)
button_Right = digitalio.DigitalInOut(board.GP13)
button_Start = digitalio.DigitalInOut(board.GP25)
button_Select = digitalio.DigitalInOut(board.GP24)

# Configure as inputs with pull-ups
for btn in [button_A, button_B, button_rUp, button_rDown, button_Up, button_Down, button_Left, button_Right, button_Start, button_Select]:
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP

button_states = {
    "A": {"pressed": False, "last_press_time": 0},
    "B": {"pressed": False, "last_press_time": 0},
    "rUp": {"pressed": False, "last_press_time": 0},
    "Up": {"pressed": False, "last_press_time": 0},
    "Down": {"pressed": False, "last_press_time": 0},
    "Left": {"pressed": False, "last_press_time": 0},
    "Right": {"pressed": False, "last_press_time": 0},
    "Start": {"pressed": False, "last_press_time": 0},
    "Select": {"pressed": False, "last_press_time": 0},
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
    send_key_on_press(button_Up, Keycode.UP_ARROW, "Up")
    send_key_on_press(button_Down, Keycode.DOWN_ARROW, "Down")
    send_key_on_press(button_Left, Keycode.LEFT_ARROW, "Left")
    send_key_on_press(button_Right, Keycode.RIGHT_ARROW, "Right")
    send_key_on_press(button_Start, Keycode.ENTER, "Start-Return")
    send_key_on_press(button_Select, Keycode.TAB, "Select-Tab")
    send_key_on_press(button_rUp, Keycode.VOLUME_INCREMENT, "Volume Up")
    send_key_on_press(button_rDown, Keycode.VOLUME_DECREMENT, "Volume Down")
    
    # rUp and rDown will be controlled through mode_controller based on the current mode
