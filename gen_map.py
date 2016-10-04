#!/usr/bin/env python

import folium
import redis
import sys

def gen_map(mypoke):
  r = redis.StrictRedis(host='nyc.fanp.co', port=21217, db=2)
  
  work = (40.735457, -73.991786)
  mypokecoordinates = []
  
  def coords_by_poke(pokename):
    for i in r.zrange(pokename, 0, -1):
      mypokecoordinates.append(r.execute_command('GEOPOS', pokename, i)[0])
  
  coords_by_poke(mypoke.upper())
  workmap = folium.Map(location=list(work), zoom_start=13)
  
  for i in mypokecoordinates:
          folium.Marker(list(i)).add_to(workmap)
  
  #view this map at http://nyc.fanp.co
  workmap.save('/var/www/index.html')

def main():
  gen_map(sys.argv[1])

if __name__ == '__main__':
	main()

