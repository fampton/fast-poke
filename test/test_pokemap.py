import mock
import unittest
import pokemap

class ResponseMock(object):
  def json(self):
    return [{
      "spawn_id":     "5f7af7a317de4d6eabe6bf599050c269.12",
      "pokemon_id":   "CUBONE",
      "encounter_id": "1823752155",
      "expireAt":     "2016-09-23T17:10:56.386+02:00",

      "lnglat":       {
                        "type":        "Point",
                        "coordinates": [-73.973064,40.764799]
                      }
    },{
      "spawn_id":     "fd03a8b6431a4009a6ce77df74f1f6ea.16",
      "pokemon_id":   "SHELLDER",
      "encounter_id": "18446744073364944820",
      "expireAt":     "2016-09-23T17:10:11.705+02:00",

      "lnglat":       {
                        "type":        "Point",
                        "coordinates": [-73.972766,40.765169]
                      }
    }]

class ErrorResponseMock(object):
  def json(self):
    return {
      "error": "Something went wrong"
    }


class PokemapTestCase(unittest.TestCase):
  def setUp(self):
    self.pokemap = pokemap.Pokemap()

  @mock.patch("pokemap.requests.get")
  def test_search_coord(self, get_mock):
    get_mock.return_value = ResponseMock()

    resp  = self.pokemap.search_coord(40.764924, -73.972988)
    first = resp[0]
    self.assertEqual(first.coordinates,  [-73.973064,40.764799])
    self.assertEqual(first.encounter_id, "1823752155")
    self.assertEqual(first.expire_at,    "2016-09-23T17:10:56.386+02:00")
    self.assertEqual(first.pokemon_id,   "CUBONE")
    self.assertEqual(first.spawn_id,     "5f7af7a317de4d6eabe6bf599050c269.12")
    self.assertEqual(len(resp),          2)

  @mock.patch("pokemap.requests.get")
  def test_search_coord_error(self, get_mock):
    get_mock.return_value = ErrorResponseMock()

    with self.assertRaises(pokemap.Error) as ctx:
      resp = self.pokemap.search_coord(40.764924, -73.972988)

    self.assertEqual(str(ctx.exception), "Something went wrong")

