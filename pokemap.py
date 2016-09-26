import collections
import requests
import urllib
import urlparse

class ResultSet(object):
  def __init__(self, result):
    self.coordinates  = result["lnglat"]["coordinates"]
    self.encounter_id = result["encounter_id"]
    self.expire_at    = result["expireAt"]
    self.pokemon_id   = result["pokemon_id"]
    self.spawn_id     = result["spawn_id"]

class Error(Exception):
  pass

def search_coord(lat, lng):
  query_string = urllib.urlencode({
    "key": "allow-all",
    "ts": "0",
    "compute": "100.38.165.58",
    "lat": ("%.6f" % lat),
    "lng": ("%.6f" % lng),
  })

  url    = list(urlparse.urlsplit("https://cache.fastpokemap.se/"))
  url[3] = query_string
  url    = urlparse.urlunsplit(url)

  headers = {
    "Origin": "https://fastpokemap.se",
  }

  resp = requests.get(url, headers=headers)
  resp = resp.json()

  if type(resp) is dict:
    if "error" in resp:
      raise Error(resp["error"])

  return [ResultSet(r) for r in resp]
