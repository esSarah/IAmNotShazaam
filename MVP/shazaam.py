'''takes a short recording and asks Shazam for title and artist, if available'''

import sounddevice as sd
from scipy.io.wavfile import write
from pydub import AudioSegment
from ShazamAPI import Shazam

def shazaam(**kwargs):
    """  records a soundbyte and asks Shazam to get
      song and artist if possible.
      Returns False (bool) if no song was found, 
      a tuple of Songtitle (string) and Artist name (string)
    Keyword arguments:
        seconds: optional integer, length of the soundbyte recording
        debug: optional bool, if true, use pre recorded soundbyte 
        silent: optional bool, if true don't write info to command line
    """       

    # handle optional arguments
    is_debug = False
    is_silent = False
    seconds_to_record = 5

    if(kwargs.get('debug', False)==True):
        is_debug = True
    if(kwargs.get('silent', False)==True):
        is_silent = True
    seconds_to_record = kwargs.get('seconds', 5)

    if(is_silent!=True): 
        print("recording for " + str(seconds_to_record) + " seconds")

    fs = 44100  # this is the frequency sampling; also: 4999, 64000
    seconds = seconds_to_record  # Duration of recording

    # get a few seonds of audio from the system microfone as wave file
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    if(is_silent!=True): 
        print("Starting: Play music now!")
    sd.wait()  # Wait until recording is finished
    if(is_silent!=True): 
        print("finished")
    if(is_debug!=True):
        write('song.wav', fs, myrecording)
    
    # load the wave and convert it to mp3
    sound= ""
    if(is_debug==True):
        sound = AudioSegment.from_wav("debug.wav") 
    else:
        sound = AudioSegment.from_wav("song.wav")
    
    sound.export('song.mp3', format='mp3')
    
    # load the mp3 into a variable
    mp3_file_content_to_recognize = open('song.mp3', 'rb').read()

    # ask shazam by sending their api the mp3 data
    shazam = Shazam(mp3_file_content_to_recognize)
    # try to get song information
    recognize_generator = shazam.recognizeSong()
    
    # wait for the response
    shazam_info = next(recognize_generator)
                   
    # if a song was found, return title and artist
    if(len(shazam_info[1]["matches"])>0):
        song_found = shazam_info[1]["track"]["title"]
        artist_found = shazam_info[1]["track"]["subtitle"]  
        if(is_silent!=True):
            print("that was \"" + song_found + "\" from " + artist_found)
        return  song_found, artist_found 
    else:
        return False       
      