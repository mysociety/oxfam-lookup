import StringIO
import unittest

from mock import patch, MagicMock
from webtest import TestApp
import falcon
import flake8.main.application

from app import application, Lookup
from services.popolo import Person
import countries
import settings


OCD_ID = 'ocd-division/country:au/state:nsw/federal_electorate:%s'


class TestURLs(unittest.TestCase):
    def setUp(self):
        self.app = TestApp(application)

    def test_bad_country(self):
        self.app.get('/postcode/ZZ/B302US', status=400)

    @patch('services.mapit.session')
    def test_unknown_postcode(self, mapit_session):
        mapit_session.get.return_value.json.return_value = {'code': 404, 'error': 'Postcode not found'}
        mapit_session.get.return_value.status_code = 404
        self.app.get('/postcode/UK/B302ZZ', status=404)

    @patch('services.mapit.session')
    def test_unknown_au_postcode(self, mapit_session):
        mapit_session.get.return_value.json.return_value = {}
        mapit_session.get.return_value.status_code = 200
        self.app.get('/postcode/AU/B302ZZ', status=404)

    @patch('services.mapit.session')
    def test_invalid_postcode(self, mapit_session):
        mapit_session.get.return_value.json.return_value = {'code': 400, 'error': 'Postcode invalid'}
        mapit_session.get.return_value.status_code = 400
        self.app.get('/postcode/UK/Nope', status=400)

    @patch('services.mapit.session')
    def test_good_uk_postcode(self, mapit_session):
        mapit_session.get.return_value.json.return_value = {"areas": {"65804": {
            "id": 65804,
            "codes": {"gss": "E14000567", "unit_id": "24692"},
            "name": "Birmingham, Selly Oak",
            "country": "E",
            "type": "WMC"
        }}}
        self.app.get('/postcode/UK/B302US')

    @patch('services.mapit.session')
    def test_unique_au_postcode(self, mapit_session):
        def au_mapit(url):
            mock = MagicMock()
            if 'pc' in url:
                mock.json.return_value = {"800": {"name": "pc2136", "country": "AU", "type": "POA"}}
            elif 'covered' in url:
                mock.json.return_value = {
                    "106": {"codes": {"ocd": OCD_ID % "watson"}, "name": "Watson", "country": "AU", "type": "CED"}
                }
            return mock
        mapit_session.get.side_effect = au_mapit
        self.app.get('/postcode/AU/2136')

    @patch('services.mapit.session')
    def test_nonunique_au_postcode(self, mapit_session):
        def au_mapit(url):
            mock = MagicMock()
            if 'pc' in url:
                mock.json.return_value = {"2257": {"name": "pc2148", "country": "AU", "type": "POA"}}
            elif 'covered' in url:
                mock.json.return_value = {}
            elif 'coverlaps' in url:
                mock.json.return_value = {
                    "111": {"codes": {"ocd": OCD_ID % 'mcmahon'}, "name": "McMahon", "type": "CED"},
                    "17": {"codes": {"ocd": OCD_ID % 'chifley'}, "name": "Chifley", "type": "CED"},
                    "31": {"codes": {"ocd": OCD_ID % 'greenway'}, "name": "Greenway", "type": "CED"}
                }
            return mock
        mapit_session.get.side_effect = au_mapit
        self.app.get('/postcode/AU/2148')

    @patch('countries.UK.area_to_rep')
    @patch('services.mapit.session')
    @patch('services.country.session')
    def test_address(self, session, mapit_session, area_to_rep):
        session.get.return_value.json.return_value = {
            'statusCode': 200,
            'resourceSets': [{'resources': [
                {'name': 'Cannon Street, Manchester',
                 'address': {'countryRegion': 'United Kingdom'},
                 'point': {'coordinates': [51, 0]}}
            ]}],
        }
        mapit_session.get.return_value.json.return_value = {"65961": {
            "id": 65961,
            "codes": {"gss": "E14001023", "unit_id": "25133"},
            "name": "Wealden",
            "country": "E",
            "type": "WMC"
        }}
        area_to_rep.return_value = {
            "name": "Nusrat Ghani",
            "twitter": "https://twitter.com/nus_ghani",
            "facebook": None,
            "party": "Conservative",
            "constituency": "Wealden",
            "email": 'nusrat.ghani.mp@parliament.uk',
        }
        resp = self.app.get('/address/UK/Cannon+Street+Manchester')
        self.assertEquals(resp.headers['Access-Control-Allow-Origin'], '*')
        self.assertEquals(resp.json, {"representative": area_to_rep.return_value})

    @patch('services.country.session')
    @patch('services.mapit.session')
    def test_bad_point_result(self, mapit_session, country_session):
        country_session.get.return_value.json.return_value = {
            'statusCode': 200,
            'resourceSets': [{'resources': [
                {'name': 'Cannon Street, Manchester',
                 'address': {'countryRegion': 'United Kingdom'},
                 'point': {'coordinates': [52, 0]}}  # Different co-ords to above, due to cache
            ]}],
        }
        mapit_session.get.return_value.json.return_value = {}
        self.app.get('/address/UK/Cannon+Street+Manchester', status=400)

    @patch('countries.AU.area_to_rep')
    @patch('services.mapit.session')
    @patch('services.country.session')
    def test_au_address(self, session, mapit_session, area_to_rep):
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
        mapit_session.get.return_value.json.return_value = {1: {
            'name': 'Constituency name', 'codes': {'ocd': 'an-ocd-id'},
        }}
        area_to_rep.return_value = {
            "name": "Hon Dr Andrew Leigh MP",
            "twitter": "https://twitter.com/ALEIGHMP",
            "facebook": "http://www.facebook.com/pages/Andrew-Leigh-MP/129819533748295",
            "party": "Australian Labor Party",
            "constituency": "Fraser, Australian Capital Territory",
            "email": "andrew.leigh.mp@aph.gov.au"
        }
        resp = self.app.get('/address/AU/Cannon+Street+Manchester')
        self.assertEqual(resp.json, {"representative": area_to_rep.return_value})

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
        self.assertEqual(resp.json, {"results": [
            {"latitude": -35.279651, "longitude": 149.138427, "address": "Cannon Street, Manchester"},
            {"latitude": -35.279651, "longitude": 149.138427, "address": "Cannon Street, Adelaide"}
        ]})

    @patch('services.country.session')
    def test_bad_address(self, session):
        session.get.return_value.json.return_value = {'statusCode': 401}
        self.app.get('/address/AU/Cannon+Street+Manchester', status=404)


