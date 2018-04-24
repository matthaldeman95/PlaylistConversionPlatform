import sys
import getpass
from builtins import input
from urllib import parse

from gmusicapi.clients import Mobileclient
from spotipy import util


class GoogleClient(object):

    def __init__(self):
        
        self.api = Mobileclient()

    def _get_playlist_id(self):
        """
        Gets user input for the playlist URL and attempts to parse it
        to get the Playlist ID
        """
        playlist_shared_url = input("Enter the shared URL for the Google playlist:  ")
        try:
            playlist_id = parse.unquote(playlist_shared_url.split('playlist/')[1])
        except:
            playlist_id = None
        return playlist_id

    def _search_for_track(self, album, artist, track_name):
        """
        Searches Google for a track matching the provided album, artist, and name
        Returns the track ID if found, else None
        """
        query = track_name + ',' + artist + ',' + album
        result = self.api.search(query)
        print(result)
        song_hits = result['song_hits']
        # TODO this search has gotta get better...
        for h in song_hits:
            if h['track']['title'] == track_name:
                if h['track']['album'] == album or h['track']['artist'] == artist:
                    return h['track']['storeId']
        # TODO Return the best match if no full match is made
        return None

    def _delete_playlist(self, playlist_id):
        """
        Unfollow a playlist so that it does not appear in your account
        Mostly useful for testing, but maybe this should be used if 
        an exception occurs in the track add process?
        Return playlist ID
        """
        return (self.api.delete_playlist(playlist_id) == playlist_id)

    def authenticate(self):

        email = input("Enter your Google email address:  ")
        password = getpass.getpass("Enter the password for your Google account:  ")
        # TODO store email locally 
        return self.api.login(email, password, Mobileclient.FROM_MAC_ADDRESS)

    def get_playlist_tracks(self, playlist_id=None):
        # TODO Get playlist namea s well!!!
        
        if not playlist_id:
            playlist_id = self._get_playlist_id()
        
        tracks = self.api.get_shared_playlist_contents(playlist_id)
        tracks = [{
            "track": t['track']['title'],
            "album": t['track']['album'],
            "artist": t['track']['artist']
            } for t in tracks]
        return {"name": None, "tracks": tracks}

    def search_for_tracklist(self, tracklist):
        """
        Searches Google for a provided list of tracks
        Track list should be the format provided by indexing 'tracks' in the 
        dict returned from get_playlist_tracks()
        """
        found, not_found = [], []
        for t in tracklist:
            result = self._search_for_track(album=t['album'], artist=t['artist'], track_name=t['track'])
            if result:
                found.append(result)
            else:
                not_found.append(t)

        return {"found": found, "not_found": not_found}

    def create_playlist(self, playlist_name):
        """
        Create a new playlist with the provided name
        "prompt" param is mostly just here for testing
        Return the generated playlist ID
        """
        return self.api.create_playlist(name=playlist_name)

    def add_tracks_to_playlist(self, playlist_id, track_list):
        """
        Add all track in provided track_list to desired playlist
        track_list should be a list of Google track IDs, 
        provided by the 'found' index of search_for_tracks()
        """
        return self.api.add_songs_to_playlist(playlist_id=playlist_id, song_ids=track_list)
        # TODO add a logical return value to this


if __name__ == "__main__":
    g = GoogleClient()
    g.authenticate()
    g._search_for_track(album="Evergreen", artist="Broods", track_name="Bridges")
    # Need to log out of google api session
