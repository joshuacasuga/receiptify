from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
#import pandas as pd
from time import gmtime, strftime
import gspread
from credentials import CLIENT_ID, CLIENT_SECRET, SECRET_KEY

SCOPE = "user-top-read user-library-read"
TOKEN_CODE = "token_info"
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_NAME'] = "Josh's session"

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

def clear_cache():
    if os.path.exists(".cache"):
        os.remove(".cache")

@app.route('/')
def index():
    return render_template('index.html', title = 'Wrapped on Demand')

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirectPage')
def redirectPage():
    clear_cache()
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_CODE] = token_info
    return redirect(url_for('landing', _external = True))

@app.route('/landing')
def landing():
    return render_template('landing.html', title = 'Wrapped on Demand')

@app.route('/showTracks')
def showTracks():
    try:
        user_token = get_token()
    except:
        print("User has not logged in.")
        return redirect("/")

    sp = spotipy.Spotify(auth = user_token['access_token'])
    username = sp.current_user()['display_name']

    #tracks
    short_term_tracks = sp.current_user_top_tracks(
        limit=10,
        offset=0,
        time_range='short_term'
    )
    medium_term_tracks = sp.current_user_top_tracks(
        limit=10,
        offset=0,
        time_range='medium_term'
    )
    long_term_tracks = sp.current_user_top_tracks(
        limit=10,
        offset=0,
        time_range='long_term'
    )

    clear_cache()

    return render_template('tracks.html', 
                           title='Wrapped on Demand', 
                           username=username,
                           short_term=short_term_tracks,
                           medium_term = medium_term_tracks,
                           long_term = long_term_tracks,
                           currentTime = gmtime())

@app.route('/showArtists')
def showArtists():
    try:
        user_token = get_token()
    except:
        print("User has not logged in.")
        return redirect("/")

    sp = spotipy.Spotify(auth = user_token['access_token'])
    username = sp.current_user()['display_name']

    #artists
    short_term_artists = sp.current_user_top_artists(
        limit=10,
        offset=0,
        time_range='short_term'
    )
    medium_term_artists = sp.current_user_top_artists(
        limit=10,
        offset=0,
        time_range='medium_term'
    )
    long_term_artists = sp.current_user_top_artists(
        limit=10,
        offset=0,
        time_range='long_term'
    )
    
    clear_cache()

    return render_template('artists.html', 
                           title='Wrapped on Demand', 
                           username=username,
                           short_term=short_term_artists,
                           medium_term = medium_term_artists,
                           long_term = long_term_artists,
                           currentTime = gmtime())

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    return strftime("%a, %d %b %Y", date)

@app.template_filter('mmss')
def _jinja2_filter_milliseconds(time, fmt=None):
    time = int(time / 1000)
    minutes = time // 60
    seconds = time % 60
    if seconds < 10:
        return str(minutes) + ":0" + str(seconds)
    return str(minutes) + ":" + str(seconds)

'''
@app.route('/getTracks')
def getTracks():
    user_token = get_token()
    sp = spotipy.Spotify(auth=user_token['access_token'])

    current_user_name = sp.current_user()['display_name']
    short_term = sp.current_user_top_tracks(
        limit=10,
        offset=0,
        time_range='short_term',
    )
    medium_term = sp.current_user_top_tracks(
        limit=10,
        offset=0,
        time_range='medium_term',
    )
    long_term = sp.current_user_top_tracks(
        limit=10,
        offset=0,
        time_range='long_term',
    )

    if os.path.exists(".cache"): 
        os.remove(".cache")

    return render_template('receipt.html', user_display_name=current_user_name, short_term=short_term, medium_term=medium_term, long_term=long_term, currentTime=gmtime())
'''


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