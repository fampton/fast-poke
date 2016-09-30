#!/usr/bin/env python

import datetime
import iso8601
import itertools
import redis
import sys

# import api configs
import config
import ph_missing
import pokemap
import maps

from twilio.rest import TwilioRestClient

#import gapi_key
gapi_key = config.gapi_key

# Twilio account config
accountSID = config.twilio_sid
authToken = config.twilio_token

twilioCli = TwilioRestClient(accountSID, authToken)
myTwilioNumber = config.myTwilioNumber
myCellPhone = config.myCellPhone

# work gps
unsq = (40.735457, -73.991786)

# central park south gps
cnt_park_s = (40.764924, -73.972988)

# home gps
bshwk_home = (40.702667, -73.919722)

# This is super clunky I know, ultimately this app should rely on device gps
# set mylat and mylong to be used in requests call
# defaults to work gps
if len(sys.argv) == 1:
  mylat = unsq[0]
  mylong = unsq[1]
  myloc = 'work'
elif sys.argv[1] == 'work':
  mylat = unsq[0]
  mylong = unsq[1]
  myloc = 'work'
elif sys.argv[1] == 'cps':
  mylat = cnt_park_s[0]
  mylong = cnt_park_s[1]
  myloc = 'cps'
elif sys.argv[1] == 'home':
  mylat = bshwk_home[0]
  mylong = bshwk_home[1]
  myloc = 'home'

# list of missing pokemon as of 16Sep
missing_poke = ph_missing.missing_poke

# Pokedex name/number map
pokedex = {
  'Abra': 63, 'Aerodactyl': 142, 'Alakazam': 65, 'Arbok': 24, 'Arcanine': 59, 'Articuno': 144, 'Beedrill': 15, 'Bellsprout': 69, 'Blastoise': 9, 'Bulbasaur': 1, 'Butterfree': 12, 'Caterpie': 10, 'Chansey': 113, 'Charizard': 6, 'Charmander': 4, 'Charmeleon': 5, 'Clefable': 36, 'Clefairy': 35, 'Cloyster': 91, 'Cubone': 104, 'Dewgong': 87, 'Diglett': 50, 'Ditto': 132, 'Dodrio': 85, 'Doduo': 84, 'Dragonair': 148, 'Dragonite': 149, 'Dratini': 147, 'Drowzee': 96, 'Dugtrio': 51, 'Eevee': 133, 'Ekans': 23, 'Electabuzz': 125, 'Electrode': 101, 'Exeggcute': 102, 'Exeggutor': 103, "Farfetch'd": 83, 'Fearow': 22, 'Flareon': 136, 'Gastly': 92, 'Gengar': 94, 'Geodude': 74, 'Gloom': 44, 'Golbat': 42, 'Goldeen': 118, 'Golduck': 55, 'Golem': 76, 'Graveler': 75, 'Grimer': 88, 'Growlithe': 58, 'Gyarados': 130, 'Haunter': 93, 'Hitmonchan': 107, 'Hitmonlee': 106, 'Horsea': 116, 'Hypno': 97, 'Ivysaur': 2, 'Jigglypuff': 39, 'Jolteon': 135, 'Jynx': 124, 'Kabuto': 140, 'Kabutops': 141, 'Kadabra': 64, 'Kakuna': 14, 'Kangaskhan': 115, 'Kingler': 99, 'Koffing': 109, 'Krabby': 98, 'Lapras': 131, 'Lickitung': 108, 'Machamp': 68, 'Machoke': 67, 'Machop': 66, 'Magikarp': 129, 'Magmar': 126, 'Magnemite': 81, 'Magneton': 82, 'Mankey': 56, 'Marowak': 105, 'Meowth': 52, 'Metapod': 11, 'Moltres': 146, 'Mr.Mime': 122, 'Muk': 89, 'Nidoking': 34, 'Nidoqueen': 31, 'Nidoran_Male': 29, 'Nidoran_Female': 32, 'Nidorina': 30, 'Nidorino': 33, 'Ninetales': 38, 'Oddish': 43, 'Omanyte': 138, 'Omastar': 139, 'Onix': 95, 'Paras': 46, 'Parasect': 47, 'Persian': 53, 'Pidgeot': 18, 'Pidgeotto': 17, 'Pidgey': 16, 'Pikachu': 25, 'Pinsir': 127, 'Poliwag': 60, 'Poliwhirl': 61, 'Poliwrath': 62, 'Ponyta': 77, 'Porygon': 137, 'Primeape': 57, 'Psyduck': 54, 'Raichu': 26, 'Rapidash': 78, 'Raticate': 20, 'Rattata': 19, 'Rhydon': 112, 'Rhyhorn': 111, 'Sandshrew': 27, 'Sandslash': 28, 'Scyther': 123, 'Seadra': 117, 'Seaking': 119, 'Seel': 86, 'Shellder': 90, 'Slowbro': 80, 'Slowpoke': 79, 'Snorlax': 143, 'Spearow': 21, 'Squirtle': 7, 'Starmie': 121, 'Staryu': 120, 'Tangela': 114, 'Tauros': 128, 'Tentacool': 72, 'Tentacruel': 73, 'Vaporeon': 134, 'Venomoth': 49, 'Venonat': 48, 'Venusaur': 3, 'Victreebel': 71, 'Vileplume': 45, 'Voltorb': 100, 'Vulpix': 37, 'Wartortle': 8, 'Weedle': 13, 'Weepinbell': 70, 'Weezing': 110, 'Wigglytuff': 40, 'Zapdos': 145, 'Zubat': 41
}

