import board
import digitalio
import time
import pwmio
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl  # Direct HID control
from adafruit_hid.consumer_control_code import ConsumerControlCode

# Initialize HID for Consumer Control (volume control)
consumer_control = ConsumerControl()  # Assuming you've set up USB HID in code.py

# Configure rTouch and set up PWM
button_rTouch = digitalio.DigitalInOut(board.GP22)  # Replace with actual pin
button_rTouch.direction = digitalio.Direction.INPUT
button_rTouch.pull = digitalio.Pull.UP

button_rUp = digitalio.DigitalInOut(board.GP19)  # Replace with actual pin
button_rUp.direction = digitalio.Direction.INPUT
button_rUp.pull = digitalio.Pull.UP

button_rDown = digitalio.DigitalInOut(board.GP18)  # Replace with actual pin
button_rDown.direction = digitalio.Direction.INPUT
button_rDown.pull = digitalio.Pull.UP

pwm_signal = pwmio.PWMOut(board.GP16, frequency=5000, duty_cycle=0)  # Adjust pin and frequency as needed

# Variables for mode and debounce
current_mode = 0
DEBOUNCE_DELAY = 0.1
last_touch_time = 0
last_rtouch_state = True  # Track last state of rTouch to detect transitions

# PWM step control
PWM_MIN = 1000
PWM_MAX = 65535
PWM_STEPS = 6
PWM_STEP_SIZE = (PWM_MAX - PWM_MIN) // PWM_STEPS  # Step size based on number of steps

# Set the initial PWM step (e.g., step 3 of 6)
INITIAL_PWM_STEP = 3  # This can be adjusted (0 to 5 for 6 steps)
initial_pwm_value = PWM_MIN + (INITIAL_PWM_STEP * PWM_STEP_SIZE)
pwm_signal.duty_cycle = initial_pwm_value
print(f"Initial PWM set to step {INITIAL_PWM_STEP + 1}, value: {initial_pwm_value}")

# Track state of rUp and rDown for detecting presses
last_rUp_state = True
last_rDown_state = True

def toggle_mode():
    global current_mode, last_touch_time, last_rtouch_state
    current_time = time.monotonic()
    if not button_rTouch.value and last_rtouch_state:  # Only toggle when the button is pressed
        if (current_time - last_touch_time) > DEBOUNCE_DELAY:
            current_mode = 1 - current_mode  # Toggle between 0 and 1
            print("Mode toggled to:", "Keycode Mode" if current_mode == 0 else "PWM Mode")
            last_touch_time = current_time
    last_rtouch_state = button_rTouch.value  # Update the last state

def handle_rUp_rDown():
    """Handle behavior of rUp and rDown based on the current mode."""
    global last_rUp_state, last_rDown_state
    if current_mode == 0:
        # Keycode mode
        if not button_rUp.value and last_rUp_state:  # Send keypress only when button goes low
            consumer_control.press(ConsumerControlCode.VOLUME_INCREMENT)
            print("Volume Up key pressed")
        elif button_rUp.value and not last_rUp_state:  # Detect button release
            consumer_control.release()  # Release volume increment
            print("Volume Up key released")

        if not button_rDown.value and last_rDown_state:  # Send keypress only when button goes low
            consumer_control.press(ConsumerControlCode.VOLUME_DECREMENT)
            print("Volume Down key pressed")
        elif button_rDown.value and not last_rDown_state:  # Detect button release
            consumer_control.release()  # Release volume decrement
            print("Volume Down key released")

    else:
        # PWM mode
        if not button_rUp.value and last_rUp_state:  # Increase PWM duty cycle on press
            current_pwm = pwm_signal.duty_cycle
            new_pwm = min(current_pwm + PWM_STEP_SIZE, PWM_MAX)
            pwm_signal.duty_cycle = new_pwm
            print("Increased PWM to:", pwm_signal.duty_cycle)
        
        if not button_rDown.value and last_rDown_state:  # Decrease PWM duty cycle on press
            current_pwm = pwm_signal.duty_cycle
            new_pwm = max(current_pwm - PWM_STEP_SIZE, PWM_MIN)
            pwm_signal.duty_cycle = new_pwm
            print("Decreased PWM to:", pwm_signal.duty_cycle)

    # Update last state of rUp and rDown
    last_rUp_state = button_rUp.value
    last_rDown_state = button_rDown.value
