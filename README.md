# SpotifyLocationPlaylistCreator
Create Spotify playlist from a map within a webapp. 

# Setup
Create a Spotify Developers account and create a new application. Set up a callback url in the edit settings section, e.g http://localhost:5000/callback

# Environment variables
SPOTIPY_CLIENT_ID = The client ID of the spotify application \
SPOTIPY_CLIENT_SECRET = The client secret of the spotify application \
SPOTIPY_REDIRECT_URI = The callback URL you want to use \
MAPBOX_TOKEN = The public mapbox token (from https://account.mapbox.com/access-tokens/, only public token scopes are needed) \