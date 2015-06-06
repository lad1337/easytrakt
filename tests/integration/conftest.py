import logging
import os

import pytest
from requests_oauthlib import OAuth2Session

import easytrakt
from easytrakt import Client

easytrakt.logger.addHandler(logging.StreamHandler())
easytrakt.logger.setLevel(logging.DEBUG)

CLIENT_ID = "8224c88cc14f27ab6e0d894dec500f7c46bd5de71fdc1b27cac6be8c027f023b"


@pytest.yield_fixture
def client():
    token = {
        "access_token": os.environ["TRAKT_TOKEN"],
        "created_at": 1433447370,
        "expires_in": 7776000,
        "expires_at": 1441223370.73398,
        "token_type": "bearer",
        "scope": ["public"],
        "refresh_token": ""
    }
    session = OAuth2Session(
        CLIENT_ID,
        token=token
    )
    yield Client(session)
