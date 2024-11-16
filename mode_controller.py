import board
import digitalio
import time
import pwmio
from adafruit_hid.consumer_control_code import ConsumerControlCode

# Configure buttons and PWM
button_rTouch = digitalio.DigitalInOut(board.GP22)
button_rTouch.direction = digitalio.Direction.INPUT
button_rTouch.pull = digitalio.Pull.UP

button_rUp = digitalio.DigitalInOut(board.GP19)
button_rUp.direction = digitalio.Direction.INPUT
button_rUp.pull = digitalio.Pull.UP

button_rDown = digitalio.DigitalInOut(board.GP18)
button_rDown.direction = digitalio.Direction.INPUT
button_rDown.pull = digitalio.Pull.UP

pwm_signal = pwmio.PWMOut(board.GP16, frequency=5000, duty_cycle=0)

# Mode variables and debounce
current_mode = 0
DEBOUNCE_DELAY = 0.1
last_touch_time = 0
last_rtouch_state = True

PWM_MIN = 1000
PWM_MAX = 65535
PWM_STEPS = 6
PWM_STEP_SIZE = (PWM_MAX - PWM_MIN) // PWM_STEPS
INITIAL_PWM_STEP = 3
pwm_signal.duty_cycle = PWM_MIN + (INITIAL_PWM_STEP * PWM_STEP_SIZE)

last_rUp_state = True
last_rDown_state = True
consumer_control = None  # Placeholder for ConsumerControl instance

# Setup function to receive ConsumerControl instance from code.py
def setup(consumer):
    global consumer_control
    consumer_control = consumer

def toggle_mode():
    global current_mode, last_touch_time, last_rtouch_state
    current_time = time.monotonic()
    if not button_rTouch.value and last_rtouch_state:
        if (current_time - last_touch_time) > DEBOUNCE_DELAY:
            current_mode = 1 - current_mode
            print("Mode toggled to:", "Keycode Mode" if current_mode == 0 else "PWM Mode")
            last_touch_time = current_time
    last_rtouch_state = button_rTouch.value

def handle_rUp_rDown():
    global last_rUp_state, last_rDown_state
    if current_mode == 0:
        if consumer_control:
            if not button_rUp.value and last_rUp_state:
                consumer_control.press(ConsumerControlCode.VOLUME_INCREMENT)
                print("Volume Up key pressed")
            elif button_rUp.value and not last_rUp_state:
                consumer_control.release()
                print("Volume Up key released")

            if not button_rDown.value and last_rDown_state:
                consumer_control.press(ConsumerControlCode.VOLUME_DECREMENT)
                print("Volume Down key pressed")
            elif button_rDown.value and not last_rDown_state:
                consumer_control.release()
                print("Volume Down key released")

    else:
        if not button_rUp.value and last_rUp_state:
            current_pwm = pwm_signal.duty_cycle
            new_pwm = min(current_pwm + PWM_STEP_SIZE, PWM_MAX)
            pwm_signal.duty_cycle = new_pwm
            print("Increased PWM to:", pwm_signal.duty_cycle)

        if not button_rDown.value and last_rDown_state:
            current_pwm = pwm_signal.duty_cycle
            new_pwm = max(current_pwm - PWM_STEP_SIZE, PWM
