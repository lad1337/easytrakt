from dateutil.parser import parse as date_parser
from mock import Mock
import pytest

from easytrakt.models import Episode
from easytrakt.models import Movie
from easytrakt.models import MovieWatchlist
from easytrakt.models import Season
from easytrakt.models import Settings
from easytrakt.models import Show


def test_search(client):
    client.request = Mock(return_value=[
        {"type": "show", "show": {"title": "foo"}}
    ])

    result = client.search("foo")
    assert result
    assert isinstance(result[0], Show)
    assert result[0].title == "foo"


def test_search_helpers(client):
    client.request = Mock(return_value=[
        {"type": "show", "show": {"title": "foo"}}
    ])

    result = client.shows("foo")
    client.request.assert_called_once_with(
        "search", {"query": "foo", "year": None, "type": "show"})
    assert result
    assert isinstance(result[0], Show)
    assert result[0].title == "foo"


def test_extend(client):
    client.request = Mock(return_value=[
        {"type": "show", "show": {"title": "foo", "ids": {"trakt": 1}}}
    ])

    show = client.search("foo")[0]
    assert show.title == "foo"
    assert show.ids.trakt == 1
    assert show.id == 1

    client.request = Mock(return_value={"overview": "this is the overview"})
    assert show.overview == "this is the overview"


def test_extend_fail(client):
    client.request = Mock(return_value=[
        {"type": "show", "show": {"title": "foo", "ids": {"trakt": 1}}}
    ])
    show = client.search("foo")[0]
    with pytest.raises(AttributeError):
        assert show.foo


def test_extend_seasons(client):
    client.request = Mock(return_value=[
        {"type": "show", "show": {"title": "foo", "ids": {"trakt": 1}}}
    ])

    show = client.search("foo")[0]
    assert show.title == "foo"
    client.request = Mock(return_value=[{"number": 0, "ids": {"trakt": 3}}])
    assert len(show.seasons) == 1
    assert isinstance(show.seasons[0], Season)
    assert show.seasons[0].number == 0
    season = show.seasons[0]
    client.request = Mock(return_value=[{"number": 1, "ids": {"trakt": 5}}])
    assert season.episodes
    assert isinstance(season.episodes[0], Episode)
    assert season.episodes[0].number == 1


def test_init_with_trakt_id(client):
    client.request = Mock(return_value={
        "title": "foo", "ids": {"trakt": 1}
    })
    show = Show(client, 1)
    assert show
    assert show.title == "foo"


def test_keys(client):
    assert Show(client, 1).keys() == [
        "aired_episodes", "airs", "available_translations", "certification",
        "country", "first_aired", "genres", "homepage", "ids", "images",
        "language", "network", "overview", "rating", "runtime", "seasons",
        "status", "title", "trailer", "updated_at", "votes", "year"]


def test_date_parser(client):
    client.request = Mock(return_value=[
        {"type": "show",
         "show": {
             "title": "foo",
             "ids": {"trakt": 1},
             "first_aired": None,
             "updated_at": "2006-10-08T04:00:00.000Z"
         }}
    ])
    show = client.search("foo")[0]
    assert show.first_aired is None
    assert show.updated_at == date_parser("2006-10-08T04:00:00.000Z")


def test_initial_missing_image_type(client):
    client.request = Mock(return_value=[
        {"type": "show",
         "show": {
             "title": "foo",
             "ids": {"trakt": 1},
             "first_aired": None,
             "images": {
                 "poster": {"full": "poster_image_url"}
             }
         }}
    ])
    show = client.search("foo")[0]
    client.request = Mock(return_value={
        "images": {
            "poster": {"full": "poster_image_url"},
            "banner": {"full": "banner_image_url"},
            "logo": {"full": "logo_image_url"},
            "clearart": {"full": "clearart_image_url"},
            "fanart": {"full": "fanart_image_url"},
            "thumb": {"full": "thumb_image_url"}
        },
        "ids": {"trakt": 1},
    })
    assert show.images.poster.full == "poster_image_url"
    assert show.images.banner.full == "banner_image_url"
    assert show.images.logo.full == "logo_image_url"
    assert show.images.clearart.full == "clearart_image_url"
    assert show.images.fanart.full == "fanart_image_url"
    assert show.images.thumb.full == "thumb_image_url"


def test_settings(client, user_data):
    client.request = Mock(return_value=user_data)
    settings = Settings(client)
    assert settings.user.username == "lad1337"


def test_get_watchlist(client):
    watchlist_data = [
        {
            "listed_at": "2014-09-01T09:10:11.000Z",
            "type": "movie",
            "movie": {
                "title": "TRON: Legacy",
                "year": 2010,
                "ids": {
                    "trakt": 1,
                    "slug": "tron-legacy-2010",
                    "imdb": "tt1104001",
                    "tmdb": 20526
                }
            }
        },
        {
            "listed_at": "2014-09-01T09:10:11.000Z",
            "type": "movie",
            "movie": {
                "title": "The Dark Knight",
                "year": 2008,
                "ids": {
                    "trakt": 6,
                    "slug": "the-dark-knight-2008",
                    "imdb": "tt0468569",
                    "tmdb": 155
                }
            }
        }
    ]
    client.request = Mock(return_value=watchlist_data)
    watchlist = MovieWatchlist(client)
    assert watchlist.items
    assert isinstance(watchlist.items[0], Movie)
    assert watchlist.items[0].listed_at ==\
        date_parser("2014-09-01T09:10:11.000Z")
