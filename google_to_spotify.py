import sys
import spotipy
import webbrowser
import getpass

from builtins import input
from urllib import parse
from gmusicapi.clients import Mobileclient
from spotipy import util


def get_google_tracklist():
    """
    Return list of tracks from a shared Google playlist URL
    """
    api = Mobileclient()
    login_email = input("Enter your Google email address:  ")
    login_password = getpass.getpass("Enter the password for your Google account:  ")
    
    print("Authenticating to Google...")
    if not api.login(login_email, login_password, Mobileclient.FROM_MAC_ADDRESS):
        print("Authentication failed")
        sys.exit(-1)

    playlist_shared_url = input("Enter the shared URL for the Google playlist:  ")
    try:
        playlist_id = parse.unquote(playlist_shared_url.split('playlist/')[1])
    except:
        print("Error parsing that URL.")
        sys.exit(-1)
    songs = api.get_shared_playlist_contents(playlist_id)
    api.logout()
    print("Success!")
    
    return songs
    
    
def create_spotify_playlist(track_list):
    
    url = 'https://accounts.spotify.com/authorize?client_id=dad7b372b95742f2b718c89f94f9b364&response_type=token&redirect_uri=http://localhost/&scope=user-read-private playlist-modify-private playlist-modify-public'
    webbrowser.open(url)

    url = input("Paste in the URL for where your browser redirected you: ")
    try:
        print(url)
        keys = url.split('#')[1].split('&')
        access_key = None
        for key in keys:
            k, v = key.split('=')
            if k == 'access_token':
                access_key = v
                break
        if not access_key:
            print("Failed to get access token from that URL.")
            sys.exit(-1)
    except:
        print("Failed to authenticate.")
        sys.exit(-1)
    
    print("Authenticating...")
    sp = spotipy.Spotify(auth=access_key)
    print("Getting your information...")
    try:
        user_data = sp.me()
        user_id = user_data['id']
    except:
        print("Failed to get your data.")
        raise

    playlist_name = input("Name your playlist:  ")
    print("Creating playlist...")
    try:
        playlist = sp.user_playlist_create(user=user_id,name=playlist_name)
        playlist_id = playlist['id']
        print("Successfully created playlist!")
    except:
        print("Could not create playlist.")
        raise
    # Try to get IDs for all tracks in playlist
    print("Finding tracks...")
    spotify_track_ids = []
    not_found = []
    index = 0
    for track in track_list:
        if index % 10 == 0:
            print("Finding track {0} of {1}".format(index, len(track_list)))
        track = track['track']
        artist = track['artist']
        title = track['title']
        album = track['album']
        try:
            result = sp.search(q='{0} {1} {2}'.format(title, artist, album), limit=1)['tracks']['items'][0]['uri']
            spotify_track_ids.append(result)
        except:
            print("Unable to find track " + title)
            not_found.append({'artist': artist, 'track': title})
        index += 1
    print("Located {0} of {1} tracks".format(len(spotify_track_ids), len(track_list))),
    if len(not_found):
        print(", could not find the following tracks:")
        for item in not_found:
            print(item)
    print("Adding tracks to playlist...")
    sp.user_playlist_add_tracks(user_id, playlist_id, spotify_track_ids)
    print("Complete")
    
def main():

    songs = get_google_tracklist()
    if len(songs) == 0:
        print("No songs found.")
        sys.exit(-1)
    create_spotify_playlist(songs)

if __name__ == "__main__":
    main()