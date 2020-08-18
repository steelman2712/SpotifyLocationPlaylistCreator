import pep8
import qwikidata.sparql as wiki
import random
from halo import Halo


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
        return sparql_results[0].get("townLabel").get("value")
        
  def parseResults(self, sparql_results):
    parsed_results = []
    for result in sparql_results:
      town = result.get("townLabel").get("value")
      artist = result.get("artistLabel").get("value")
      parsed_results.append({"town":town,"artist":artist})
    self.sparql_results = parsed_results


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


  def query(self, lat, long, radius=10):
    spinner = Halo(text='Sending query', spinner='line')
    spinner.start()
    raw_sparql_query = f"""
      SELECT DISTINCT ?artistLabel ?townLabel ?location WHERE {{
      hint:Query hint:optimizer "None".
      SERVICE wikibase:around {{
        ?town wdt:P625 ?location.
        bd:serviceParam wikibase:center "Point({long} {lat})"^^geo:wktLiteral;
        wikibase:radius "{radius}".
      }}
      ?town wdt:P31/wdt:P279* wd:Q486972 .
      
      {{
        ?artist wdt:P19 ?town.  
        ?artist (wdt:P106/(wdt:P279*)) wd:Q2643890.
        ?artist wdt:P31 wd:Q5.
        ?artist wikibase:sitelinks ?sitelinks .
      }}
      UNION
      {{
        ?artist wdt:P740 ?town.
        ?artist (wdt:P31/(wdt:P279*)) wd:Q215380.
        ?artist wikibase:sitelinks ?sitelinks .  
      }}
      
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
      FILTER (?sitelinks > 2)
    }}
    LIMIT {super().SPARQL_ARTIST_RETURN_LIMIT}
    """
    res = super().get_sparql_results(raw_sparql_query)
    results = res.get('results').get("bindings")
    spinner.stop()
    super().parseResults(results)
    print(self.sparql_results)
    return self.sparql_results
    