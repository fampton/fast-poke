import mock
import unittest
import maps

class ResponseMock(object):
  def json(self):
    return {
      "routes": [
        {
          "legs": [
            {
              "duration": {
                "text":  "3 mins",
                "value": 159
              }
            },
          ]
        }
      ]
    }

  def raise_for_status(self):
    pass

class MapsTestCase(unittest.TestCase):
  @mock.patch("maps.requests.get")
  def test_directions(self, get_mock):
    get_mock.return_value = ResponseMock()

    maps_client = maps.Client("a valid api key")
    duration = maps_client.duration((40.735457, -73.991786),
                                    (40.764924, -73.972988))

    self.assertEqual(duration, 159)
