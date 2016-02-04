import RPi.GPIO as GPIO
from time import sleep

class Led:
    """Semi-lowlevel class handling leds"""
    def __init__(self):
        """Initialize GPIO pins and start threads for each diode"""
        GPIO.setmode(GPIO.BOARD)
        self.pins = {"blue":(11,0), "green":(19,0)}
        GPIO.output(self.pin_blue, state)
        GPIO.setup((self.pin_green, self.pin_blue), GPIO.OUT)

    def switch(self, color, time=0):
        """Run only as a thread function"""
        state = 1 - self.pins[color][1]
        GPIO.output(self.pins[color][0], state)
        if time != 0:
            sleep time;
            state = 1-state
            GPIO.output(self.pins[color][0], state)
        self.pins[color][1] = state
