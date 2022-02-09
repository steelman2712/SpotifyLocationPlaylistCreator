import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from spotify_query import SpotifySparqlQuery
import spotify_request
import genres
import os
import spotipy
import uuid


app = Flask(__name__)

app.config["SECRET_KEY"] = os.urandom(64)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "/tmp/.flask_session/"
Session(app)

caches_folder = "/tmp/.spotify_caches/"
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


def session_cache_path():
    return caches_folder + session.get("uuid")


@app.before_first_request
def setup():
    global auth_manager 
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope="playlist-modify-private, playlist-modify-public",
        cache_path=session_cache_path(),
        show_dialog=True,
    )


@app.route("/")
def home():
    print(request)
    if not session.get("uuid"):
        # Step 1. Visitor is unknown, give random ID
        session["uuid"] = str(uuid.uuid4())

    if not auth_manager.get_cached_token():
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        print(auth_url)
        return redirect(auth_url)

    # Step 3. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return redirect(url_for("map"))


# @app.route('/artist', methods=['GET','POST'])
def artist(name=None):
    if request.method == "POST":
        artist = request.form["artist"]
        # results = sparql_query.SparqlResultsFromArtist().query(artist)
        return render_template("artist.html", place="place")

    return render_template("artist.html")


@app.route("/map", methods=["GET", "POST"])
def map():
    spotify = check_authed()
    mapbox_token = os.getenv("MAPBOX_TOKEN")
    if spotify is None:
        return redirect(url_for("home"))
    if request.method == "POST":
        print(request.form.getlist("genres"))
        request_object = spotify_request.SpotifyLocationRequest(request)
        print(request_object.__dict__)
        sp = SpotifySparqlQuery().createPlaylist(spotify, request_object)
        return redirect(url_for("results", playlist_id=sp))

    return render_template("map.html", filters=genres.GENRES, mapbox_token=mapbox_token)


@app.route("/results")
def results():
    playlist_id = request.args.get("playlist_id")
    print(playlist_id)
    return render_template("results.html", playlist_id=playlist_id)


@app.route("/sign_out")
def sign_out():
    os.remove(session_cache_path())
    session.clear()
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
    except (TypeError, OSError):
        pass
    return redirect(url_for("home"))


@app.route("/callback/")
def callback():
    if request.args.get("code"):
        code_id = request.args.get("code")
        auth_manager.get_access_token(code_id)
        return redirect(url_for("home", code=code_id))


# @app.route('/playlists')
def playlists():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect("/")

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()


# @app.route('/currently_playing')
def currently_playing():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect("/")
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if track is not None:
        return track
    return "No track currently playing."


# @app.route('/current_user')
def current_user():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    if not auth_manager.get_cached_token():
        return redirect("/")
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()


def check_authed():
    try:
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    except TypeError:
        auth_manager = None
    try:
        if auth_manager.get_cached_token():
            spotify = spotipy.Spotify(auth_manager=auth_manager)
    except AttributeError:
        spotify = None
    return spotify
