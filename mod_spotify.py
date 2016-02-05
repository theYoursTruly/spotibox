import spotify
import threading
import logging
import credencials # file not included in GIT repository

class Spotify:
    """Spotify handler responsible for communication between Spotibox and Spotify service."""
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)

        config = spotify.Config()
        config.load_application_key_file()
        config.user_agent = "spotibox"
        config.tracefile = "logfile.log"

        self.session = spotify.Session(config)
        spotify.AlsaSink(self.session)
        loop = spotify.EventLoop(self.session)
        loop.start()

        self.logged_in = threading.Event()
        self.end_of_track = threading.Event()
        self.session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, self._update)
        self.session.on(spotify.SessionEvent.END_OF_TRACK, self._on_end_of_track)

        self.session.login(credencials.user(), credencials.password())
        self.logged_in.wait()

        self.session.playlist_container.load()

        self.playing = False
        self.current_playlist = 0
        self.current_track = 0

    def _update(self, session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self.logged_in.set()

    def _on_end_of_track(self):
        self.end_of_track.set()

    def play(self):
        if self.playing:
            self.playing = False
            if self.session.player.state is spotify.PlayerState.PLAYING:
                self.session.player.pause()
        else:
            self.playing = True
            if self.session.player.state is spotify.PlayerState.UNLOADED:
                track = self.session.playlist_container[self.current_playlist].tracks[self.current_track]
                self._play_track(track)
            else if self.session.player.state is spotify.PlayerState.LOADED or
                    self.session.player.state is spotify.PlayerState.PAUSED:
                self.session.player.play()

    def _play_track(self, name):
        if not self.session.player.state is spotify.PlayerState.UNLOADED:
            self.session.player.unload()
        self.session.player.load(track)
        self.session.player.play()
