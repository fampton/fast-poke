import collections
import requests
import urllib
import urlparse

ResultSet = collections.namedtuple("ResultSet", [
  "coordinates",
  "encounter_id",
  "expire_at",
  "pokemon_id",
  "spawn_id"
])

def dict_to_result_set(data):
  return ResultSet(
    data["lnglat"]["coordinates"],
    data["encounter_id"],
    data["expireAt"],
    data["pokemon_id"],
    data["spawn_id"]
  )

class Error(Exception):
  pass

def search_coord(lat, lng):
  url = list(urlparse.urlsplit("https://cache.fastpokemap.se/"))

  query_string = urllib.urlencode({
    "key": "allow-all",
    "ts": "0",
    "compute": "100.38.165.58",
    "lat": ("%.6f" % lat),
    "lng": ("%.6f" % lng),
  })

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

  return [dict_to_result_set(r) for r in resp]
