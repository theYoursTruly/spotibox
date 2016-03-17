import spotify
import threading
import logging
import random
import credencials # file not included in GIT repository

class Spotify:
    """Spotify handler responsible for communication between Spotibox and Spotify service."""
    def __init__(self, led_module):
        logging.basicConfig(level=logging.INFO)

        config = spotify.Config()
        config.load_application_key_file()
        config.user_agent = "spotibox"
        config.tracefile = "logfile.log"

        self.session = spotify.Session(config)
        spotify.AlsaSink(self.session)
        loop = spotify.EventLoop(self.session)
        loop.start()

        self.logged_in = threading.Event()
        self.session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, self._update)
        self.session.on(spotify.SessionEvent.END_OF_TRACK, self._on_end_of_track)

        self.session.login(credencials.user(), credencials.password())
        self.logged_in.wait()

        self.session.playlist_container.load()
        self.led = led_module
        self.setup()

    def setup(self):
        """Set starting parameters for tracks and playlists."""
        self.current_playlist = self.session.playlist_container[0]
        self.current_playlist.load()
        self.current_tracks = self.current_playlist.tracks
        self.current_playlist_num = 0
        self.current_track_num = 0
        self.last_offset = 1
        self.playing = False
        self.shuffle = False
        self._generate_tracklist()

    def play(self, stop=False):
        """Start/pause/resume the current track."""
        player_state = self.session.player.state
        if stop:
            self.session.player.unload()
            self.playing = False
            self.led.switch("blue", 0)
            print ("Stop track")
        elif player_state is spotify.PlayerState.PLAYING:
            self.session.player.pause()
            self.playing = False
            self.led.switch("blue", 0)
            print ("Pause track")
        else:
            self._play_track(self._get_track(0))
            self.session.player.prefetch(self._get_track(1))
            self.playing = True
            self.led.switch("blue", 1)
            print ("Play track")

    def switch_track(self, offset):
        """Play track that is offset away from the current one."""
        self.last_offset = offset
        self.current_track_num = (self.current_track_num + offset) % len(self.current_tracks)
        if self.playing:
            self.session.player.unload()
            self.play()

    def switch_playlist(self):
        """Switch to the next playlist."""
        playlists_num = len(self.session.playlist_container)
        self.current_playlist_num = (self.current_playlist_num + 1) % playlists_num
        print ("Load playlist %d of %d" % (self.current_playlist_num, playlists_num))
        self.current_playlist = self.session.playlist_container[self.current_playlist_num]
        self.current_playlist.load()
        self.current_tracks = self.current_playlist.tracks
        self._generate_tracklist()
        self.current_track_num = 0
        print ("Playlist ready to play [%s]" % (self.current_playlist.name.encode('utf-8'),))
        if self.playing:
            self.session.player.unload()
            self.play()

    def toggle_shuffle(self):
        """Shuffle tracks or keep them in order."""
        self.shuffle = not self.shuffle
        self._generate_tracklist()
        print ("Shuffle %d" % (self.shuffle,))

    def snooze(self, delay):
        """Stops playback after specified time (in seconds)."""
        if delay > 0:
            print ("Initiate delayed stop after %dsec" % (delay,))
            threading.Timer(delay, self.play, [True]).start()

    # -------- Private Methods ---------

    def _update(self, session):
        """Set thread event when logged in to spotify account."""
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self.logged_in.set()

    def _on_end_of_track(self, session):
        """Detect end of track and switch to the next one."""
        print ("End of track, load the next one.")
        self.switch_track(1)

    def _generate_tracklist(self):
        """Generate list of numbers representing track numbers (and sometimes shuffle).
           This method was created because shuffling tracks is bugged."""
        self.tracks_order = range(len(self.current_tracks))
        if self.shuffle:
            random.shuffle(self.tracks_order)

    def _get_track(self, offset):
        """Return track that is 'offset' apart from the current one."""
        return self.current_tracks[self.tracks_order[self.current_track_num + offset]]

    def _play_track(self, track):
        """Low-level method to play a track."""
        try:
            if self.session.player.state is spotify.PlayerState.UNLOADED:
                track.load()
                self.session.player.load(track)
            print ("Play the track: %s" % (track.name.encode('utf-8'),))
            self.session.player.play()
        except:
            print ("[%d] Unable to play the track: %s" % (self.last_offset, track.name))
            self.switch_track(self.last_offset)
