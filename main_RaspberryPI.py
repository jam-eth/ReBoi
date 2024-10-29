import time
from machine import Pin, ADC

CLK = Pin(5, Pin.OUT)
MOSI = Pin(4, Pin.OUT)
CS = Pin(3, Pin.OUT)
RST = Pin(8, Pin.OUT)
CS.on()
LED = Pin(18, Pin.OUT)
adc1 = ADC(Pin(28))
adc2 = ADC(Pin(27))
V12V_EN = Pin(11, Pin.OUT)

# Function to convert ADC reading to voltage
def adc_to_voltage(adc_value):
    return (adc_value / 65535) * 3.3  # Convert to voltage (0 to 3.3V)

# Function to read ADC values and print voltages
def read_and_print_adc():
    # Read ADC values
    adc_value1 = adc1.read_u16()
    adc_value2 = adc2.read_u16()
    
    # Convert ADC values to voltage
    voltage1 = adc_to_voltage(adc_value1)
    voltage2 = adc_to_voltage(adc_value2)
    
    # Print the voltages
    print("Voltage ADC1 (GP26): {:.3f} V".format(voltage1))
    print("Voltage ADC2 (GP27): {:.3f} V".format(voltage2))
    
    return voltage1, voltage2

def check_voltages_and_control_pin(voltage1, voltage2):
    if voltage1 > 1.5 or voltage2 > 1.5:
        V12V_EN.value(1)  # Set GP11 high
        print("GP11 set high")
    else:
        V12V_EN.value(0)  # Set GP11 low
        print("GP11 set low")

def clock_tick():
    time.sleep(0.0001)
    CLK.off()
    time.sleep(0.0001)
    CLK.on()
    time.sleep(0.0001)


def write_bit(v):
    MOSI.off() if v == 0 else MOSI.on()
    clock_tick()
    print("bit written: " + str(MOSI.value()))
 

def write_byte(v):
    for x in range(0, 8):
        write_bit(v & (0b10000000 >> x))


def write_register(register, data):
    if not isinstance(data, list):
        data = [data]
    print("data is:")
    print([data])
    CS.off()
    write_bit(0)  # register select
    write_byte(register)
    print("register written")
    print(hex(register))
    for i in range(0, len(data)):
        write_bit(1)  # register write
        write_byte(data[i])
        print("data written")
    CS.on()
    
def write_cmd(v):
    CS.off()
    write_bit(0)
    for x in range(0, 8):
        write_bit(v & (0b10000000 >> x))
    print("command written " + hex(v))
    CS.on()

def reset(): 
    time.sleep(0.001)
    RST.off()
    time.sleep(0.120)
    RST.on()
    time.sleep(0.001)
    
def disp_init():
    reset()
    write_cmd(0x01) #SW reset
    time.sleep(0.010)
    write_cmd(0x11)  #Sleep out
    time.sleep(0.010)
    write_register(0x3a, 0x60)                 #pixel format set
    write_register(0xb0, 0xc0)                 #RGB Interface Signal Control
    write_register(0xf6, [0x01, 0x00, 0x06])   #Interface Control
    write_register(0x36, 0x48)                 #BGR and mirroring
  
    write_cmd(0x29)  #Display ON

LED.on()
disp_init()
LED.off()

while True:
    voltage1, voltage2 = read_and_print_adc()  # Call the function to read and print ADC values
    time.sleep(1)  # Wait for a short period before the next reading
    check_voltages_and_control_pin(voltage1, voltage2)

# firmware/config.txt settings:

# dtoverlay=vc4-kms-dpi-generic
# dtparam=hactive=240,hfp=10,hsync=10,hbp=20
# dtparam=vactive=320,vfp=4,vsync=2,vbp=2
# dtparam=clock-frequency=7000000
# dtparam=rgb666-padhi
# dtparam=hsync-invert
# dtparam=vsync-invert
# dtparam=pixclk-invert
# #dtparam=de-invert
