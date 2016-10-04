#!/usr/bin/env python

import argparse
import datetime
import iso8601
import itertools
import redis
import sys
import time

# import local configs
import config
import maps
import myloc
import notify
import ph_missing
import pokemap
import pokedex

from twilio.rest import TwilioRestClient

#import gapi_key
gapi_key = config.gapi_key

# Twilio account config
accountSID = config.twilio_sid
authToken = config.twilio_token

twilioCli = TwilioRestClient(accountSID, authToken)
myTwilioNumber = config.myTwilioNumber
myCellPhone = config.myCellPhone

notify = notify.notify

parser = argparse.ArgumentParser(description='Get notifications for given location.')
parser.add_argument('-n', '--notify', help='Send SMS for location.', action='store_true', default=False)
args = parser.parse_args()

loc_dict = {
'work':(40.735457, -73.991786),
'cps':(40.764924, -73.972988),
'home':(40.702667, -73.919722),
'tmsq':(40.758732, -73.985217),
'ppprk':(40.665995, -73.970354),
'bbprk':(40.702729, -73.995815),
'les':(40.719457, -73.987170),
'uws':(40.785426, -73.975863),
'ues':(40.775160, -73.951739),
'hrlm':(40.806965, -73.948888),
'hldtn':(40.724185, -74.007070),
}

# list of missing pokemon as of 16Sep
missing_poke = ph_missing.missing_poke

# Pokedex name/number map
pokedex = pokedex.pokedex

revpokedex = dict((v,k) for k,v in pokedex.iteritems())

# Configure redis connection
r = redis.StrictRedis(host='localhost', port=21217, db=1)
remote_redis = redis.StrictRedis(host='nyc.fanp.co', port=21217, db=2)

# Example poke object
# {"pokemon_id":"PIDGEY",
#  "lnglat":{"type":"Point","coordinates":[-73.99195579345653,40.73548518715059]},
#  "encounter_id":"8900503607140605597",
#  "spawn_id":"89c25998605",
#  "expireAt":"2016-09-15T21:22:25.844+02:00"}

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
def check_for_missing(mylist, mylat, mylng):
  mypokelist = []
  for i in mylist:
    # because missing poke list is by id and the data we get from fastpokemaps.se gives names we lookup number via mapping
    if pokedex[i.pokemon_id.title()] in missing_poke:
      #mydistance = get_walking_time(i)
      mydistance = 'NA'
      # check redis to see if we have already seen this poke, so that we don't send sms for previous pokemon
      if r.exists(i.encounter_id):
        mypokelist.append((i.pokemon_id, pokedex[i.pokemon_id.title()], gmap_url(i, mylat, mylng), poke_time_left(i), mydistance))
        pass
      else:
        mypokelist.append((i.pokemon_id, pokedex[i.pokemon_id.title()], gmap_url(i, mylat, mylng), poke_time_left(i), mydistance, 'new'))
        r.set(i.encounter_id, i.coordinates)
        r.expire(i.encounter_id, poke_time_left(i))
        remote_redis.set(i.encounter_id, i)
        remote_redis.execute_command('GEOADD', i.pokemon_id, i.coordinates[1], i.coordinates[0], i.encounter_id)
    else:
      if not remote_redis.exists(i.encounter_id):
        remote_redis.set(i.encounter_id, i)
        remote_redis.execute_command('GEOADD', i.pokemon_id, i.coordinates[1], i.coordinates[0], i.encounter_id)
      pass
  return mypokelist

def gmap_url(mypokemon, mylat, mylng):
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

# currently unused
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
  for loc in loc_dict.keys():
    try:
      mylat = loc_dict[loc][0]
      mylong = loc_dict[loc][1]
      print loc, mylat, mylong
      mydata = get_data(mylat, mylong)
      list_nearby(mydata)
      mycheck = check_for_missing(mydata, mylat, mylong)
      for i in mycheck:
        if 'new' in i:
          print('Found NEW one!', i[0], pokedex[i[0].title()], i[2], 'expires in', i[3], 'seconds. Walking duration', i[4])
          # replace this with a call to the send_sms() function
          if notify == loc:
            message = twilioCli.messages.create(body='{} {} at {} expiring in {}, travel time {} min'.format(i[0], pokedex[i[0].title()], i[2], i[3], i[4]), from_=myTwilioNumber, to=myCellPhone)
        else:
          print('Found one!', i[0], pokedex[i[0].title()], i[2], 'expires in', i[3], 'seconds. Walking duration', i[4])
      time.sleep(1)
    except:
      print 'error'

if __name__ == '__main__':
	main()
