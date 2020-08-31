import pep8
import qwikidata.sparql as wiki
import random
from halo import Halo
from . import genres as genre_list

class SparqlResults():
  SPARQL_RETRY_LIMIT = 2
  SPARQL_ARTIST_RETURN_LIMIT = 20
  sparql_results = {"town":"No town found", "artist":"No artist found"}

  def set_retry_limit(self, retry_limit):
    self.SPARQL_RETRY_LIMIT=retry_limit

  def get_sparql_results(self, raw_sparql_query):
    attempts = 0
    while attempts<=self.SPARQL_RETRY_LIMIT:
      try:
        res = wiki.return_sparql_query_results(raw_sparql_query)
        return(res)
      except:
        attempts = attempts+1
  
  def getTown(self,sparql_results):
        return sparql_results[0].get("placeLabel").get("value")
        
  def parseResults(self, sparql_results):
    parsed_results = []
    print(sparql_results)
    for result in sparql_results:
      town = result.get("placeLabel").get("value")
      artist = result.get("artistLabel").get("value")
      parsed_results.append({"town":town,"artist":artist})
    self.sparql_results = parsed_results

  def createGenreFilter(self,genres):
    genre_filter=""
    if genres == []:
      genre_filter="wd:Q37073"
    else:
      for item in genres:
        genre_filter = genre_filter+" "+ genre_list.GENRES[item]
    return genre_filter

class SparqlResultsFromArtist(SparqlResults):

  def query(self, artist):
    spinner = Halo(text='Sending query', spinner='line')
    spinner.start()
    random_int = random.uniform(0,100)
    raw_sparql_query = f"""
    SELECT DISTINCT ?townLabel ?artist ?artistLabel (MD5(CONCAT(str(?artist),str({random_int}))) as ?random) WHERE {{
      {{
        ?artist wdt:P19 ?town.  
        ?artist (wdt:P106/(wdt:P279*)) wd:Q2643890.
        ?artist wdt:P31 wd:Q5.
        ?artist wikibase:sitelinks ?sitelinks .
      }}
      UNION
      {{
        ?artist wdt:P740 ?town.
        ?artist wikibase:sitelinks ?sitelinks .  
      }}
      
      
      {{
        ?artistA wdt:P19 ?town.  
        ?artistA (wdt:P106/(wdt:P279*)) wd:Q2643890.
        ?artistA wdt:P31 wd:Q5.
      }}
      UNION
      {{
        ?artistA wdt:P740 ?town.
        ?artistA (wdt:P31/(wdt:P279*)) wd:Q215380.
      }}
        ?artistA ?label "{artist}"@en .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
      FILTER (?sitelinks > 2)
    }}
    ORDER BY ?random
    LIMIT {super().SPARQL_ARTIST_RETURN_LIMIT}
    """
    res = super().get_sparql_results(raw_sparql_query)
    results = res.get('results').get("bindings")
    spinner.stop()
    super().parseResults(results)
    return self.sparql_results

 
class SparqlResultsFromCoordinates(SparqlResults):


  def query(self, lat, long, radius=10, genres=[]):
    print("Query received")
    spinner = Halo(text='Sending query', spinner='line')
    spinner.start()
    genre_filter = super().createGenreFilter(genres)
    print(genre_filter)
    raw_sparql_query = f"""
      SELECT DISTINCT ?artistLabel ?placeLabel ?location (MD5(CONCAT(str(?artist),str(5))) as ?random) WHERE {{
      hint:Query hint:optimizer "None".
      VALUES ?professions {{wd:Q177220 wd:Q639669}}
      VALUES ?genres {{ {genre_filter} }}
      SERVICE wikibase:around {{
        ?place wdt:P625 ?location.
        bd:serviceParam wikibase:center "Point({long} {lat})"^^geo:wktLiteral;
        wikibase:radius "{radius}".
      }}
      ?place wdt:P31/wdt:P279 wd:Q486972 .
      
      {{
        ?artist wdt:P19 ?place.  
        ?artist wdt:P106 ?professions.
        ?artist wdt:P31 wd:Q5.
      }}
      UNION
      {{
        ?artist wdt:P740 ?place.
        {{?artist wdt:P31 wd:Q215380.}}
        UNION
        {{?artist wdt:P31/wdt:P279 wd:Q215380.}}
      }}
      
      ?artist wdt:P136/wdt:P279* ?genres .
      ?artist wikibase:statements ?statementcount .
      FILTER (?statementcount > 5 ) .

      ?artist rdfs:label ?artistLabel. FILTER( LANG(?artistLabel)="en" )
      ?place rdfs:label ?placeLabel. FILTER( LANG(?placeLabel)="en" )
      }}
      ORDER BY ?random
      LIMIT {super().SPARQL_ARTIST_RETURN_LIMIT}
    """
    res = super().get_sparql_results(raw_sparql_query)
    results = res.get('results').get("bindings")
    spinner.stop()
    super().parseResults(results)
    return self.sparql_results
    