import usb_keypad

import time
import board
import digitalio
import analogio

# Initialize digital output pins
CLK = digitalio.DigitalInOut(board.GP5)
CLK.direction = digitalio.Direction.OUTPUT

MOSI = digitalio.DigitalInOut(board.GP4)
MOSI.direction = digitalio.Direction.OUTPUT

CS = digitalio.DigitalInOut(board.GP3)
CS.direction = digitalio.Direction.OUTPUT
CS.value = True  # Equivalent to CS.on() in MicroPython

RST = digitalio.DigitalInOut(board.GP8)
RST.direction = digitalio.Direction.OUTPUT

LED = digitalio.DigitalInOut(board.GP18)
LED.direction = digitalio.Direction.OUTPUT

V12V_EN = digitalio.DigitalInOut(board.GP11)
V12V_EN.direction = digitalio.Direction.OUTPUT

# Initialize ADC (analog input) pins
adc1 = analogio.AnalogIn(board.GP28)
adc2 = analogio.AnalogIn(board.GP27)

# Function to convert ADC reading to voltage
def adc_to_voltage(adc):
    return (adc.value / 65535) * 3.3  # Convert to voltage (0 to 3.3V)

# Function to read ADC values and print voltages
def read_and_print_adc():
    # Read ADC values
    voltage1 = adc_to_voltage(adc1)
    voltage2 = adc_to_voltage(adc2)
    
    # Print the voltages
    print("Voltage ADC1 (GP26): {:.3f} V".format(voltage1))
    print("Voltage ADC2 (GP27): {:.3f} V".format(voltage2))
    
    return voltage1, voltage2

def check_voltages_and_control_pin(voltage1, voltage2):
    if voltage1 > 1.5 or voltage2 > 1.5:
        V12V_EN.value = True  # Set GP11 high
        print("GP11 set high")
    else:
        V12V_EN.value = False  # Set GP11 low
        print("GP11 set low")

def clock_tick():
    time.sleep(0.0001)
    CLK.value = False
    time.sleep(0.0001)
    CLK.value = True
    time.sleep(0.0001)

def write_bit(v):
    MOSI.value = v == 1
    clock_tick()
    print("bit written: " + str(MOSI.value))

def write_byte(v):
    for x in range(0, 8):
        write_bit(v & (0b10000000 >> x))

def write_register(register, data):
    if not isinstance(data, list):
        data = [data]
    print("data is:")
    print([data])
    CS.value = False
    write_bit(0)  # register select
    write_byte(register)
    print("register written")
    print(hex(register))
    for i in range(0, len(data)):
        write_bit(1)  # register write
        write_byte(data[i])
        print("data written")
    CS.value = True

def write_cmd(v):
    CS.value = False
    write_bit(0)
    for x in range(0, 8):
        write_bit(v & (0b10000000 >> x))
    print("command written " + hex(v))
    CS.value = True

def reset(): 
    time.sleep(0.001)
    RST.value = False
    time.sleep(0.120)
    RST.value = True
    time.sleep(0.001)

def disp_init():
    reset()
    write_cmd(0x01)  # SW reset
    time.sleep(0.010)
    write_cmd(0x11)  # Sleep out
    time.sleep(0.010)
    write_register(0x3a, 0x60)                 # pixel format set
    write_register(0xb0, 0xc0)                 # RGB Interface Signal Control
    write_register(0xf6, [0x01, 0x00, 0x06])   # Interface Control
    write_register(0x36, 0x48)                 # BGR and mirroring
  
    write_cmd(0x29)  # Display ON

LED.value = True
disp_init()
LED.value = False

while True:
    voltage1, voltage2 = read_and_print_adc()  # Call the function to read and print ADC values
    time.sleep(1)  # Wait for a short period before the next reading
    check_voltages_and_control_pin(voltage1, voltage2)
