import datetime
import json


class Data(object):
    def __init__(self, data):
        self.__dict__ = data


def define_fn(collection, key_name, value_name):
    def thing(self, key):
        for link in getattr(self, collection, []):
            if link[key_name] == key:
                return link[value_name]
        return None
    return thing

Data.link = define_fn('links', 'note', 'url')
Data.contact_detail = define_fn('contact_details', 'type', 'value')


class Person(Data):
    @property
    def email(self):
        return self.__dict__.get('email')


class Area(Data):
    pass


class Org(Data):
    pass


class Popolo(Data):
    @classmethod
    def load(cls, fp):
        data = json.load(fp)
        return cls(data)

    def __init__(self, data):
        super(Popolo, self).__init__(data)
        self.persons = {p['id']: Person(p) for p in self.persons}
        self.organizations = {o['id']: Org(o) for o in self.organizations}
        self.areas_by_id = {a['id']: Area(a) for a in self.areas}
        self.areas_by_name = {a['name']: Area(a) for a in self.areas}
        mships = {}
        for m in self.memberships:
            mships.setdefault(m['legislative_period_id'], {}).setdefault(m['area_id'], []).append(m)
        self.memberships = mships
        for e in self.events:
            if 'end_date' not in e or e['end_date'] >= datetime.date.today().isoformat():
                self.current_period = e

    # NOTE: Returns only one membership for period/area
    def membership(self, area=None, period=None):
        return self.memberships[period['id']][area.id][0]

    def person(self, id=None):
        return self.persons[id]

    def org(self, id=None):
        return self.organizations[id]

    def area_by_id(self, id):
        return self.areas_by_id[id]

    def area_by_name(self, name):
        return self.areas_by_name[name]
