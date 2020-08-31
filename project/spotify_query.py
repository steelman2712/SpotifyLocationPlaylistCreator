
import pep8
import spotipy
import sys
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import random
from . import sparql_query as sparql
import flask 
import reverse_geocode

class SpotifyQueryBase():

    def getTracksFromArtist(self,spotify_session,artistId):
        trackList = []
        topTracksSearch = spotify_session.artist_top_tracks(artist_id=artistId)
        topTracks = topTracksSearch.get("tracks")
        for track in topTracks:
            trackList.append(track.get("id"))
        return trackList

    def getArtistId(self,spotify_session,artist):
        search = spotify_session.search(artist,limit=10,type="artist")
        artistSpotifyList = search.get("artists").get("items")
        for spotifyArtist in artistSpotifyList:
            spotifyName = spotifyArtist.get("name")
            if spotifyName == artist:
                return spotifyArtist.get("id")

    def getTrackList(self,spotify_session,artists):
        trackIds = []
        for artist in artists:
            artistId = self.getArtistId(spotify_session,artist)
            if artistId != None:
                artistTrackIds = self.getTracksFromArtist(spotify_session,artistId)
                trackIds.extend(artistTrackIds)
        return trackIds

    def isSpotifySearchNotEmpty(self,searchResult):
        if searchResult.get("tracks").get("items") != []:
            return True
        else:
            return False

    def getTrackIdsForArtistSearch(self,search):
            artistTrackIds = []
            trackSearch = search.get("tracks").get("items")
            for track in trackSearch:
                artistTrackIds.append(track.get("id"))
            return artistTrackIds    

class SpotifyPlaylistUtils(SpotifyQueryBase):
    
    def createPlaylistFromArtistList(self, spotify_session, artists, name = "Playlist", description = "", public="False"):
        sp = spotify_session
        username = sp.current_user().get("id")
        tracklist = super().getTrackList(spotify_session,artists)
        chunked_tracklist = [tracklist[i:i + 99] for i in range(0, len(tracklist), 99)]
        playlist = sp.user_playlist_create(user=username,name=name,public=public,description=description)
        playlistId = playlist.get("id")
        for chunks in chunked_tracklist:
            print(len(chunks))
            sp.user_playlist_add_tracks(user=username,playlist_id=playlistId,tracks=chunks)
        return playlistId



class SpotifySparqlQuery(SpotifyPlaylistUtils):
    
    def createPlaylist(self, spotify_session, request):
        if request.latitude and request.longitude:
            return self.createPlaylistFromCoordinates(spotify_session, request)

    def createPlaylistFromArtist(self,spotify_session,artist):
        results = sparql.SparqlResultsFromArtist().query(artist)
        artists = [result["artist"] for result in results]
        town = results[0]["town"]
        description = "A playlist containing songs by bands from the same town as {artist}".format(artist=artist)
        playlist_id = super().createPlaylistFromArtistList(spotify_session, artists, name=town,description=description,public=True)
        return playlist_id

    def createPlaylistFromCoordinates(self, spotify_session, request):
        sparql_query = sparql.SparqlResultsFromCoordinates()
        print(request.latitude)
        sparql_query.query(request.latitude, request.longitude)
        artists = [result["artist"] for result in sparql_query.sparql_results]
        coordinates = (request.latitude,request.longitude), 
        location = reverse_geocode.search(coordinates)
        name = location[0].get("city")+", "+location[0].get("country")
        description = "A set of songs from around "+name
        playlist_id = super().createPlaylistFromArtistList(spotify_session, artists,name=name, description=description)
        print(playlist_id)
        return playlist_id