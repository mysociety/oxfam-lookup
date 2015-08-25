import falcon
import json

import countries
import services


class Lookup(object):
    def get_country(self, country):
        try:
            return countries.get(country)
        except KeyError:
            raise falcon.HTTPInvalidParam("", "country")

    def to_area(self, country, postcode):
        try:
            return country.postcode_to_area(postcode)
        except services.mapit.NotFoundException as e:
            raise falcon.HTTPNotFound(title='Not Found', description=e.args[0])
        except services.mapit.BadRequestException as e:
            raise falcon.HTTPBadRequest('Bad request', e.args[0])

    def area_to_rep(self, country, area):
        try:
            rep = country.area_to_rep(area)
        except services.country.NotFoundException as e:
            raise falcon.HTTPNotFound(title='Not Found', description=e.args[0])
        except Exception as e:
            msg = '%s: %s' % (e.__class__.__name__, e.args[0])
            raise falcon.HTTPInternalServerError('Internal Server Error', msg)
        return {'representative': rep}


class Postcode(Lookup):
    def on_get(self, req, resp, country, postcode):
        country = self.get_country(country)
        areas = self.to_area(country, postcode)
        if len(areas) != 1:
            req.context['result'] = {'areas': areas}
            return
        req.context['result'] = self.area_to_rep(country, areas[0])


class JSONOutput(object):
    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return
        resp.body = json.dumps(req.context['result'])


application = falcon.API(middleware=[JSONOutput()])
application.add_route('/postcode/{country}/{postcode}', Postcode())
