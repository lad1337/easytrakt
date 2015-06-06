from collections import defaultdict
from json import loads

from attrdict import AttrDict
from dateutil.parser import parse as date_parser


BASE_NESTED = {"ids": lambda c, d, p: AttrDict(d)}


def model_from_search_item(client, item):
    type_ = item["type"]

    return TYPE_MAP[type_](client, item[type_])


def images_generator(client, images, parent):
    out = AttrDict()
    for type_, sizes in images.items():
        for size, url in sizes.items():
            if type_ not in out:
                out[type_] = AttrDict()
            out[type_][size] = url
    return out


class BaseModel(object):
    id_key = None
    extendables = defaultdict(list)
    nested = {}
    uri_section = ""
    heretical_identifier_structure = '{"ids": {"trakt": %s}}'

    def __init__(self, client, data, parent=None):
        self.client = client
        if isinstance(data, int):
            data = loads(self.heretical_identifier_structure % data)
        self._data = data
        self.nested.update(**BASE_NESTED)
        self.parent = parent

    def handle_nested(self, name, generator):
        if name != "ids":
            self.client.logger.debug(
                "%s building nested property '%s' with %s",
                self, name, self._data[name])
        return generator(self.client, self._data[name], self)

    def __getattr__(self, name):
        if name in self._data:
            if name in self.nested:
                return self.handle_nested(name, self.nested[name])
            return self._data[name]

        for extend_key, attributes in self.extendables.items():
            if name in attributes:
                self.client.logger.debug(
                    "%s is extending '%s' using '%s'",
                    self, name, extend_key)
                self.extend(name, **self.build_extend_kwargs(extend_key))
                if name in self._data:
                    break
        else:
            raise AttributeError(
                "{} has no (extendable) attribute: {}".format(self, name))
        return getattr(self, name)

    def build_extend_kwargs(self, extend_key):
        if extend_key.startswith("/"):
            return {"path": self.uri_path + extend_key}
        elif extend_key.startswith("-"):
            path_extension = None
            for extendable in self.parent.extendables:
                if extendable.startswith("/") and\
                        extendable[1:].startswith(self.type):
                    path_extension = extendable
            if path_extension is None:
                raise ValueError("no parent extension found for '%s'", self.type)
            return {
                "path": self.parent.uri_path + path_extension,
                "extend_flag": extend_key[1:]}

        return {"extend_flag": extend_key}

    def extend(self, name, extend_flag=None, path=None):
        uri = self.uri_path
        if path:
            uri = path

        if extend_flag == self.type:
            data = self.client.request(uri)
        elif extend_flag:
            data = self.client.request(uri, {"extended": extend_flag})
        else:
            data = self.client.request(uri)
        if isinstance(data, list):
            self._data[name] = data
            for entry in data:
                base = BaseModel(self.client, entry)
                if base.trakt == self.trakt:
                    self.client.logger.debug(
                        "%s is applying '%s' with entry %s", self, name, base)
                    self._data.update(**entry)
                    break
        else:
            self.client.logger.debug(
                "%s is updating its data, because of '%s' with %s",
                self, name, data)
            self._data.update(**data)
        return data

    def keys(self):
        keys = []
        for attributes in self.extendables.values():
            keys.extend(attributes)
        return sorted(keys)

    @property
    def type(self):
        return self.__class__.__name__.lower()

    @property
    def uri_path(self):
        if self.parent is None:
            return self.uri_section.format(self=self)
        return self.parent.uri_path + self.uri_section.format(self=self)

    @property
    def id(self):
        return getattr(self, self.id_key)

    @property
    def trakt(self):
        return self.ids.trakt

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    __str__ = __repr__


class Movie(BaseModel):
    id_key = "trakt"
    extendables = {
        "movie": ["title", "ids", "year"],
        "images": ["images"],
        "full": ["overview", "released", "tagline", "trailer", "rating",
                 "votes", "language", "available_translations", "genres",
                 "certification"],
        "/seasons": ["seasons"]}
    nested = {
        "released": lambda c, d, p: date_parser(d),
        "images": images_generator
    }
    uri_section = "/movies/{self.id}"


class Episode(BaseModel):
    id_key = "number"
    extendables = {
        "images": ["images"],
        "full": [
            "number_abs", "overview", "first_aired", "updated_at", "rating",
            "updated_at", "rating", "votes", "available_translations"],
        "episodes": ["episodes"]}
    nested = {
        "first_aired": lambda c, d, p: date_parser(d),
        "images": images_generator
    }
    uri_section = "/episodes/{self.number}"


class Season(BaseModel):
    id_key = "number"
    extendables = {
        "season": ["ids"],
        "-images": ["images"],
        "-full": [
            "rating", "votes", "episode_count", "aired_episodes", "overview"],
        "episodes": ["episodes"]}
    nested = {
        "episodes": lambda c, ee, p: [Episode(c, s, p) for s in ee],
        "images": images_generator
    }
    uri_section = "/seasons/{self.number}"


class Show(BaseModel):
    id_key = "trakt"
    extendables = {
        "show": ["title", "ids"],
        "images": ["images"],
        "full": ["overview", "airs"],
        "/seasons": ["seasons"]}
    nested = {
        "seasons": lambda c, ss, p: [Season(c, s, p) for s in ss],
        "airs": lambda c, d, p: AttrDict(d),
        "images": images_generator
    }
    uri_section = "shows/{self.ids.trakt}"


class Person(BaseModel):
    pass


class List(BaseModel):
    pass


TYPE_MAP = {
    "movie": Movie,
    "show": Show,
    "person": Person,
    "episode": Episode,
    "list": List
}
