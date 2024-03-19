## Pi Pico controller for Triaxial Numechron Clock

This allows you to control Shiura's excellent triaxial Numechron clock
(https://www.printables.com/model/629294-triaxial-numechron-clock)
with a Raspberry Pi Pico W. Using a Pico W rather than a plain Pico
means it'll set the time automatically.

# Case
I've designed a case for a Pico W and a ULN2003 driver board. You can get it from (TODO: add an address when it's uploaded). It's got space for four little buttons like [these](https://www.amazon.co.uk/dp/B07XWXV1TS). Three of them are in a row, and one is separate.

# Buttons
The buttons are wired to the most physically convenient pins in my case. They are:

* Pins 6–9: The stepper Driver. If you decide to change this, you need
to choose four consecutively-numbered pins.

* Pin 10: Advances the minute wheel one minute
* Pin 11: Advances the minute wheel by a tenth of the 'minute distance'
* Pin 12: Moves the minute wheel backwards by a tenth of the 'minute distance'

These last three buttons are optional, but I find it easier to adjust the clock this way than physically moving the minute wheel. And they were useful in testing.