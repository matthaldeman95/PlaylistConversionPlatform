import sys
from builtins import input
from enum import Enum

from googleclient import GoogleClient
from spotifyclient import SpotifyClient

class PlaylistConverter(object):

    def __init__(self):
        self.source_client = None
        self.destination_client = None
        self.services = [
            {"name": "Google Play Music", "client": GoogleClient()},
            {"name": "Spotify", "client": SpotifyClient()}
        ]


    def describe_services(self):
        """
        List available services
        """
        print("Currently available services:")
        for i in range(len(self.services)):
            print("{}: {}".format(i, self.services[i]['name']))

    def get_services(self):
        """
        Call get_service() to get both source and destination
        """
        self.describe_services()
        print("Please select a source service")
        self.source_client = self.get_service()['client']
        print("Please select a destination service")
        self.destination_client = self.get_service()['client']

    def get_service(self):
        """
        Prompts user to select one of the available services based on integer entry
        """
        while True:
            try:
                selection = input("Select the integer corresponding to desired service:  ")
                selection_index = int(selection)
                if 0 <= selection_index < len(self.services):
                    return self.services[selection_index]
                else:
                    print("Invalid choice")
            except ValueError:
                print("Not an number")

    def authenticate_service(self, client):
        """
        Prompts user through authentication flow, allows retries if desired
        """
        while True:
            auth_status = client.authenticate()
            if not auth_status:
                print("Authentication failed, try again?")
                selection = input("Type y for yes, anything else for no:  ")
                if selection != "y":
                    return False
            else:
                return True


# Authenticate services
pc = PlaylistConverter()
pc.get_services()
source_auth_status = pc.authenticate_service(pc.source_client)
if not source_auth_status:
    sys.exit(-1)
destination_auth_status = pc.authenticate_service(pc.destination_client)
if not destination_auth_status:
    sys.exit(-1)

# Get source playlist tracks and name
source_playlist = pc.source_client.get_playlist_tracks()
playlist_name = source_playlist['name']
playlist_tracks = source_playlist['tracks']
if not playlist_tracks:
    print("No tracks found on that playlist")
    sys.exit(-2)


destination_tracks = pc.destination_client.search_for_tracklist(playlist_tracks)
found_tracks = destination_tracks['found']
not_found_tracks = destination_tracks['not_found']
print("{} tracks not found, would you like to see a list?  ".format(len(not_found_tracks)))
selection = input("Type y for yes, anything else for no:  ")
if selection == "y":
    for t in not_found_tracks:
        print(t)
if not found_tracks:
    print("Could not successfully find any of those tracks in destination service")
    sys.exit(-3)

print("Current source playlist name:  {}".format(playlist_name))
selection = input("Type name for new playlist (leave blank to use current name):  ")
if selection:
    playlist_name = selection

created_playlist_id = pc.destination_client.create_playlist(playlist_name)
if not created_playlist_id:
    print("Could not create destination playlist")
    sys.exit(-4)

pc.destination_client.add_tracks_to_playlist(created_playlist_id, found_tracks)
