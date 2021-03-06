#!/usr/bin/env python

import collections
import folium
import redis

from geopy.distance import vincenty

ResultSet = collections.namedtuple("ResultSet", [
  "coordinates",
  "encounter_id",
  "expire_at",
  "pokemon_id",
  "spawn_id"
])

r = redis.StrictRedis(host='nyc.fanp.co', port=21217, db=2)

def coord_formatted(myresultset):
    return tuple(eval(myresultset).coordinates)[::-1]

work = (40.735457, -73.991786)
mypokecoordinates = []

for i in r.keys():
    try:
        mypokecoordinates.append(coord_formatted(r.get(i)))
    except:
        pass

 function to get distance in miles from giving point to pokemon
for poke in mypokecoordinates[0:1000]:
    print(vincenty(poke, work).miles)

for i in mypokecoordinates[0:400]:
  folium.Marker(list(i)).add_to(workmap)

#view this map at http://nyc.fanp.co
workmap.save('/var/www/index.html')
