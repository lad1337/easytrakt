import logging

import pytest

import easytrakt
from easytrakt import Client

easytrakt.logger.addHandler(logging.StreamHandler())
easytrakt.logger.setLevel(logging.DEBUG)


@pytest.yield_fixture
def client():
    yield Client()
