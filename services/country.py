import os

from .popolo import Popolo
from .mapit import MapIt


DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))


class BaseException(Exception):
    pass


class NotFoundException(BaseException):
    pass


class Country(object):
    def __init__(self):
        self.mapit = MapIt(self)
        self.popolo = Popolo.load(open(os.path.join(DATA_DIR, self.ep_country + '.json')))

    def _area(self, area):
        return {
            'id': area['codes'].get('everypolitician'),
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

    def area_to_rep(self, area):
        if area['id']:
            area = self.popolo.area_by_id(area['id'])
        else:
            area = self.popolo.area_by_name(area['name'])
        try:
            mship = self.popolo.membership(area=area, period=self.popolo.current_period)
        except KeyError:
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
