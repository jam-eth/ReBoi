import board
import digitalio
import time
import pwmio
import usb_hid
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# Configure rTouch, rUp, rDown, and set up PWM
button_rTouch = digitalio.DigitalInOut(board.GP22)  # Replace with actual pin
button_rUp = digitalio.DigitalInOut(board.GP21)    # Replace with actual pin
button_rDown = digitalio.DigitalInOut(board.GP23)  # Replace with actual pin
button_rTouch.direction = digitalio.Direction.INPUT
button_rTouch.pull = digitalio.Pull.UP
button_rUp.direction = digitalio.Direction.INPUT
button_rUp.pull = digitalio.Pull.UP
button_rDown.direction = digitalio.Direction.INPUT
button_rDown.pull = digitalio.Pull.UP

pwm_signal = pwmio.PWMOut(board.GP16, frequency=5000, duty_cycle=0)  # Adjust pin and frequency as needed

# Initialize consumer control for volume control
consumer_ctrl = ConsumerControl(usb_hid.devices)

# Variables for mode, debounce, and release tracking
current_mode = 0
DEBOUNCE_DELAY = 0.1
last_touch_time = 0
rTouch_released = True  # Track if rTouch has been released

# Mode toggle function with release tracking to prevent multiple toggles
def toggle_mode():
    global current_mode, last_touch_time, rTouch_released
    current_time = time.monotonic()

    # Check if rTouch is pressed and was previously released
    if not button_rTouch.value and rTouch_released and (current_time - last_touch_time) > DEBOUNCE_DELAY:
        current_mode = 1 - current_mode  # Toggle between 0 and 1
        print("Mode toggled to:", "Keycode Mode" if current_mode == 0 else "PWM Mode")
        rTouch_released = False  # Indicate rTouch is now pressed
        last_touch_time = current_time

    # Update rTouch_released when the button is no longer pressed
    if button_rTouch.value:
        rTouch_released = True

# Handle rUp and rDown based on the current mode
def handle_rUp_rDown():
    """Handle behavior of rUp and rDown based on the current mode."""
    if current_mode == 0:
        # Keycode mode - send consumer commands (volume up/down)
        if not button_rUp.value:
            consumer_ctrl.press(ConsumerControlCode.VOLUME_INCREMENT)
            print("Volume Up")
        elif button_rUp.value:
            consumer_ctrl.release(ConsumerControlCode.VOLUME_INCREMENT)

        if not button_rDown.value:
            consumer_ctrl.press(ConsumerControlCode.VOLUME_DECREMENT)
            print("Volume Down")
        elif button_rDown.value:
            consumer_ctrl.release(ConsumerControlCode.VOLUME_DECREMENT)

    else:
        # PWM mode - adjust PWM duty cycle without sending consumer commands
        new_duty_cycle = pwm_signal.duty_cycle  # Track changes
        if not button_rUp.value:  # Increase PWM duty cycle
            new_duty_cycle = min(pwm_signal.duty_cycle + 1000, 65535)
        elif not button_rDown.value:  # Decrease PWM duty cycle
            new_duty_cycle = max(pwm_signal.duty_cycle - 1000, 0)
        
        # If duty cycle has changed, update and print it
        if new_duty_cycle != pwm_signal.duty_cycle:
            pwm_signal.duty_cycle = new_duty_cycle
            print("PWM duty cycle set to:", pwm_signal.duty_cycle)
