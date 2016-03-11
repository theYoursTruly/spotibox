import RPi.GPIO as GPIO
from time import sleep

class Led:
    """Semi-lowlevel class handling leds"""
    def __init__(self):
        """Initialize GPIO pins for each diode"""
        GPIO.setmode(GPIO.BOARD)
        self.pins = {"blue":[19,0], "green":[11,0]}
        GPIO.setup((self.pins["blue"][0], self.pins["green"][0]), GPIO.OUT)
        GPIO.output(self.pins["blue"][0], 0)
        GPIO.output(self.pins["green"][0], 0)

    def switch(self, color, state=-1):
        """Turn diode on or off."""
        if state == -1:
            state = 1 - self.pins[color][1]
        GPIO.output(self.pins[color][0], state)
        self.pins[color][1] = state
