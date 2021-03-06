import mod_spotify
import mod_buttons
import mod_led
from time import sleep
import signal

_led = mod_led.Led()
_spotify = mod_spotify.Spotify(_led)
_buttons = mod_buttons.Buttons()

def _handle_click(button, module):
    _led.switch("green")
    if button == "play":
        _spotify.play()
    elif button == "prev":
        _spotify.switch_track(-1)
    elif button == "next":
        _spotify.switch_track(1)
    elif button == "playlist":
        _spotify.switch_playlist()
    elif button == "shuffle":
        _spotify.toggle_shuffle()
    elif button == "delay":
        _spotify.snooze(2000)
    else:
        print ("How come there is more buttons?")
        pass
    while button == module.check():
        sleep(0.1)
    _led.switch("green")

try:
    print("------------- LISTENING ---------------")
    while True:
        button_pressed = _buttons.check()
        if button_pressed != "":
            _handle_click(button_pressed, _buttons)
        else:
            sleep(0.1)
except KeyboardInterrupt:
    print("------------- CLOSING ---------------")
