from time import sleep
from rp2 import StateMachine, PIO
from machine import Pin
from blink_pio import blink_prog, blink_number, drive_stepper


led = Pin(16, Pin.OUT) 

def py_blink():
    for i in range(5):
        led.value(1)
        sleep(0.25)
        led.value(0)
        sleep(0.25)

def pio_blink(sm):
    sm.active(1)
    sleep(4)
    sm.active(0)

def pio_blink_number(sm):
    sm1.active(1)
    for _ in range(5):
        sm1.put(0x00010001)
    sm1.active(0)

def do_steps(sm, steps):
    sm.active(1)
    sm.put(steps)

# Instantiate a state machine with the blink program, at 2000Hz, with set bound to Pin(25) (LED on the Pico board)
# sm0 = StateMachine(0, blink_prog, freq=2000, set_base=Pin(16))
sm1 = StateMachine(0, blink_number, freq=2000, out_shiftdir=PIO.SHIFT_RIGHT, out_base=Pin(16))
sm2 = StateMachine(1, drive_stepper, freq=2000, set_base=Pin(2))

# Run the state machine for 3 seconds.  The LED should blink.
# sm0.active(1)
# sleep(2)
# sm0.active(0)
