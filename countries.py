import inspect

from services import country
from settings import config


class Country(country.Country):
    bing_key = config['BING_MAPS_API_KEY']


class UK(Country):
    ep_country = 'UK'
    ep_house = 'Commons'
    mapit_base = 'http://mapit.mysociety.org'
    mapit_type = 'WMC'
    postcode_areas = False
    geocoding_bounding_box = '49,-9,61,2'
    geocoding_country = 'United Kingdom'


class AU(Country):
    ep_country = 'Australia'
    ep_house = 'Representatives'
    mapit_base = 'http://oxfam.mapit.mysociety.org'
    mapit_type = 'CED'
    postcode_areas = True
    geocoding_bounding_box = '-44,113,-10,154'
    geocoding_country = 'Australia'


COUNTRIES = dict((k, v()) for k, v in globals().items() if inspect.isclass(v) and hasattr(v, 'ep_country'))


def get(country=None):
    return COUNTRIES[country] if country else COUNTRIES
