import pytest
from src.data.fbref_scraper import FBrefScraper


def test_fetch_worldcup_fixtures_returns_list(mocker):
    mock_df = mocker.Mock()
    mock_df.empty = False
    mock_df.to_dict.return_value = [
        {
            "date": "2026-06-11",
            "home_team": "Mexico",
            "away_team": "Canada",
            "home_score": None,
            "away_score": None,
        },
        {
            "date": "2026-06-11",
            "home_team": "United States",
            "away_team": "Japan",
            "home_score": None,
            "away_score": None,
        },
    ]
    scraper = FBrefScraper()
    mock_fbref = mocker.Mock()
    mock_fbref.read_schedule.return_value = mock_df
    scraper._fbref = mock_fbref

    result = scraper.fetch_worldcup_fixtures()
    assert len(result) == 2
    assert result[0]["home_team"] == "Mexico"
    assert result[0]["away_team"] == "Canada"


def test_fetch_worldcup_standings(mocker):
    mock_df = mocker.Mock()
    mock_df.empty = False
    mock_df.to_dict.return_value = [
        {
            "team": "Argentina",
            "pts": 9,
            "gf": 8,
            "ga": 1,
            "rank": 1,
        },
        {
            "team": "Peru",
            "pts": 4,
            "gf": 2,
            "ga": 3,
            "rank": 2,
        },
    ]
    scraper = FBrefScraper()
    mock_fbref = mocker.Mock()
    mock_fbref.read_standings.return_value = mock_df
    scraper._fbref = mock_fbref

    result = scraper.fetch_worldcup_standings()
    assert len(result) == 2
    assert result[0]["team"] == "Argentina"
    assert result[0]["pts"] == 9


def test_fetch_elo_ratings(mocker):
    scraper = FBrefScraper()
    mock_elo = mocker.Mock()
    mock_elo.data = {"Argentina": 2050, "Brazil": 2020, "Peru": 1850}
    scraper._club_elo = mock_elo

    result = scraper.fetch_elo_ratings()
    assert result["Argentina"] == 2050
    assert result["Brazil"] == 2020


def test_fetch_returns_empty_on_error(mocker):
    scraper = FBrefScraper()
    mock_fbref = mocker.Mock()
    mock_fbref.read_schedule.side_effect = Exception("Scraping failed")
    scraper._fbref = mock_fbref

    result = scraper.fetch_worldcup_fixtures()
    assert result == []


def test_worldcup_available_returns_bool(mocker):
    scraper = FBrefScraper()
    mock_fbref = mocker.Mock()
    mock_fbref.read_schedule.return_value.empty = False
    scraper._fbref = mock_fbref

    assert scraper.is_worldcup_available() is True