revpokedex = dict((v,k) for k,v in pokedex.iteritems())

# Configure redis connection
r = redis.StrictRedis(host='localhost', port=21217, db=1)
remote_redis = redis.StrictRedis(host='nyc.fanp.co', port=21217, db=2)

# Example poke object
# {"pokemon_id":"PIDGEY","lnglat":{"type":"Point","coordinates":[-73.99195579345653,40.73548518715059]},"encounter_id":"8900503607140605597","spawn_id":"89c25998605","expireAt":"2016-09-15T21:22:25.844+02:00"}

# make request to fastpokemap api
# returns list (in string form) of pokemon objects as seen in example above
def get_data(mylat, mylong):
  return pokemap.search_coord(mylat, mylong)

# parse list for pokemon names mapped from pokedex dict
def list_nearby(mylist):
  sort_by = lambda x: x.pokemon_id
  xs = sorted(mylist, key=sort_by)

  print('Nearby Pokemon:'+'\n')
  for value, group in itertools.groupby(xs, lambda x: x.pokemon_id):
    print(value, len(list(group)))

# check nearby pokemon for any that I do not have
def check_for_missing(mylist):
  mypokelist = []
  for i in mylist:
    # because my missing poke list is by id and the data we get from fastpokemaps.se gives names we lookup number via mapping
    if pokedex[i.pokemon_id.title()] in missing_poke:
      mydistance = get_walking_time(i)
      # check redis to see if we have already seen this poke, so that we don't send sms for previous pokemon
      if r.exists(i.encounter_id):
        mypokelist.append((i.pokemon_id, pokedex[i.pokemon_id.title()], gmap_url(i), poke_time_left(i), mydistance))
        pass
      else:
        mypokelist.append((i.pokemon_id, pokedex[i.pokemon_id.title()], gmap_url(i), poke_time_left(i), mydistance, 'new'))
        r.set(i.encounter_id, i.coordinates)
        r.expire(i.encounter_id, poke_time_left(i))
    else:
      if not remote_redis.exists(i.encounter_id):
        remote_redis.set(i.encounter_id, i)
      pass
  return mypokelist

def gmap_url(mypokemon):
  mylat = mypokemon.coordinates[1]
  mylng = mypokemon.coordinates[0]
  return 'http://www.google.com/maps/place/{},{}'.format(mylat, mylng)


def duration_until(expire_at):
  expire_dt  = iso8601.parse_date(expire_at)
  current_dt = datetime.datetime.now(expire_dt.tzinfo)

  if current_dt < expire_dt:
    return expire_dt - current_dt
  else:
    return datetime.timedelta()

def poke_time_left(mypokemon):
  duration = duration_until(mypokemon.expire_at)
  return duration.seconds

def send_sms(poke_id, mypokemon, myexpiry):
  # should combine poke_id, mypokemon and myexpiry to be sourced from one object
  message = twilioCli.messages.create(body='{} at {} expiring at {}'.format(poke_id, gmap_url(mypokemon), myexpiry), from_=myTwilioNumber, to=myCellPhone)
  print('SMS sent')

#gapi response json
#jq '.routes[0] .legs[0] .duration.value'
def get_walking_time(mypokemon):
  maps_client = maps.Client(gapi_key)
  coord = mypokemon.coordinates
  duration = maps_client.duration((mylat, mylong), (coord[1], coord[0]))

  return duration / 60

def main():
  mydata = get_data(mylat, mylong)
  list_nearby(mydata)
  mycheck = check_for_missing(mydata)
  for i in mycheck:
    if 'new' in i:
      print('Found NEW one!', i[0], pokedex[i[0].title()], i[2], 'expires in', i[3], 'seconds. Walking duration', i[4])
      message = twilioCli.messages.create(body='{} {} at {} expiring in {}, travel time {} min'.format(i[0], pokedex[i[0].title()], i[2], i[3], i[4]), from_=myTwilioNumber, to=myCellPhone)
    else:
      print('Found one!', i[0], pokedex[i[0].title()], i[2], 'expires in', i[3], 'seconds. Walking duration', i[4])

if __name__ == '__main__':
	main()
