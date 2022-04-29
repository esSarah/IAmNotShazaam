#step one, get the top 100
import pandas as pd
from bs4 import BeautifulSoup
import requests

import os
# shazamapi needs ffmpeg , but it doesn't really have to be imported anywhere : import ffmpeg
#Initialize SpotiPy with user credentias
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import config

import combine_dataframe

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from matplotlib import pyplot
import numpy as np
import pickle
# local libraries
import shazaam

sp = spotipy

search_data_dataframe = []
scaler = object
kmeans = object
song_selector_dictionary = {}

search_selector_list = []
results_are_a_list = False
there_is_a_track_id = False
selection_features = []
track_id=""
song_selected = ""

def load(filename = "filename.pickle"): 
    try: 
        with open(filename, "rb") as f: 
            return pickle.load(f) 
        
    except FileNotFoundError: 
        print("File not found!") 

def soundex(name):


    """
    The Soundex algorithm assigns a 1-letter + 3-digit code to strings,
    the intention being that strings pronounced the same but spelled
    differently have identical encodings; words pronounced similarly
    should have similar encodings.
    """

    soundexcoding = [' ', ' ', ' ', ' ']
    soundexcodingindex = 1

    #           ABCDEFGHIJKLMNOPQRSTUVWXYZ
    mappings = "01230120022455012623010202"

    soundexcoding[0] = name[0].upper()

    for i in range(1, len(name)):

         c = ord(name[i].upper()) - 65

         if c >= 0 and c <= 25:

             if mappings[c] != '0':

                 if mappings[c] != soundexcoding[soundexcodingindex-1]:

                     soundexcoding[soundexcodingindex] = mappings[c]
                     soundexcodingindex += 1

                 if soundexcodingindex > 3:

                     break

    if soundexcodingindex <= 3:
        while(soundexcodingindex <= 3):
            soundexcoding[soundexcodingindex] = '0'
            soundexcodingindex += 1

    return ''.join(soundexcoding)



def get_top_100():
    URL = 'https://www.billboard.com/charts/hot-100/'
    Top100Website = requests.get(URL)
    result = BeautifulSoup(Top100Website.content, 'html.parser')

    result.find("span", id="count_texttitle-of-a-story")

    line_number = 0
    place_number = 0
    Song = "";
    Artists = "";
    Top_100 = pd.DataFrame(columns=['place','song','artists', 'song_soundex'])

    
    for lines in result.find_all("li", {"o-chart-results-list__item"}):
        line_number += 1

        if((line_number-4)%14==0):
            place_number += 1
            internal_line = 1
            for current_line in lines.get_text().splitlines():

                if(current_line.strip()!=""):
                    if(internal_line==1):
                        Song = current_line.strip()
                    else:
                        Artists = current_line.strip()

                        Top_100.loc[place_number -1] = [place_number, Song, Artists, soundex(str(Song))]
    
                    internal_line += 1

    return Top_100

def init_cluster():

    all_song_dataframe, features_dataframe, credentials_dataframe = combine_dataframe.get_combinedSongs()

    scaler = load("../models/scaler.pickle")
    kmeans = load("../models/kmeans_135.pickle")

    scaler.fit(features_dataframe)
    audio_features_scaled = scaler.transform(features_dataframe)
    category_dataframe = kmeans.predict(audio_features_scaled)

    category_dataframe = pd.DataFrame(category_dataframe)
    category_dataframe.columns = ['cluster']
    return credentials_dataframe.join(category_dataframe)

