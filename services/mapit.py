from requests_cache import CachedSession

session = CachedSession(cache_name='cache', expire_after=86400)


class BaseException(Exception):
    pass


class NotFoundException(BaseException):
    pass


class BadRequestException(BaseException):
    pass


class MapIt(object):
    postcode_url = '%s/postcode/%s'
    point_url = '%s/point/4326/%s,%s'
    areas_url = '%s/areas/%s'
    cache = {}

    def __init__(self, config):
        self.base = config.mapit_base
        self.type = config.mapit_type
        self.name_hook = getattr(config, 'name_hook', None)

    def typed_areas(self, areas):
        return [a for a in areas if a['type'] == self.type]

    def postcode_point_to_area(self, pc):
        url = self.postcode_url % (self.base, pc)
        data = self.get(url)
        return self.typed_areas(data['areas'].values())

    def postcode_area_to_area(self, pc):
        url = self.areas_url % (self.base, pc)
        data = self.get(url)
        id = data.keys().pop()
        matches = []
        for query in ('coverlaps', 'covered'):
            url = '%s/area/%s/%s?type=%s' % (self.base, id, query, self.type)
            data = self.get(url).values()
            matches.extend(self.typed_areas(data))
        if self.name_hook:
            self.name_hook(self, matches)
        return matches

    def point_to_area(self, point):
        url = self.point_url % (self.base, point['longitude'], point['latitude'])
        data = self.get(url).values()
        matches = self.typed_areas(data)
        if self.name_hook:
            self.name_hook(self, matches)
        if len(matches) != 1:
            raise BadRequestException("Should only be one result")
        return matches[0]

    def get(self, url):
        if url not in self.cache:
            resp = session.get(url)
            data = resp.json()
            if resp.status_code == 404:
                raise NotFoundException(data['error'])
            if resp.status_code == 400:
                raise BadRequestException(data['error'])
            self.cache[url] = data
        return self.cache[url]
