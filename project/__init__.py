from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from .spotify_query import SpotifySparqlQuery
from . import sparql_query
import folium
import time
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import uuid
import reverse_geocode

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/tmp/.flask_session/'
Session(app)

caches_folder = '/tmp/.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

@app.route('/')
def home():
    print(request)
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-modify-private, playlist-modify-public',
                                                cache_path=session_cache_path(), 
                                                show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect(url_for('home'))

    if not auth_manager.get_cached_token():
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        print(auth_url)
        return redirect(auth_url)

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return redirect(url_for('map'))


#@app.route('/artist', methods=['GET','POST'])
def artist(name=None):
    if request.method == 'POST':
        artist = request.form['artist']
        #results = sparql_query.SparqlResultsFromArtist().query(artist)
        return render_template('artist.html', town="Town")

    return render_template('artist.html')

@app.route('/map', methods=['GET','POST'])
def map():
    spotify = check_authed()
    if spotify == None:
        return redirect(url_for('home'))
    if request.method == 'POST':
        print("post got")
        longitude = request.form['longitude']
        latitude = request.form['latitude']
        print("longitude: {longitude}, latitude: {latitude}".format(longitude=longitude, latitude=latitude))
        sp = SpotifySparqlQuery().createPlaylistFromCoordinates(spotify,latitude,longitude)
        print("sp")
        return redirect(url_for('results',playlist_id=sp))

    return render_template('map.html')
    

@app.route('/results')
def results():
    playlist_id = request.args.get('playlist_id')
    return render_template('results.html',playlist_id=playlist_id)

    

@app.route('/sign_out')
def sign_out():
    os.remove(session_cache_path())
    session.clear()
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
    except (TypeError,OSError):
        pass
    return redirect(url_for('home'))


@app.route('/callback/')
def callback():
    if request.args.get("code"):
        code_id = request.args.get("code")
        return redirect(url_for('home',code=code_id))

#@app.route('/playlists')
def playlists():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()


#@app.route('/currently_playing')
def currently_playing():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


#@app.route('/current_user')
def current_user():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()

def check_authed():
    try:
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    except TypeError:
        auth_manager=None
    try:
        if auth_manager.get_cached_token():
            spotify = spotipy.Spotify(auth_manager=auth_manager)
    except AttributeError:
        spotify = None
    return spotify