def find_match(recommend_me_something_for_this, Top_100):

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id= config.client_id,  client_secret= config.client_secret))

    search_row_list = []
    artist_row_list = []
    columns_counter = 0

    artist_row_list

    song_selector_dictionary = {}
    song_selected = ""
    if(recommend_me_something_for_this=="shazaam"):
        #use the local shazaam library to identify the song currently playing
        recorded = shazaam.shazaam()

        #returns false if nothing was found
        if(recorded != False):
            #and a tuple of song and artist if it worked
            recorded_song, recorded_artist = recorded 
            print(recorded_song + " " + recorded_artist)
        
            #replace the input with the actual song
            recommend_me_something_for_this = recorded_song
    
    Number_Of_Songs_Found = len(Top_100[Top_100['song_soundex'] == soundex(recommend_me_something_for_this.strip())])
    if(Number_Of_Songs_Found>0):
        #find a new song
        print("Let me recommend you:")
        recommendation_dataframe = Top_100.sample(n=1)
        print(str(recommendation_dataframe ))
    else:
        if(len(recommend_me_something_for_this.strip())>0):

            search_results = sp.search(q=recommend_me_something_for_this.strip(),limit=50,market="GB")
            if(len(search_results["tracks"])>1):
                there_is_a_track_id = True
                results_are_a_list = True
                print("Please select a number regarding the many titles of this name")
                for i in range(0,len(search_results["tracks"]["items"])):
                    columns_counter += 1
                    search_row_list.append("[" + str(i+1) + "]")
                    artist_row_list.append(" ")
                    search_row_list.append( str(search_results["tracks"]["items"][i]["name"]))
                    #print("["+str(i+1)+"] " + str(search_results["tracks"]["items"][i]["name"]))
                    song_selector_dictionary[str(i+1)] = str(search_results["tracks"]["items"][i]["id"])
                    #print("by")
                    current_artists =""
                    for j in range(0,len(search_results["tracks"]["items"][i]["artists"])):
                        current_artists += str(search_results["tracks"]["items"][i]["artists"][j]["name"]) + ", "
                        #print(str(search_results["tracks"]["items"][i]["artists"][j]["name"]))
                    artist_row_list.append(current_artists[:-2])
                    #print(" ")
                    if(columns_counter%5==0):
                        columns_counter = 0
                        search_selector_list.append(search_row_list)
                        search_row_list = []
                        search_selector_list.append(artist_row_list)
                        artist_row_list = []
                    
                    # HTML('''<html><head><title>none</title></head><body>test</body></html>'''      )
                
            # print(str(search_results["tracks"]["items"][i]["name"]))        
            else:
                if(len(search_results)==1):
                    there_is_a_track_id = True
                    #print(str(search_results["tracks"]["items"][0]["name"]))
                    #print("by")
                    track_id=str(search_results["tracks"]["items"][i]["id"])
                    for j in range(0,len(search_results["tracks"]["items"][0]["artists"])):
                        print("  " + str(search_results["tracks"]["items"][0]["artists"][j]["name"]))


def get_match():
    if(there_is_a_track_id):
        if(results_are_a_list):
            #song_selected = input("which number do you choose? ")
            track_id = song_selector_dictionary[song_selected]
    selection_features = sp.audio_features("spotify:track:" + track_id)
    #print(str(selection_features))
    list_of_one = []
    list_values_of_one = [
        selection_features[0]['danceability'],
        selection_features[0]['energy'],
        selection_features[0]['key'],
        selection_features[0]['loudness'],
        selection_features[0]['mode'],
        selection_features[0]['speechiness'],
        selection_features[0]['acousticness'],
        selection_features[0]['instrumentalness'],
        selection_features[0]['liveness'],
        selection_features[0]['valence'],
        selection_features[0]['tempo']
    ]
    list_of_one.append(list_values_of_one)
    dataframe_of_one = pd.DataFrame(list_of_one)
    dataframe_of_one.columns = ['danceability','energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness','valence','tempo']

    scaler.fit(dataframe_of_one)
    dataframe_of_one_scaled = scaler.transform(dataframe_of_one)
    category_of_one_dataframe = kmeans.predict(dataframe_of_one_scaled)

    catecory_to_find_song = category_of_one_dataframe[0]
    track = search_data_dataframe.loc[search_data_dataframe['cluster'] == catecory_to_find_song ].sample(n=1)
    print(str(track))
    for r in track.to_numpy().tolist():
        track_id = r[1]    

def isTrack_isList_TrackID():
    return there_is_a_track_id, results_are_a_list, track_id

print("prepared")