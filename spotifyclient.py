import os
import json
import sys
import webbrowser
import requests
from builtins import input
import spotipy


class SpotifyClient(object):
    def __init__(self):

        self.auth_url = "https://accounts.spotify.com/authorize?client_id=dad7b372b95742f2b718c89f94f9b364&response_type=token&redirect_uri=http://localhost/&scope=user-read-private playlist-modify-private playlist-modify-public"
        self.auth_key = None
        self._load_token()
        self.base_url = "https://api.spotify.com/v1/"
        self.headers = {
            "Authorization": "Bearer " + self.auth_key,
            "Content-Type": "application/json"
            }
        self.user_id = None

    # Private methods not used directly in main routines
    def _store_token(self):
        """
        Store token on disk for caching
        """
        with open('.spotify', 'w') as outfile:
            outfile.write(self.auth_key)

    def _load_token(self):
        """
        Read token on disk for caching
        """
        # We can almost definitely do this more gracefully
        if not os.path.isfile('.spotify'):
            self._store_token()
        with open('.spotify') as infile:
            self.auth_key = infile.read()

    def _test_token(self):
        """
        Create client with credentials, attempt to pull data
        Return boolean - whether the client successfully authenticated or not
        """
        url = self.base_url + "me"
        r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            self.user_id = r.json()['id']
        return r.status_code == 200

    def _get_playlist_id(self):
        """
        Gets user input for the playlist URL and attempts to parse it
        to get the User ID and Playlist ID
        """
        playlist_url = input("Enter the URL for the public playlist:  ")
        url_parts = playlist_url.split('/')
        user_id, playlist_id = None, None
        for i in range(len(url_parts)):
            if url_parts[i] == 'user':
                user_id = url_parts[i+1]
            elif url_parts[i] == 'playlist':
                playlist_id = url_parts[i+1]
        if not user_id or not playlist_id:
            print("Could not parse that URL.")
            sys.exit(-1)

        return user_id, playlist_id

    def _search_for_track(self, album, artist, track_name):
        """
        Searches Spotify for a track matching the provided album, artist, and name
        Returns the track ID if found, else None
        """

        url = self.base_url + "search?q=album:{}%20artist:{}%20track:{}&type=track".format(album, artist, track_name)
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        data = r.json()
        try:
            result = data['tracks']['items'][0]['id']
        except:
            result = None
        return result

    def _delete_playlist(self, playlist_id):
        """
        Unfollow a playlist so that it does not appear in your account
        Mostly useful for testing, but maybe this should be used if 
        an exception occurs in the track add process?
        """
        
        url = self.base_url + "users/{}/playlists/{}/followers".format(self.user_id, playlist_id)
        r = requests.delete(url, headers=self.headers)
        r.raise_for_status()
        return True
        
    # Public methods consumed by main routine
    def authenticate(self):
        """
        Tries loading ticket from file and authenticating
        If that fails, prompts user through OAuth flow to get working token
        Return True if successfully authenticated, False otherwise
        """
        self._load_token()
        if not self._test_token():
            webbrowser.open(self.auth_url)
            url = input("Paste in the URL to which your browser redirected you after logging in: ")
            try:
                keys = url.split('#')[1].split('&')
                for key in keys:
                    k, v = key.split('=')
                    if k == 'access_token':
                        self.auth_key = v
                        self.headers["Authorization"] = "Bearer " + self.auth_key
                        break
                if not self.auth_key:
                    print("Failed to get access token from that URL.")
                    return False
            except:
                print("#1")
                print("Failed to authenticate.")
                return False
        if not self._test_token():
            print("#2")
            print("Failed to authenticate.")
            return False
        self._store_token()
        return True

    def get_playlist_tracks(self, playlist_id=None, user_id=None):
        """
        Downloads list of tracks on provided Spotify playlist
        Returns dictionary with following schema:

        {
            "name": <playlist name>,
            "tracks": [
                {
                    "artist": <artist>,
                    "album": <album>,
                    "track": <track name>
                }
            ]
        }
        """

        if not user_id and not playlist_id:
            user_id, playlist_id = self._get_playlist_id()
        all_tracks = []

        base_url = self.base_url + 'users/{0}/playlists/{1}'.format(user_id, playlist_id)
        url = base_url
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        data = r.json()
        offset = 0
        repeat_call = False
        while True:
            r = requests.get(url, headers=self.headers)
            r.raise_for_status()
            data = r.json()
            if not repeat_call:
                playlist_name = data['name']
                data = data['tracks']
            items = [{
                "album": t['track']['album']['name'], 
                "artist": t['track']['artists'][0]['name'], 
                "track": t['track']['name']
            } for t in data['items']]
        
            all_tracks += items
            if data['next']:
                offset += data['limit']
                url = data['next']
                repeat_call = True
            else:
                break
        
        return {'name': playlist_name, 'tracks': all_tracks}

    def search_for_tracklist(self, tracklist):
        """
        Searches Spotify for a provided list of tracks
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
        Return the playlist ID
        """        
        url = self.base_url + "users/" + self.user_id + "/playlists"
        data = {
            "name": playlist_name
        }
        r = requests.post(url, headers=self.headers, data=json.dumps(data))
        r.raise_for_status()
        return r.json()['id']

    

    def add_tracks_to_playlist(self, playlist_id, track_list):
        """
        Add all track in provided track_list to desired playlist
        track_list should be a list of Spotify track IDs, 
        provided by the 'found' index of search_for_tracks()
        """
        url = self.base_url + "users/{}/playlists/{}/tracks".format(self.user_id, playlist_id)
        base_uri_string = "?uris=spotify:track:"
        index = 0
        count = 50
        while index < len(track_list):
            sub_track_list = track_list[index:index+count]
            track_list_string = base_uri_string + ",spotify:track:".join(sub_track_list)            
            r = requests.post(url + track_list_string, headers=self.headers, data=json.dumps({}))
            r.raise_for_status()
            index += len(sub_track_list)

        # TODO add a logical return value to this
            

if __name__ == "__main__":
    pass
