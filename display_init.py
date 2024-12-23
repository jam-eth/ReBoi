import time
import digitalio
import board

# Initialize pins
CLK = digitalio.DigitalInOut(board.GP5)  # Replace with correct pin
CLK.direction = digitalio.Direction.OUTPUT

MOSI = digitalio.DigitalInOut(board.GP4)  # Replace with correct pin
MOSI.direction = digitalio.Direction.OUTPUT

CS = digitalio.DigitalInOut(board.GP3)  # Replace with correct pin
CS.direction = digitalio.Direction.OUTPUT
CS.value = True

RST = digitalio.DigitalInOut(board.GP8)  # Replace with correct pin
RST.direction = digitalio.Direction.OUTPUT
RST.value = True

LED = digitalio.DigitalInOut(board.GP20)  # Replace with correct pin
LED.direction = digitalio.Direction.OUTPUT

def clock_tick():
    time.sleep(0.0001)
    CLK.value = False
    time.sleep(0.0001)
    CLK.value = True
    time.sleep(0.0001)

def write_bit(v):
    MOSI.value = bool(v)
    clock_tick()
    print("bit written:", MOSI.value)

def write_byte(v):
    for x in range(8):
        write_bit(v & (0b10000000 >> x))

def write_register(register, data):
    if not isinstance(data, list):
        data = [data]
    print("data is:", data)
    CS.value = False
    write_bit(0)  # register select
    write_byte(register)
    print("register written:", hex(register))
    for i in range(0, len(data)):
        write_bit(1)  # register write
        write_byte(data[i])
        print("data written:", hex(data[i]))
    CS.value = True

def write_cmd(v):
    CS.value = False
    write_bit(0)
    for x in range(8):
        write_bit(v & (0b10000000 >> x))
    print("command written:", hex(v))
    CS.value = True

def reset():
    time.sleep(0.001)
    RST.value = False
    time.sleep(0.120)
    RST.value = True
    time.sleep(0.001)

def disp_init():
    LED.value = True
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
    LED.value = False

# dtoverlay=vc4-kms-dpi-generic
# dtparam=hactive=240,hfp=10,hsync=10,hbp=20
# dtparam=vactive=320,vfp=4,vsync=2,vbp=2
# dtparam=clock-frequency=7000000
# dtparam=rgb666-padhi
# dtparam=hsync-invert
# dtparam=vsync-invert
# dtparam=pixclk-invert
# #dtparam=de-invert
