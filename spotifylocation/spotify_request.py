from dataclasses import dataclass

@dataclass
class SpotifyLocationRequest:
    def __init__(self, request):
        self.latitude = request.form["latitude"]
        self.longitude = request.form["longitude"]
        self.radius = request.form["radius"]
        self.genres = request.form.getlist("genres")

