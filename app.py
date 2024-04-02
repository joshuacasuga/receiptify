from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from time import gmtime, strftime
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
    try:
        user_token = get_token()
        sp = spotipy.Spotify(auth = user_token['access_token'])
    except:
        print("User has not logged in.")
        return redirect("/")
    return render_template('landing.html', title = 'Wrapped on Demand')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacypolicy')
def privacy():
    return render_template('privacy.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/tracks')
def tracks():
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

@app.route('/artists')
def artists():
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