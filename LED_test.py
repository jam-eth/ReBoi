import board
import digitalio
import time

# Set up LEDs on GPIO pins 18, 19, and 20
led_pins = [board.GP18, board.GP19, board.GP20]
leds = []

for pin in led_pins:
    led = digitalio.DigitalInOut(pin)
    led.direction = digitalio.Direction.OUTPUT
    leds.append(led)

# Define functions to turn LEDs on and off
def led_on(led_index):
    if 0 <= led_index < len(leds):
        leds[led_index].value = True
        print(f"LED {led_index + 1} is now ON")

def led_off(led_index):
    if 0 <= led_index < len(leds):
        leds[led_index].value = False
        print(f"LED {led_index + 1} is now OFF")
