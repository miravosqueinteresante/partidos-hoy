import pytest
from src.data.data_cascade import DataCascade


def test_cascade_tries_api_football_first(mocker):
    mocker.patch("src.data.data_cascade.APIFootballClient")
    mocker.patch("src.data.data_cascade.FBrefScraper")
    mocker.patch("src.data.data_cascade.FootballDataOrgClient")

    cascade = DataCascade()
    cascade.api_football.fetch_worldcup_fixtures.return_value = [
        {"home_team": "Argentina", "source": "api-football"}
    ]

    result = cascade.get_worldcup_fixtures()
    assert len(result) == 1
    assert result[0]["source"] == "api-football"
    cascade.fbref.fetch_worldcup_fixtures.assert_not_called()


def test_cascade_falls_back_to_fbref(mocker):
    mocker.patch("src.data.data_cascade.APIFootballClient")
    mocker.patch("src.data.data_cascade.FBrefScraper")
    mocker.patch("src.data.data_cascade.FootballDataOrgClient")

    cascade = DataCascade()
    cascade.api_football.fetch_worldcup_fixtures.return_value = []
    cascade.fbref.fetch_worldcup_fixtures.return_value = [
        {"home_team": "Argentina", "source": "fbref"}
    ]

    result = cascade.get_worldcup_fixtures()
    assert result[0]["source"] == "fbref"
    cascade.fbref.fetch_worldcup_fixtures.assert_called_once()


def test_cascade_falls_back_to_football_data_org(mocker):
    mocker.patch("src.data.data_cascade.APIFootballClient")
    mocker.patch("src.data.data_cascade.FBrefScraper")
    mocker.patch("src.data.data_cascade.FootballDataOrgClient")

    cascade = DataCascade()
    cascade.api_football.fetch_worldcup_fixtures.return_value = []
    cascade.fbref.fetch_worldcup_fixtures.return_value = []
    cascade.football_data.fetch_matches.return_value = [
        {"home_team": "Argentina", "source": "football-data.org"}
    ]

    result = cascade.get_worldcup_fixtures()
    assert result[0]["source"] == "football-data.org"


def test_cascade_returns_empty_when_all_fail(mocker):
    mocker.patch("src.data.data_cascade.APIFootballClient")
    mocker.patch("src.data.data_cascade.FBrefScraper")
    mocker.patch("src.data.data_cascade.FootballDataOrgClient")

    cascade = DataCascade()
    cascade.api_football.fetch_worldcup_fixtures.side_effect = Exception("fail")
    cascade.fbref.fetch_worldcup_fixtures.return_value = []
    cascade.football_data.fetch_matches.return_value = []

    result = cascade.get_worldcup_fixtures()
    assert result == []


def test_cascade_unifies_data_format(mocker):
    mocker.patch("src.data.data_cascade.APIFootballClient")
    mocker.patch("src.data.data_cascade.FBrefScraper")
    mocker.patch("src.data.data_cascade.FootballDataOrgClient")

    cascade = DataCascade()
    cascade.api_football.fetch_worldcup_fixtures.return_value = [
        {
            "fixture": {"id": 1, "date": "2026-06-11T21:00:00+00:00"},
            "teams": {"home": {"name": "Mexico"}, "away": {"name": "Canada"}},
            "league": {"id": 1},
        }
    ]

    result = cascade.get_worldcup_fixtures()
    assert len(result) == 1
    assert "home_team" in result[0] or "teams" in result[0]
