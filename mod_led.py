import RPi.GPIO as GPIO
import threading
from time import sleep

class Led:
    """Semi-lowlevel class handling leds"""
    def __init__(self):
        """Initialize GPIO pins and start threads for each diode"""
        GPIO.setmode(GPIO.BOARD)
        self.pins = {"blue":[19,0], "green":[11,0]}
        GPIO.setup((self.pins["blue"][0], self.pins["green"][0]), GPIO.OUT)
        GPIO.output(self.pins["blue"][0], 0)
        GPIO.output(self.pins["green"][0], 0)

    def switch(self, color, time=0):
        """Run only as a thread function"""
        state = 1 - self.pins[color][1]
        GPIO.output(self.pins[color][0], state)
        self.pins[color][1] = state
        if time != 0:
            threading.Timer(time, self.switch, [color]).start()
