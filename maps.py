import collections
import requests
import urllib
import urlparse

class Client(object):
  def __init__(self, api_key):
    self.api_key = api_key

  def duration(self, origin, dest):
    query_string = urllib.urlencode({
      "origin":      ("%.6f,%.6f" % (origin[0], origin[1])),
      "destination": ("%.6f,%.6f" % (  dest[0],   dest[1])),
      "mode":        "walking",
      "key":         self.api_key
    })

    url    = list(urlparse.urlsplit("https://maps.googleapis.com"))
    url[2] = "/maps/api/directions/json"
    url[3] = query_string
    url    = urlparse.urlunsplit(url)

    resp = requests.get(url)
    resp.raise_for_status()
    resp = resp.json()

    return resp["routes"][0]["legs"][0]["duration"]["value"]
