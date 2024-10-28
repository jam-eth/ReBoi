import time
from machine import Pin

CLK = Pin(1, Pin.OUT)
MOSI = Pin(0, Pin.OUT)
CS = Pin(3, Pin.OUT)
RST = Pin(2, Pin.OUT)
CS.on()
LED = Pin(25, Pin.OUT)

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
