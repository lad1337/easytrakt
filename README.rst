EasyTrakt
=========

|alt travis build| |alt codecov| |alt pypi version| |alt requires| |alt pypi
downloads|

install
-------

.. code:: python

    pip install easytrakt

use
---

.. code:: python

    from easytrakt import Client
    client = Client()
    search_results = client.search("The Big Lebowski")
    movie = search_results[0]
    assert movie.title == "The Big Lebowski"

with OAuth you need a session with a token this libary does not take
care of OAuth authentcation but can use a ``OAuth2Session`` from
``requests_oauthlib``

.. code:: python

    # you get this stuff from the oauth process
    token = {
        "access_token": "",
        "created_at": 1433447370,
        "expires_in": 7776000,
        "expires_at": 1441223370.73398,
        "token_type": "bearer",
        "scope": ["public"],
        "refresh_token": ""
    }
    from requests_oauthlib import OAuth2Session
    session = OAuth2Session(your_app_client_id, token=token)

    from easytrakt import Client
    client = Client(session)
    search_results = client.shows("Dexter")
    show = search_results[0]
    assert show.title == "Dexter"
    # all ids are behind 'ids'
    assert show.ids.trakt == 1396
    # the trakt id has a short version
    assert show.ids.trakt == show.trakt
    # for a show/movie it's also the .id
    assert show.trakt == show.id

    # or if you have the trakt id
    from easytrakt.models import Show
    # still need a client ...
    dexter = Show(client, 1396)
    for season in dexter.seasons:
        print season.number
        print season.images.poster.medium
        for episode in season.episodes:
            print episode.number
            print epidode.title
            print episode.first_air_date
            print episode.images.screenshot.full

every attribute is build dynamically, to get all keys on the current
level call ``.keys()`` of any model class

.. |alt travis build| image:: https://img.shields.io/travis/lad1337/easytrakt.svg
.. |alt codecov| image:: https://img.shields.io/codecov/c/github/lad1337/easytrakt.svg
.. |alt pypi version| image:: https://img.shields.io/pypi/v/easytrakt.svg
.. |alt requires| image:: https://img.shields.io/requires/github/lad1337/easytrakt.svg
.. |alt pypi downloads| image:: https://img.shields.io/pypi/dm/easytrakt.svg
