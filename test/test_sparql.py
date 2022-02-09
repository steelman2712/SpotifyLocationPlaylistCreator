from spotifylocation.sparql_query import SparqlResultsFromArtist, SparqlResultsFromCoordinates

def test_artist_query(mocker):
    expected_sparql_response = {"results":{"bindings":[{"placeLabel":{"value":"TestPlace"},"artistLabel":{"value":"TestArtist"}}]}}
    expected_query_response = [{"place":"TestPlace","artist":"TestArtist"}]
    ArtistResults = SparqlResultsFromArtist()
    mocker.patch("spotifylocation.sparql_query.SparqlResults.get_sparql_results", return_value = expected_sparql_response )
    query = ArtistResults.query("artist")
    assert query == expected_query_response

def test_location_query(mocker):
    expected_sparql_response = {"results":{"bindings":[{"placeLabel":{"value":"TestPlace"},"artistLabel":{"value":"TestArtist"}}]}}
    expected_query_response = [{"place":"TestPlace","artist":"TestArtist"}]
    ArtistResults = SparqlResultsFromCoordinates()
    mocker.patch("spotifylocation.sparql_query.SparqlResults.get_sparql_results", return_value = expected_sparql_response )
    query = ArtistResults.query(lat=0, long=0, radius=10, genres=[])
    assert query == expected_query_response
