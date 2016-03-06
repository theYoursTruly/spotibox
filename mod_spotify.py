import spotify
import threading
import logging
import random
import credencials # file not included in GIT repository

class Spotify:
    """Spotify handler responsible for communication between Spotibox and Spotify service."""
    def __init__(self):
        #logging.basicConfig(level=logging.DEBUG)

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

        self.playing = False
        self.setup()

    def setup(self):
        """Set or reset starting parameters for tracks and playlists."""
        if self.playing:
            self.play()
        self.current_playlist = self.session.playlist_container[0]
        self.current_playlist.load()
        self.current_tracks = self.current_playlist.tracks
        self.current_playlist_num = 0
        self.current_track_num = 0
        self.last_offset = 1
        self._generate_shuffle(len(self.current_tracks))
        self.shuffle = False
        print ("Settings reset")

    def play(self, stop_only=False):
        """Start/pause/resume the current track."""
        if self.playing:
            self.playing = False
            if self.session.player.state is spotify.PlayerState.PLAYING:
                self.session.player.pause()
            print ("Track paused")
        elif not stop_only:
            self.playing = True
            if self.session.player.state is spotify.PlayerState.UNLOADED:
                self._play_track(self.current_tracks[self.current_track_num])
            elif self.session.player.state is spotify.PlayerState.LOADED or self.session.player.state is spotify.PlayerState.PAUSED:
                self.session.player.play()
                print ("Track resumed")

    def switch_track(self, offset):
        """Play the next track."""
        self.last_offset = offset
        self.current_track_num = (self.current_track_num + offset) % len(self.current_tracks)
        track_num = self.shuffle_list[self.current_track_num] if self.shuffle else self.current_track_num
        self._play_track(self.current_tracks[track_num])

    def switch_playlist(self):
        """Switch to the next playlist."""
        playlists_num = len(self.session.playlist_container)
        self.current_playlist_num = (self.current_playlist_num + 1) % playlists_num
        print ("Load playlist %d of %d" % (self.current_playlist_num, playlists_num))
        self.current_playlist = self.session.playlist_container[self.current_playlist_num]
        self.current_playlist.load()
        self.current_tracks = self.current_playlist.tracks
        self._generate_shuffle(len(self.current_tracks))
        self.current_track_num = 0
        print ("Playlist ready to play [%s]" % (self.current_playlist.name,))
        if self.playing:
            self._play_track(self.current_tracks[0])

    def toggle_shuffle(self):
        """Shuffle tracks or keep them in order."""
        self.shuffle = not self.shuffle
        print ("Shuffle %d" % (self.shuffle,))

    def delayed_pause(self, delay):
        """Stops the playback after delay (in seconds)."""
        if delay > 0:
            print ("Initiate delayed pause by %dsec" % (delay,))
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

    def _generate_shuffle(self, count):
        """Generate list of shuffled numbers from 0 to count.
           This method was created because shuffling tracks is bugged."""
        self.shuffle_list = range(count)
        random.shuffle(self.shuffle_list)

    def _play_track(self, track):
        """Low-level method to play a track."""
        track.load()
        if not self.session.player.state is spotify.PlayerState.UNLOADED:
            print ("Stop last song")
            self.session.player.unload()
        try:
            print ("Play the track: %s" % (track.name,))
            self.session.player.prefetch(track)
            self.session.player.load(track)
            self.session.player.play()
        except:
            print ("[%d] Unable to play the track: %s" % (self.last_offset, track.name))
            self.switch_track(self.last_offset)
