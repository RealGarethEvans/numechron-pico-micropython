# Controller for Shiura's excellent triaxial Numechron clock:
# https://www.printables.com/model/629294-triaxial-numechron-clock

import time
from machine import Pin, RTC, reset
from rp2 import StateMachine
import network
import ntptime
from motor_pio import forward, backwards
from wlan_settings import ssid, password

# Change these button numbers according to how you've got it wired. It'll work fine if you don't bother with any of these buttons
TICK_BUTTON = Pin(10, Pin.IN, Pin.PULL_UP) # You can press this button to advance one minute
FORWARD_BUTTON = Pin(11, Pin.IN, Pin.PULL_UP) # This button moves a tenth of a position so you can easily adjust the position
BACKWARD_BUTTON = Pin(12, Pin.IN, Pin.PULL_UP) # And this one moves a tenth of a position backwards

# You have to have the stepper control lines wired to four consecutive pins. Set the start pin here
STEPPER_START_PIN = 6

STEPS_PER_ROTATION = 383 # Actually a quarter of the number, because we do four steps at a time
DEBOUNCE_TIME = 0.1

class Clock:
    def __init__(self, steps_per_rotation, tick_button=None, forward_button=None, backward_button=None):
        self.steps_per_rotation = steps_per_rotation
        self.tick_button = tick_button
        self.forward_button = forward_button
        self.backward_button = backward_button
        self.tick_button_state = False
        self.forward_button_state = False
        self.backward_button_state = False
        self.debounce_time = DEBOUNCE_TIME
        self.rtc = RTC()
        self.sm_forward = StateMachine(0, forward, freq=2000, set_base=Pin(STEPPER_START_PIN))
        self.sm_forward.active(1)
        self.sm_backwards = StateMachine(1, backwards, freq=2000, set_base=Pin(STEPPER_START_PIN))
        self.sm_backwards.active(1)
        self.net = Network()
        self.set_time()
        self.stop = False # Set this true to stop the clock loop. Useful while testing

    def rotate(self, steps):
        # All we do to rotate the clock is put a number in the state machine's FIFO
        if steps >= 0:
            self.sm_forward.put(steps)
        else:
            self.sm_backwards.put(-steps)

    def tick(self):
        self.rotate(self.steps_per_rotation)

    def adjust_angle(self, percent):
        # move the clock by the given percentage of a minute
        self.rotate(int(self.steps_per_rotation * percent / 100))

    def loop(self):
        while True:
            if self.stop:
                self.stop = False
                break
            minute = self.rtc.datetime()[5]
            if self.previous_min != minute:
                print(f'Tick: {self.rtc.datetime()[4]}:{minute}')
                self.previous_min = minute
                self.tick()

            # I'm setting the time from the Internet every hour.
            # If you think daily is more polite, uncomment this section, and comment out the next
            # if self.previous_day != self.rtc.datetime()[1]:
            #     self.previous_day = self.rtc.datetime()[1]
            #     self.set_time()

            if self.previous_hour != self.rtc.datetime()[4]:
                self.previous_hour = self.rtc.datetime()[4]
                print(f'Hour is {self.previous_hour}')
                time.sleep(5) # so that we're not trying to do too many things at once
                self.set_time()

            # if self.previous_tenmin != int((self.rtc.datetime()[5])/10):
            #     self.previous_tenmin = int((self.rtc.datetime()[5])/10)
            #     print(f'tenmin is {self.previous_tenmin}')
            #     time.sleep(5) # so that we're not trying to do too many things at once
            #     self.set_time()

            # Check for button presses.
            # We debounce by putting everything to sleep for a moment. Maybe not the most efficient,
            # but it's a mechanical clock so it only needs to move once a minute.
            if self.tick_button is not None:
                if self.tick_button.value() == 0 and self.tick_button_state == False:
                    self.tick_button_state = True
                    self.tick()
                    time.sleep(self.debounce_time)
                elif self.tick_button.value() == 1 and self.tick_button_state == True:
                    self.tick_button_state = False

            if self.forward_button is not None:
                if self.forward_button.value() == 0 and self.forward_button_state == False:
                    self.forward_button_state = True
                    self.adjust_angle(5)
                    time.sleep(self.debounce_time)
                elif self.forward_button.value() == 1 and self.forward_button_state == True:
                    self.forward_button_state = False

            if self.backward_button is not None:
                if self.backward_button.value() == 0 and self.backward_button_state == False:
                    self.backward_button_state = True
                    self.adjust_angle(-5)
                    time.sleep(self.debounce_time)
                elif self.backward_button.value() == 1 and self.backward_button_state == True:
                    self.backward_button_state = False

    def set_time(self):
        print("setting time")
        time = self.rtc.datetime()
        print(f'time is currently {time[4]}:{time[5]}:{time[6]}')
        self.net.connect()
        try:
            ntptime.settime() # Almost too easy. I wonder where we get the time from...
            time = self.rtc.datetime()
        except Exception as e:
            print(f'Failed to set time: {e}')
            # I'm just going to let it slide and hopefully it'll work in another hour
        finally:
            print(f'time is now {time[4]}:{time[5]}:{time[6]}')
            print(f'on {time[2]}/{time[1]} {time[0]}')
            self.previous_min = time[5]
            # self.previous_day = time[1]
            self.previous_hour = time[4]
            # self.previous_tenmin = int((self.rtc.datetime()[5])/10)
            self.net.disconnect()
        

class Network:
    def __init__(self):
        self.led = Pin("LED", Pin.OUT)
        # first blink means hello
        self.blink(1, 0.5)

    def connect(self):
        print('Going to connect to wifi')
        try: # to connect to wifi
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
            self.wlan.connect(ssid, password)
            while not self.wlan.isconnected():
                pass
            print(f'Connected to wifi on {self.wlan.ifconfig()[0]}')
            # Four blinks means success
            self.blink(4, 0.25)
        except Exception as e:
            print(f'Failed to connect to wifi: {e}')
            reset() # Nothing clever here

    def disconnect(self):
        self.wlan.disconnect()
        self.wlan.active(False)
        # Three blinks means disconnected
        self.blink(3, 0.25)
        print('Disconnected from wifi')

    def blink(self, how_many, how_long):
        for i in range(how_many):
            self.led.value(1)
            time.sleep(how_long)
            self.led.value(0)
            time.sleep(how_long)


clock = Clock(steps_per_rotation=STEPS_PER_ROTATION, tick_button=TICK_BUTTON, forward_button=FORWARD_BUTTON, backward_button=BACKWARD_BUTTON)
clock.loop()