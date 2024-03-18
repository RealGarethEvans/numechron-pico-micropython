# type: ignore
# This is in a separate file to stop VS Code hassling me with wavy lines

from rp2 import PIO, asm_pio

@asm_pio(set_init=(PIO.OUT_LOW,) * 4)
def forward():
    # fire this up at the start, then put a number in the FIFO to trigger a movement
    # the number is a quarter of the number of steps to move, because it's easier to program in fours
    wrap_target()

    pull() # Should be the number of steps
    mov(x, osr)

    jmp(not_x, "end") # when we've finished, x will be zero
    label("loop")

    set(pins, 1)    [4] # Increase the number at the end of these lines if you want to slow down the movement.
    set(pins, 2)    [4] # If you want to speed it up, you might be better off
    set(pins, 4)    [4] # changing the frequency when you create the state machine
    set(pins, 8)    [4]

    jmp(x_dec, "loop")
    label("end")
    set(pins, 0)    [4]

    wrap()

@asm_pio(set_init=(PIO.OUT_LOW,) * 4)
def backwards():
    # fire this up at the start, and put a number in the FIFO to trigger a movement
    # the number is a quarter of the number of steps to move, because it's easier to program in fours
    wrap_target()

    pull() # Should be the number of steps
    mov(x, osr)

    jmp(not_x, "end") # when we've finished, x will be zero
    label("loop")

    set(pins, 8)    [4] # Increase the number at the end of these lines if you want to slow down the movement.
    set(pins, 4)    [4] # If you want to speed it up, you might be better off
    set(pins, 2)    [4] # changing the frequency when you create the state machine
    set(pins, 1)    [4]

    jmp(x_dec, "loop")
    label("end")
    set(pins, 0)    [4]

    wrap()

