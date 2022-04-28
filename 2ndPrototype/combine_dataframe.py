import os
import pandas as pd
import spotipy
import config
from spotipy.oauth2 import SpotifyClientCredentials

def get_combinedSongs():
    CSVs = []
    files = os.listdir('../data/')
    for file in files:
        #file is not an object, but a string
        start_of_filename = file.split("-", 1)[0]

        if(start_of_filename == 'Playlist'):
            CSVs.append(file)

    dataframe_of_songs = pd.DataFrame(columns = ['setnumber','Title','id','danceability','energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness','valence','tempo'])
    for csv in CSVs:
        current_csv_as_dataframe = pd.read_csv("../data/" + csv)
        dataframe_of_songs = pd.concat([dataframe_of_songs,  current_csv_as_dataframe])

    dataframe_of_songs.drop_duplicates() 

    features = dataframe_of_songs[['danceability','energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness','valence','tempo']] 
    song_credentials = dataframe_of_songs[['Title','id']]

    return dataframe_of_songs, features, song_credentials

def features_of_playlist(playlist_id):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id= config.client_id,  client_secret= config.client_secret))
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
    dataframe_of_songs.to_csv("../data/Playlist-" + str(playlist_id) + ".csv", index=False)

    return dataframe_of_songs
