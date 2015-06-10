__author__ = 'dennis.lutter'

import models

from attrdict import AttrDict
from dateutil.parser import parse as date_parser


def attrdict(client, data, parent):
    return AttrDict(data)


def images(client, images, parent, expected=()):
    if expected and not all(type_ in images for type_ in expected):
        raise GeneratorExit(
            "not all expected image types found %s", expected)
    out = AttrDict()
    for type_, sizes in images.items():
        for size, url in sizes.items():
            if type_ not in out:
                out[type_] = AttrDict()
            out[type_][size] = url
    return out


def date(client, data, parent):
    if data:
        return date_parser(data)


def watchlist_items(client, items, parent):
    client.logger.debug("watchlist_items: %s", items)
    watchlist_items = []
    for item in items:
        model = models.model_from_item(client, item)
        model._data["listed_at"] = item["listed_at"]
        model.nested["listed_at"] = date
        client.logger.debug("watchlist_items model: %s", model)

        watchlist_items.append(model)
    return watchlist_items
