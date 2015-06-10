__author__ = 'dennis.lutter'

from functools import partial
import logging

from cachecontrol import CacheControl
import requests

from models import model_from_item
from models import TYPE_MAP

BASE_URL = "https://api-v2launch.trakt.tv"
logger = logging.getLogger("easytrakt")


class Client(object):

    def __init__(self, session=None, verify_ssl=True, url=BASE_URL):
        session = session or requests.session()
        session.headers = {
            "Content-type": "application/json",
            "trakt-api-key": getattr(session, "client_id", ""),
            "trakt-api-version": 2
        }
        self.session = CacheControl(session)

        self.logger = logger
        self.verify_ssl = verify_ssl
        self.base_url = url

        for type_ in TYPE_MAP:
            setattr(self, type_ + "s", partial(self.search, type=type_))

    def search(self, query, type=None, year=None):
        params = {
            "query": query,
            "type": type,
            "year": year
        }
        return [model_from_item(self, item)
                for item in self.request("search", params)]

    def request(self, uri_path, params=None):
        uri = "{}/{}".format(self.base_url, uri_path)
        self.logger.info("call to: %s with %s", uri, params)
        result = self.session.get(
            uri,
            params=params,
            verify=self.verify_ssl
        )
        result.raise_for_status()
        return result.json()
