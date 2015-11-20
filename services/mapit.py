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
    point_url = '%s/point/4326/%s,%s?type=%s'
    areas_url = '%s/areas/%s'
    cache = {}

    def __init__(self, config):
        self.base = config.mapit_base
        self.type = config.mapit_type

    def typed_areas(self, areas):
        return [a for a in areas if a['type'] == self.type]

    def postcode_point_to_area(self, pc):
        url = self.postcode_url % (self.base, pc)
        data = self.get(url)
        return self.typed_areas(data['areas'].values())

    def postcode_area_to_area(self, pc):
        url = self.areas_url % (self.base, pc)
        data = self.get(url)
        if not data:
            raise NotFoundException('No Postcode matches the given query.')
        id = data.keys().pop()
        url = '%s/area/%s/covered?type=%s' % (self.base, id, self.type)
        data = self.get(url).values()
        if data:
            return data
        url = '%s/area/%s/coverlaps?type=%s' % (self.base, id, self.type)
        data = self.get(url).values()
        return data

    def point_to_area(self, point):
        url = self.point_url % (self.base, point['longitude'], point['latitude'], self.type)
        matches = self.get(url).values()
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
