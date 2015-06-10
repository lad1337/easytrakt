from datetime import datetime

from dateutil.parser import parse as date_parser


from easytrakt.models import Episode
from easytrakt.models import Movie
from easytrakt.models import MovieWatchlist
from easytrakt.models import Season
from easytrakt.models import Settings
from easytrakt.models import Show
from easytrakt.models import ShowWatchlist


def test_search_show(client):
    result = client.search("Dexter")
    assert result
    show = result[0]
    assert isinstance(show, Show)
    assert show.title == "Dexter"
    assert show.ids.trakt == 1396
    assert show.id == 1396
    assert show.images.poster.full.startswith("http")
    assert show.images.banner.full.startswith("http")


def test_search_movie(client):
    result = client.movies("The Big Lebowski")
    assert result
    movie = result[0]
    assert isinstance(movie, Movie)
    assert movie.title == "The Big Lebowski"
    assert movie.year == 1998
    assert movie.id == 84
    assert isinstance(movie.released, datetime)
    assert movie.released == date_parser("1998-03-06")
    assert movie.images.poster.full.startswith("http")
    assert movie.images.fanart.full.startswith("http")


def test_season(client):
    show = Show(client, 1396)
    seasons = show.seasons
    assert seasons
    season = seasons[1]
    assert isinstance(season, Season)
    assert season.number == 1
    assert season.trakt == 3999
    assert season.aired_episodes == 12
    assert season.images.poster.full.startswith("http")


def test_episodes(client):
    show = Show(client, 1396)
    episodes = show.seasons[1].episodes
    episode = episodes[1]
    assert isinstance(episode, Episode)
    assert episode.season == 1
    assert episode.number == 2
    assert episode.trakt == 74162
    assert episode.title == "Crocodile"
    assert isinstance(episode.first_aired, datetime)
    assert episode.first_aired == date_parser("2006-10-08T04:00:00.000Z")
    assert episode.images.screenshot.full.startswith("http")


def test_settings(client):
    settings = Settings(client)
    assert settings.user.username == "lad1337"


def test_movie_watchlist(client):
    watchlist = MovieWatchlist(client)
    assert watchlist.items
    assert isinstance(watchlist.items[0], Movie)


def test_show_watchlist(client):
    watchlist = ShowWatchlist(client)
    assert watchlist.items
    assert isinstance(watchlist.items[0], Show)
