import unittest
import json

class TestImports(unittest.TestCase):
    
    
    def test_google_client(self):

        # Initialize client
        from googleclient import GoogleClient
        google_client = GoogleClient()
        assert(google_client)

        # Authenticate
        assert(google_client.authenticate())
        
        # Search for test tracks
        track_list = [
            {
                "artist": "Broods",
                "track": "Bridges",
                "album": "Evergreen"
            },
            {
                "artist": "Matthew Haldeman",
                "track": "PCP",
                "album": "The Matthew Haldeman Experience"
            }
        ]
        result = google_client.search_for_tracklist(track_list)
        assert(len(result['found']) == len(result['not_found']) == 1)

        # Create a test playlist
        playlist_name = "Test Playlist"
        playlist_id = google_client.create_playlist(playlist_name=playlist_name)

        # Add test tracks
        track_list=["Trt4j3fkj3rqytzh3ppwm2rqnni", "Tlbdefxc2ba7cbj6g7olhvqtaay"]
        result = google_client.add_tracks_to_playlist(playlist_id=playlist_id, track_list=track_list)
        # TODO Check to make sure the tracks were added
        assert(len(result) == len(track_list) == 2)
        
        # Delete test playlist
        result = google_client._delete_playlist(playlist_id)
        assert(result)

        #playlist_id = "AMaBXylOVFMGKhY9cGUl-ls7HMIhQualBYDk6cP1Dn55dxsTSXllEIMDxOC_Sw7FSbtXj-3r3YwPlhErUKcmlBBec1v_yNXElg=="
        #results = google_client.get_playlist_tracks(playlist_id=playlist_id)
        #assert(len(results['tracks']) == 75)
    
    
    def test_spotify_client(self):

        # Initialize client
        from spotifyclient import SpotifyClient
        spotify_client = SpotifyClient()
        assert(spotify_client)

        # Authenticate
        assert(spotify_client.authenticate())   

        # Search for test tracks (one that exists and one that doesn't)     
        track_list = [
            {
                "artist": "Broods",
                "track": "Bridges",
                "album": "Evergreen"
            },
            {
                "artist": "Matthew Haldeman",
                "track": "PCP",
                "album": "The Matthew Haldeman Experience"
            }
        ]
        result = spotify_client.search_for_tracklist(track_list)
        assert(len(result['found']) == len(result['not_found']) == 1)

        # Create a test playlist
        playlist_name = "Test Playlist"
        playlist_id = spotify_client.create_playlist(playlist_name=playlist_name)

        # Add test tracks
        track_list=["2Ud3deeqLAG988pfW0Kwcl", "1285n66OGGUB3Bnh6c18nS"]
        spotify_client.add_tracks_to_playlist(playlist_id=playlist_id, track_list=track_list)
        # Check to make sure the tracks were added
        results = spotify_client.get_playlist_tracks(playlist_id=playlist_id, user_id=spotify_client.user_id)
        assert(results['name']) == playlist_name
        assert(len(results['tracks']) == len(track_list))

        # Unfollow playlist (so I don't clutter up my spotify with bullshit "Test Playlists")
        result = spotify_client._delete_playlist(playlist_id =playlist_id)
        assert(result)


if __name__ == '__main__':
    unittest.main()