class TestCountry(unittest.TestCase):
    def test_no_popolo_data(self):
        class Fake(countries.UK):
            ep_country = 'Non-existant'
        Fake()


class TestLookup(unittest.TestCase):
    def setUp(self):
        self.au = countries.AU()

    def test_bad_area(self):
        with self.assertRaises(falcon.HTTPInternalServerError):
            Lookup().area_to_rep(self.au, None)

    def test_no_memberships(self):
        self.au.popolo.memberships = {}
        with self.assertRaises(falcon.HTTPNotFound):
            Lookup().area_to_rep(self.au, {'id': OCD_ID % 'mackellar'})

    def test_multiple_memberships(self):
        area_id = OCD_ID % 'mackellar'
        term_id = self.au.popolo.current_period['id']
        self.au.popolo.persons['person/10046'] = Person({
            'name': 'Bronwyn Bishop'
        })

        self.au.popolo.memberships[term_id][area_id] = [
            {"on_behalf_of_id": "party/liberal_party",
             "person_id": "person/10043",
             "start_date": "2015-08-02",
             "end_date": "2015-09-01",
             },
            {"on_behalf_of_id": "party/liberal_party",
             "person_id": "person/10046",
             "start_date": "2015-09-02",
             },
        ]
        data = Lookup().area_to_rep(self.au, {'id': area_id})
        self.assertEqual(data['representative']['name'], 'Bronwyn Bishop')

    def test_out_of_date_eemberships(self):
        area_id = OCD_ID % 'mackellar'
        term_id = self.au.popolo.current_period['id']
        self.au.popolo.memberships[term_id][area_id] = [
            {"on_behalf_of_id": "party/liberal_party",
             "person_id": "person/10043",
             "start_date": "2015-08-02",
             "end_date": "2015-09-01",
             },
        ]
        with self.assertRaises(falcon.HTTPNotFound):
            Lookup().area_to_rep(self.au, {'id': area_id})


class TestConfig(unittest.TestCase):
    def test_non_dict_config(self):
        io = StringIO.StringIO("Test")
        with self.assertRaises(Exception):
            settings.load_config(io)

    def test_bad_yaml(self):
        io = StringIO.StringIO("Foo: Foo\nFoo")
        with self.assertRaises(Exception):
            settings.load_config(io)


class TestFlake8(unittest.TestCase):
    def test_flake8(self):
        app = flake8.main.application.Application()
        app.run()


if __name__ == '__main__':
    unittest.main()
