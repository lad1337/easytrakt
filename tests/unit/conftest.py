import logging

import pytest

import easytrakt
from easytrakt import Client

easytrakt.logger.addHandler(logging.StreamHandler())
easytrakt.logger.setLevel(logging.DEBUG)


@pytest.yield_fixture
def client():
    yield Client()


@pytest.yield_fixture
def user_data():
    yield {
        "user": {
            "username": "lad1337",
            "private": False,
            "name": "Dennis Lutter",
            "vip": True,
            "vip_ep": False,
            "joined_at": "2010-09-25T17:49:25.000Z",
            "location": "San Diego, CA",
            "about": "Co-founder of trakt.",
            "gender": "male",
            "age": 32,
            "images": {
                "avatar": {
                    "full": "https://secure.gravatar.com/avatar/30c2f0dfbc39e48656f40498aa871e33?r=pg&s=256"  # noqa
                }
            }
        },
        "account": {
            "timezone": "America/Los_Angeles",
            "time_24hr": False,
            "cover_image": "https://walter.trakt.us/images/movies/000/001/545/fanarts/original/0abb604492.jpg?1406095042"  # noqa
        },
        "connections": {
            "facebook": True,
            "twitter": True,
            "google": True,
            "tumblr": False
        },
        "sharing_text": {
            "watching": "I'm watching [item]",
            "watched": "I just watched [item]"
        }
    }
