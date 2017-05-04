import os

import falcon
from requests_cache import CachedSession

from .popolo import Popolo
from .mapit import MapIt

session = CachedSession(cache_name='bing', expire_after=86400)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))


class BaseException(Exception):
    pass


class NotFoundException(BaseException):
    pass


class Country(object):
    bing_url = "http://dev.virtualearth.net/REST/v1/Locations"

    def __init__(self):
        self.mapit = MapIt(self)
        try:
            self.popolo = Popolo.load(open(os.path.join(DATA_DIR, self.ep_country + '.json')))
        except IOError:
            # Assume it's because it doesn't exist yet
            pass

    def geocode(self, addr):
        url = self.bing_url
        params = {
            'query': addr,
            'key': self.bing_key,
            'userMapView': self.geocoding_bounding_box,
        }
        url += falcon.to_query_str(params)

        data = session.get(url).json()
        if data['statusCode'] != 200:
            return []

        points = []
        for result in data['resourceSets'][0]['resources']:
            if result['address']['countryRegion'] != self.geocoding_country:
                continue
            lat, lon = result['point']['coordinates']
            points.append({
                'address': result['name'],
                'latitude': lat,
                'longitude': lon,
            })

        return points

    def _area(self, area):
        return {
            'id': area['codes'].get('ocd'),
            'name': area['name']
        }

    def postcode_to_area(self, pc):
        if self.postcode_areas:
            pc = 'pc%s' % pc
            matches = self.mapit.postcode_area_to_area(pc)
        else:
            matches = self.mapit.postcode_point_to_area(pc)
        matches = [self._area(m) for m in matches]
        return matches

    def point_to_area(self, point):
        area = self.mapit.point_to_area(point)
        return self._area(area)

    def area_to_rep(self, area):
        try:
            if area['id']:
                area = self.popolo.area_by_id(area['id'])
            else:
                area = self.popolo.area_by_name(area['name'])
        except KeyError:
            area = None
        if area is None:
            # No memberships, so areas stripped by fetch-data
            raise NotFoundException("No membership found")

        try:
            mship = self.popolo.current_membership(area=area, period=self.popolo.current_period)
        except (KeyError, IndexError):
            mship = None
        if mship is None:
            raise NotFoundException("No membership found")

        person = self.popolo.person(id=mship['person_id'])
        party = self.popolo.org(id=mship['on_behalf_of_id'])
        return {
            'name': person.name,
            'party': party.name,
            'constituency': area.name,
            'email': person.email,
            'facebook': person.link('facebook'),
            'twitter': person.contact_detail('twitter'),
        }
