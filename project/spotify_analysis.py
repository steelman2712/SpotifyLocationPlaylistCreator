import spotipy

def getTracksAudioFeatures(tracklist):
    chunked_tracklist = [tracklist[i:i + 99] for i in range(0, len(tracklist), 99)]
    audio_features = []
    for chunk in chunked_tracklist:
        chunk_analysis = spotipy.audio_features(chunk)
        audio_features.append(chunk_analysis)
    return audio_features