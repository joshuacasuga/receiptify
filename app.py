from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import pandas as pd
import time
import gspread
from credentials import CLIENT_ID, CLIENT_SECRET, SECRET_KEY

SCOPE = "user-top-read user-library-read"
TOKEN_CODE = "token_info"

app = Flask(__name__)
app.secret_key = SECRET_KEY

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for('redirectPage', _external = True),
        scope = SCOPE
    )

def get_token():
    token_info = session.get(TOKEN_CODE, None)
    return token_info

@app.route('/')
def index():
    return render_template('index.html', title = 'Welcome')

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirectPage')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_CODE] = token_info
    return redirect(url_for('receipt', _external = True))

@app.route('/receipt')
def receipt():
    user_token = get_token()
    sp = spotipy.Spotify(auth = user_token['access_token'])
    user_top_songs = sp.current_user_top_tracks(
        limit = 10,
        offset = 0,
        time_range = 'medium_term'
    )
    return render_template('receipt.html', title='Welcome')


'''
#Getting Track IDs
def get_track_ids(time_frame):
    track_ids = []
    for song in time_frame['items']:
        track_ids.append(song['id'])
    return track_ids

#Getting track information using track ids
def get_track_features(id):
    meta = spotipy.track(id)

    #meta data
    name = meta['name']
    album = meta['album']['name']
    artist = meta['album']['artists'][0]['name']
    spotify_url = meta['external_urls']['spotify']
    album_cover = meta['album']['images'][0]['url']
    track_info = [name, album, artist, spotify_url, album_cover]
    return track_info

def insert_to_spread(track_ids):
    #Loop over track ids
    tracks = []
    for i in range(len(track_ids)):
        time.sleep(.75)
        track = get_track_features(track_ids[i])
        tracks.append(track)

    #Create dataframe
        dataframe = pd.DataFrame(tracks, columns = ['name', 'album', 'artist', 'spotify_url', 'album_cover'])
        #print(df.head(5))

        #Inserting dataset into Google Sheet
        gc = gspread.service_account(filename='credentials.json')
        sh = gc.open_by_key(os.getenv('GSPREAD_OPEN_BY_KEY'))
        worksheet = sh.worksheet(f'{time_period}')
        worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
        print("Import " + str(i + 1) + " complete.")

#Getting data within different time ranges
time_ranges = ['short_term', 'medium_term', 'long_term']
for time_period in time_ranges:
    print("Beginning import for time frame: " + time_period)
    top_tracks = spotipy.current_user_top_tracks(limit = 10, offset = 0, time_range = time_period)
    track_ids = get_track_ids(top_tracks)
    insert_to_spread(track_ids) #Calls function

print('Data import complete.')
'''