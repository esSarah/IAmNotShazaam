'''All that is needed for the I am not Shazaam app'''
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
import datetime

class hidden:
    '''For the purposes of access to values it is a class'''

    # I use a sample outside of the workflow here
    # the data from the workflow would be "../models"
    
    filepathToData = "../models/"
    #filepathToData = "./local_data/"

    # the chosen sample als indicates the number of kategories
    model_iterations = "388"
    #model_iterations = "135"

    sp = spotipy

    search_data_dataframe = []

    search_selector_list = []
    song_selected = ""

    there_is_a_track_id = False 
    results_are_a_list = False
    track_id = ""
    song_selected = ""
    song_selector_dictionary = {}

    scaler = object
    kmeans = object

    Top_100 = object



    def load(self, filename = "filename.pickle"):
        '''
        quick helper function to unpickle objects
        takes path, returns object if possible
        ''' 
        try: 
            with open(filename, "rb") as f: 
                return pickle.load(f) 
            
        except FileNotFoundError: 
            print("File not found!") 

    def soundex(self, name):
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



    def get_top_100(self):
        '''gets the top 100 Songs from Billboard, returns them in a dataframe'''
        to_delete_list  = []
        needs_to_refresh = True
        files = os.listdir('../data/')
        current_filename = 'Top100-' +  datetime.datetime.today().strftime('%Y%m%d') + ".pickle"

        # sorts out all the pickles
        # out of sell by date
        # ------------------
        # which is everything but today
        for file in files:
            start_of_filename = file.split("-", 1)[0]

            if(start_of_filename == 'Top100'):
                if(file==current_filename ):
                    needs_to_refresh=False
                else:
                    to_delete_list.append(file)
        for old_files in to_delete_list:
            os.remove('../data/'+old_files)
        
        if(needs_to_refresh):

            # OK, lets look at the page
            URL = 'https://www.billboard.com/charts/hot-100/'
            Top100Website = requests.get(URL)
            result = BeautifulSoup(Top100Website.content, 'html.parser')

            result.find("span", id="count_texttitle-of-a-story")

            line_number = 0
            place_number = 0
            Song = "";
            Artists = "";
            self.Top_100 = pd.DataFrame(columns=['place','song','artists', 'song_soundex'])

            #and move ourselfs through the table, feeding our list
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

                                self.Top_100.loc[place_number -1] = [place_number, Song, Artists, self.soundex(str(Song))]
            
                            internal_line += 1
            
            #pickle with best by date tomorrow
            with open('../data/' + current_filename, "wb") as f:
                pickle.dump(self.Top_100,f)
        else:
            # when possible, we also can just load the pickled version
            self.Top_100 = self.load(filename = '../data/' + current_filename)

        return self.Top_100

    def init_cluster(self):
        '''prepares the k means categorization'''
        all_song_dataframe, features_dataframe, credentials_dataframe = combine_dataframe.get_combinedSongs()

        # load the saved clusters and scaler, change is always possible

        print(self.filepathToData + "scaler.pickle")
        self.scaler = self.load(self.filepathToData + "scaler.pickle")
        self.kmeans = self.load(self.filepathToData + "kmeans_" + self.model_iterations + ".pickle")

        # the price for the flexibility is that we have to classify our
        # current data every time
        self.scaler.fit(features_dataframe)
        audio_features_scaled = self.scaler.transform(features_dataframe)
        category_dataframe = self.kmeans.predict(audio_features_scaled)

        # adds the categories to the dataframe
        category_dataframe = pd.DataFrame(category_dataframe)
        category_dataframe.columns = ['cluster']
        self.search_data_dataframe = credentials_dataframe.join(category_dataframe)
        return self.search_data_dataframe

    def find_match(self , recommend_me_something_for_this, Top_100):
        '''searches for a ssong on Spotify, takes the search string and the top 100 dataframe'''
        self.track_id = ""
        self.there_is_a_track_id = False
        self.results_are_a_list = False

        search_row_list = []
        artist_row_list = []
        columns_counter = 0

        artist_row_list

        self.song_selector_dictionary = {}

        song_selected = ""
        search_selector_list = []


        if(recommend_me_something_for_this.strip()==""):
            print("Please retry, it was empty!")
        else:
            self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id= config.client_id,  client_secret= config.client_secret))

            # detour to recording and asking shazam for help
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
            # look it if it is in the billboards top 100
            Number_Of_Songs_Found = len(Top_100[Top_100['song_soundex'] == self.soundex(recommend_me_something_for_this.strip())])
            if(Number_Of_Songs_Found>0):
                #find a new song
                print("Let me recommend you:")
                recommendation_dataframe = Top_100.sample(n=1)
                print(str(recommendation_dataframe ))
            else:
                #else look it up on spotify
                if(len(recommend_me_something_for_this.strip())>0):
                    self.song_selector_dictionary.clear()
                    self.search_selector_list .clear()
                    search_results = self.sp.search(q=recommend_me_something_for_this.strip(),limit=50,market="GB")
                    if(len(search_results["tracks"])>1):
                        #if there is more than one result, prepare a selection
                        self.there_is_a_track_id = True
                        self.results_are_a_list = True
                        print("Please select a number regarding the many titles of this name")
                        for i in range(0,len(search_results["tracks"]["items"])):
                            columns_counter += 1
                            search_row_list.append("[" + str(i+1) + "]")
                            artist_row_list.append(" ")
                            search_row_list.append( str(search_results["tracks"]["items"][i]["name"]))
                            self.song_selector_dictionary[str(i+1)] = str(search_results["tracks"]["items"][i]["id"])
                            current_artists =""
                            for j in range(0,len(search_results["tracks"]["items"][i]["artists"])):
                                current_artists += str(search_results["tracks"]["items"][i]["artists"][j]["name"]) + ", "
                            artist_row_list.append(current_artists[:-2])
                            if(columns_counter%5==0):
                                columns_counter = 0
                                self.search_selector_list.append(search_row_list)
                                search_row_list = []
                                self.search_selector_list.append(artist_row_list)
                                artist_row_list = []
                    else:
                        #otherwise just use the one and flag accourdingly
                        if(len(search_results)==1):
                            self.there_is_a_track_id = True
                            self.track_id=str(search_results["tracks"]["items"][i]["id"])
                            for j in range(0,len(search_results["tracks"]["items"][0]["artists"])):
                                print("  " + str(search_results["tracks"]["items"][0]["artists"][j]["name"]))

    def get_match(self):
        '''matches a song from the categorized data'''
        if(self.there_is_a_track_id):
            if(self.results_are_a_list):
                # if we had a selection we get the selected track id here
                self.track_id = self.song_selector_dictionary[self.song_selected]
        # get the features of the selected song
        selection_features = self.sp.audio_features("spotify:track:" + self.track_id)
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

        #fit it with the data
        self.scaler.fit(dataframe_of_one)
        dataframe_of_one_scaled = self.scaler.transform(dataframe_of_one)
        category_of_one_dataframe = self.kmeans.predict(dataframe_of_one_scaled)

        #and randomly pick a song from the same category
        catecory_to_find_song = category_of_one_dataframe[0]
        track = self.search_data_dataframe.loc[self.search_data_dataframe['cluster'] == catecory_to_find_song ].sample(n=1)
        print(str(track))
        for r in track.to_numpy().tolist():
            self.track_id = r[1]    

