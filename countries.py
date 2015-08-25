import inspect

from services import country


class UK(country.Country):
    ep_country = 'UK'
    ep_house = 'Commons'
    mapit_base = 'http://mapit.mysociety.org'
    mapit_type = 'WMC'
    postcode_areas = False


class AU(country.Country):
    ep_country = 'Australia'
    ep_house = 'Representatives'
    mapit_base = 'http://oxfam.mapit.mysociety.org'
    mapit_type = 'CED'
    postcode_areas = True

    mapit_state_type = 'STT'
    state_lookup = {
        'ACT': 'Australian Capital Territory',
        'NSW': 'New South Wales',
        'NT': 'Northern Territory',
        'OT': 'Ocean Territories',
        'QLD': 'Queensland',
        'SA': 'South Australia',
        'TAS': 'Tasmania',
        'VIC': 'Victoria',
        'WA': 'Western Australia',
    }

    # Add state name to end of name
    def name_hook(self, mapit, matches):
        for m in matches:
            if m['name'] == 'Fraser' and 'Australian Capital Territory' not in m['name']:
                m['name'] += ', Australian Capital Territory'
                continue
            url = '%s/area/%s/covered?type=%s' % (self.mapit_base, m['id'], self.mapit_state_type)
            data = mapit.get(url).values()
            if len(data) == 1 and self.state_lookup[data[0]['name']] not in m['name']:
                m['name'] = '%s, %s' % (m['name'], self.state_lookup[data[0]['name']])


COUNTRIES = dict((k, v()) for k, v in globals().items() if inspect.isclass(v) and hasattr(v, 'ep_country'))


def get(country=None):
    return COUNTRIES[country] if country else COUNTRIES
