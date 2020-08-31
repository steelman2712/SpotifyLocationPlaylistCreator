class SpotifyLocationRequest():

    def __init__(self, request):
        self.latitude = request.form['latitude']
        self.longitude = request.form['longitude']
        self.filters_enabled = request.form['filters']

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
        return self._longitude

    @radius.setter
    def radius(self,value):
        self._radius = value

    @property
    def filters_enabled(self):
        return self._filters_enabled
    
    @filters_enabled.setter
    def filters_enabled(self, filters_enabled):
        if filters_enabled == True:
            self._filters_enabled = True
        else:
            self._filters_enabled = False


    
    