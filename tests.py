import unittest

from webtest import TestApp

from app import application
import countries


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


if __name__ == '__main__':
    unittest.main()
