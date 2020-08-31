class SpotifyLocationRequest():

    def __init__(self, request):
        self.latitude = request.form['latitude']
        self.longitude = request.form['longitude']
        self.radius = request.form['radius']

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self,value):
        self._latitude = value

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self,value):
        self._longitude = value

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self,value):
        self._radius = value

    



    
    