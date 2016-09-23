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

class Pokemap(object):
  def __init__(self):
    pass

  def build_coord_url(self, lat, lng):
    url = list(urlparse.urlsplit("https://cache.fastpokemap.se/"))

    query_string = urllib.urlencode({
      "key": "allow-all",
      "ts": "0",
      "compute": "100.38.165.58",
      "lat": ("%.6f" % lat),
      "lng": ("%.6f" % lng),
    })

    url[3] = query_string
    return urlparse.urlunsplit(url)

  def build_cookies(self):
    return {
      "__cfduid": "defc59e78e21e3acea19f00c04bbbccb91473965777",
      "path":     "/",
      "domain":   ".fastpokemap.se",
      "httpOnly": "true"
    }

  def build_headers(self):
    return {
      "Accept":     "application/json, text/javascript, */*; q=0.01",
      "Connection": "keep-alive",
      "Host":       "cache.fastpokemap.se",
      "Origin":     "https://fastpokemap.se",
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"
    }

  def search_coord(self, lat, lng):
    url  = self.build_coord_url(lat, lng)
    resp = self.request_get(url)

    if type(resp) is dict:
      if "error" in resp:
        raise Error(resp["error"])

    return [ResultSet(r) for r in resp]

  def request_get(self, url):
    cookies = self.build_cookies()
    headers = self.build_headers()
    resp = requests.get(url, cookies=cookies, headers=headers)
    return resp.json()


