import mod_spotify
import mod_buttons
import mod_led
from time import sleep

_spotify = mod_spotify.Spotify()
_led = mod_led.Led()
_buttons = mod_buttons.Buttons()

try:
    while true:
        main_loop()
        sleep(0.1)
except KeyboardInterrupt:
    pass

def main_loop():
    button_pressed = _buttons.check():

    if button_pressed == "":
        pass
    else:
        _led.switch(blue, 0.5)
        if button_pressed == "play":
            _spotify.play()
        else if button_pressed == "prev":
            pass #TODO
        else:
            pass #TODO
