import RPi.GPIO as GPIO
from time import sleep

class Buttons:
    """Low-level class handling button-clicks on the Spotibox."""
    def __init__(self):
        """Setup GPIO pins for buttons and prepare variables needed later."""
        self.buttons = {"play":12, "prev":16, "next":18, "playlist":22, "shuffle":13, "delay":15,}
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup((12,13,15,16,18,22), GPIO.IN)

    def check(self):
        """Check if any of the buttons have been just pressed. Function called regularly."""
        for action, button in self.buttons.items():
            if GPIO.input(button):
                return action
        return ""
