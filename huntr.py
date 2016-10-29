#!/usr/bin/env python

import requests
from ignore_these import ignore

orig_lat = '40.735447'
orig_lng = ' -73.991786'

def poke_call():
  myurl = 'https://pokehuntr.com/api/'
  myheader = {'referer':'https://pokehuntr.com/'} 
  mycookies = {'timeChecker':'1477673475','hashCheck':'24e7d7e7b43205ac350784e57c7e1b21','location':'40.73648%2C+-73.99076'}
  myget = requests.get(myurl, headers=myheader, cookies=mycookies)
  myresponse = myget.json()
  return myresponse

def dist_check():
  from geopy.distance import vincenty
  rare = []
  pdist = {}
  for i in poke_call()['pokemons']:
    lng = i['longitude']
    lat = i['latitude']
    #if i['pokemon_rarity'] in ['Rare','Very Rare']:
    if i['pokemon_id'] not in ignore:
      distance = vincenty((orig_lat,orig_lng),(lat,lng)).miles
      #print distance
      rare.append(i['pokemon_name'])
      if i['pokemon_name'] not in pdist.keys():
        pdist[i['pokemon_name']] = distance
      else:
        if distance < pdist[i['pokemon_name']]:
          pdist[i['pokemon_name']] = distance
  #for i in set(rare):
  #  print i, rare.count(i)#, str(pdist[i['pokemon_name']])
  for i in pdist.keys():
    print i, '{:0.2f}'.format(pdist[i])+'m'

if __name__ == '__main__':
  dist_check()
