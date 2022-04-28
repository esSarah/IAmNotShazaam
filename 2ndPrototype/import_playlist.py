import json
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import config
import os
import sys


override = False
playlist_id = ""





def features_of_playlist(playlist_id):
    list_of_songs=[]
    the_end_is_neigh = True
    current_offset=0
    counter_over_all_entries = 0
    
    no_features_available = 0
    connection_timeout = 0
    
    while(the_end_is_neigh):
        playlist = sp.user_playlist_tracks("spotify", playlist_id,offset=current_offset,market="GB")
        current_offset += 99
        for i in range(0,len(playlist["items"])):
            try:
                features = sp.audio_features(playlist["items"][i]["track"]["uri"] )
                try:
                    list_values = [
                        current_offset+i-98,
                        playlist["items"][i]["track"]["name"],
                        playlist["items"][i]["track"]["id"],
                        features[0]['danceability'],
                        features[0]['energy'],
                        features[0]['key'],
                        features[0]['loudness'],
                        features[0]['mode'],
                        features[0]['speechiness'],
                        features[0]['acousticness'],
                        features[0]['instrumentalness'],
                        features[0]['liveness'],
                        features[0]['valence'],
                        features[0]['tempo']
                    ]
                    list_of_songs.append(list_values)
                except:
                    print('saving of this song not possible')
                    no_features_available += 1
            except:
                print("we ran into a timeout")
                connection_timeout += 1
                
            counter_over_all_entries += 1
            print(str(list_values))
        if(i!=99):
            the_end_is_neigh = False
            #because the end is here
    print("It was not possible to access the features of " + str(no_features_available) + " titles.")
    print("We ran into a timeout " + str(connection_timeout) + " times.")
    
    dataframe_of_songs = pd.DataFrame(list_of_songs)
    dataframe_of_songs.columns = ['setnumber','Title','id','danceability','energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness','valence','tempo']
    dataframe_of_songs.to_csv("..\\data\\Playlist-" + str(playlist_id) + ".csv", index=False)

    return dataframe_of_songs


if(len(sys.argv) == 1):
    print("I need the playlist id")
    error = True
else:
    playlist_id = sys.argv[1]
    if(len(sys.argv) == 3):
        if(sys.argv[2] == "override"):
            override = True

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id= config.client_id,  client_secret= config.client_secret))
    filename = "..\\data\\Playlist-" + str(playlist_id) + ".csv"
    if(os.path.exists(filename )):
        if(override):
            print("File exists, but we refresh it")
            dataframe_of_songs = features_of_playlist(playlist_id)
        else:
            print("file already exists, nothing will be done")
    else:
        print("creating new file")
        dataframe_of_songs = features_of_playlist(playlist_id)
		
