import mod_spotify
import mod_buttons
import mod_led

_spotify = Spotify()
_led = Led()
_buttons = Buttons()

try:
    while true:
        main_loop()
except KeyboardInterrupt:
    pass

def main_loop():
    button_pressed = _buttons.check():

    if button_pressed == "play":
        _spotify.play()
