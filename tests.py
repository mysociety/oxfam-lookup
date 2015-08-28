import json
import StringIO
import unittest

from mock import patch
from webtest import TestApp

from app import application
import countries
import settings


# TODO: This relies on the internet working
class TestURLs(unittest.TestCase):
    def setUp(self):
        self.app = TestApp(application)

    def test_bad_country(self):
        self.app.get('/postcode/ZZ/B302US', status=400)

    def test_bad_postcodes(self):
        self.app.get('/postcode/UK/B302ZZ', status=404)
        self.app.get('/postcode/UK/Nope', status=400)

    def test_postcodes(self):
        self.app.get('/postcode/UK/B302US')
        self.app.get('/postcode/AU/2136')
        self.app.get('/postcode/AU/2148')

    @patch('services.country.session')
    def test_address(self, session):
        session.get.return_value.json.return_value = {
            'statusCode': 200,
            'resourceSets': [{'resources': [
                {'name': 'Cannon Street, Manchester',
                 'address': {'countryRegion': 'United Kingdom'},
                 'point': {'coordinates': [51, 0]}}
            ]}],
        }
        resp = self.app.get('/address/UK/Cannon+Street+Manchester')
        data = json.loads(resp.body)
        self.assertEquals(data, {"representative": {
            "name": "Nusrat Ghani",
            "twitter": "Nus_Ghani",
            "facebook": None,
            "party": "Conservative",
            "constituency": "Wealden",
            "email": None
        }})

    @patch('services.country.session')
    def test_au_address(self, session):
        session.get.return_value.json.return_value = {
            'statusCode': 200,
            'resourceSets': [{'resources': [
                {'name': 'Cannon Street, Manchester',
                 'address': {'countryRegion': 'Australia'},
                 'point': {'coordinates': [-35.279651, 149.138427]}},
                {'name': 'Cannon Street, Adelaide',
                 'address': {'countryRegion': 'France'},
                 'point': {'coordinates': [-35.279651, 149.138427]}}
            ]}],
        }
        resp = self.app.get('/address/AU/Cannon+Street+Manchester')
        data = json.loads(resp.body)
        self.assertEqual(data, {"representative": {
            "name": "Hon Dr Andrew Leigh MP",
            "twitter": "https://twitter.com/ALEIGHMP",
            "facebook": "http://www.facebook.com/pages/Andrew-Leigh-MP/129819533748295",
            "party": "Australian Labor Party",
            "constituency": "Fraser, Australian Capital Territory",
            "email": "andrew.leigh.mp@aph.gov.au"
        }})

    @patch('services.country.session')
    def test_multiple_address(self, session):
        session.get.return_value.json.return_value = {
            'statusCode': 200,
            'resourceSets': [{'resources': [
                {'name': 'Cannon Street, Manchester',
                 'address': {'countryRegion': 'Australia'},
                 'point': {'coordinates': [-35.279651, 149.138427]}},
                {'name': 'Cannon Street, Adelaide',
                 'address': {'countryRegion': 'Australia'},
                 'point': {'coordinates': [-35.279651, 149.138427]}}
            ]}],
        }
        resp = self.app.get('/address/AU/Cannon+Street+Manchester')
        data = json.loads(resp.body)
        self.assertEqual(data, {"results": [
            {"latitude": -35.279651, "longitude": 149.138427, "address": "Cannon Street, Manchester"},
            {"latitude": -35.279651, "longitude": 149.138427, "address": "Cannon Street, Adelaide"}
        ]})

    @patch('services.country.session')
    def test_bad_address(self, session):
        session.get.return_value.json.return_value = {'statusCode': 401}
        self.app.get('/address/AU/Cannon+Street+Manchester', status=404)


class TestCountry(unittest.TestCase):
    def test_area_by_id(self):
        data = countries.AU().area_to_rep({'id': 'ocd-division/country:au/state:nsw/federal_electorate:mackellar'})
        self.assertEqual(data, {
            'name': u'Hon Bronwyn Bishop MP',
            'twitter': None,
            'facebook': None,
            'party': u'Liberal Party of Australia',
            'constituency': u'Mackellar, New South Wales',
            'email': u'Bronwyn.Bishop.MP@aph.gov.au'
        })


class TestConfig(unittest.TestCase):
    def test_non_dict_config(self):
        io = StringIO.StringIO("Test")
        with self.assertRaises(Exception):
            settings.load_config(io)

    def test_bad_yaml(self):
        io = StringIO.StringIO("Foo: Foo\nFoo")
        with self.assertRaises(Exception):
            settings.load_config(io)


if __name__ == '__main__':
    unittest.main()
