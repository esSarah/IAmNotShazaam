import json
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import config
import os
import sys
import combine_dataframe


override = False
playlist_id = ""

if(len(sys.argv) == 1):
    print("I need the playlist id")
    error = True
else:
    playlist_id = sys.argv[1]
    if(len(sys.argv) == 3):
        if(sys.argv[2] == "override"):
            override = True

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id= config.client_id,  client_secret= config.client_secret))
    filename = "../data/Playlist-" + str(playlist_id) + ".csv"
    if(os.path.exists(filename )):
        if(override):
            print("File exists, but we refresh it")
            dataframe_of_songs = combine_dataframe.features_of_playlist(playlist_id)
        else:
            print("file already exists, nothing will be done")
    else:
        print("creating new file")
        dataframe_of_songs = combine_dataframe.features_of_playlist(playlist_id)
		
