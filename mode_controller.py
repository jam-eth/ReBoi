import board
import digitalio
import time
import pwmio
from adafruit_hid.keycode import Keycode
import usb_keypad  # to access keyboard functions

# Configure rTouch and set up PWM
button_rTouch = digitalio.DigitalInOut(board.GP22)  # Replace with actual pin
button_rTouch.direction = digitalio.Direction.INPUT
button_rTouch.pull = digitalio.Pull.UP

pwm_signal = pwmio.PWMOut(board.GP16, frequency=5000, duty_cycle=0)  # Adjust pin and frequency as needed

# Variables for mode and debounce
current_mode = 0
DEBOUNCE_DELAY = 0.1
last_touch_time = 0

def toggle_mode():
    global current_mode, last_touch_time
    current_time = time.monotonic()
    if not button_rTouch.value and (current_time - last_touch_time) > DEBOUNCE_DELAY:
        current_mode = 1 - current_mode  # Toggle between 0 and 1
        print("Mode toggled to:", "Keycode Mode" if current_mode == 0 else "PWM Mode")
        last_touch_time = current_time

def handle_rUp_rDown():
    """Handle behavior of rUp and rDown based on the current mode."""
    if current_mode == 0:
        # Keycode mode
        usb_keypad.send_key_on_press(usb_keypad.button_rUp, Keycode.UP_ARROW, "rUp")
        usb_keypad.send_key_on_press(usb_keypad.button_rDown, Keycode.DOWN_ARROW, "rDown")
    else:
        # PWM mode
        if not usb_keypad.button_rUp.value:  # Increase PWM duty cycle
            pwm_signal.duty_cycle = min(pwm_signal.duty_cycle + 1000, 65535)
            print("Increased PWM to:", pwm_signal.duty_cycle)
        elif not usb_keypad.button_rDown.value:  # Decrease PWM duty cycle
            pwm_signal.duty_cycle = max(pwm_signal.duty_cycle - 1000, 0)
            print("Decreased PWM to:", pwm_signal.duty_cycle)
