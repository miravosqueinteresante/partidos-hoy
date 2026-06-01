import pytest
from src.data.api_football_client import APIFootballClient
from src.config import config


def test_fetch_fixtures_returns_list(mocker):
    mock_response = {
        "response": [
            {"fixture": {"id": 1, "date": "2026-06-01"},
             "league": {"id": 9, "name": "Premier League"},
             "teams": {"home": {"name": "Arsenal"}, "away": {"name": "Chelsea"}}}
        ]
    }
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=200,
                                          json=lambda: mock_response))
    client = APIFootballClient(api_key="test_key")
    result = client.fetch_fixtures(league_id=9, season=2025)
    assert len(result) == 1
    assert result[0]["teams"]["home"]["name"] == "Arsenal"


def test_fetch_standings_returns_teams(mocker):
    mock_response = {
        "response": [{
            "league": {
                "standings": [[
                    {"rank": 1, "team": {"name": "Arsenal", "id": 42},
                     "points": 85, "goalsDiff": 45}
                ]]
            }
        }]
    }
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=200,
                                          json=lambda: mock_response))
    client = APIFootballClient(api_key="test_key")
    result = client.fetch_standings(league_id=9, season=2025)
    assert len(result) == 1
    assert result[0]["league"]["standings"][0][0]["team"]["name"] == "Arsenal"


def test_fetch_worldcup_fixtures(mocker):
    mock_response = {
        "response": [
            {"fixture": {"id": 100, "date": "2026-06-11T21:00:00+00:00"},
             "league": {"id": 1, "name": "FIFA World Cup", "season": 2026},
             "teams": {"home": {"name": "Mexico"}, "away": {"name": "Canada"}}}
        ]
    }
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=200,
                                          json=lambda: mock_response))
    client = APIFootballClient(api_key="test_key")
    result = client.fetch_worldcup_fixtures()
    assert len(result) == 1
    assert result[0]["league"]["id"] == 1
    assert result[0]["teams"]["home"]["name"] == "Mexico"


def test_fetch_multiple_fixtures(mocker):
    mock_response = {"response": [{"fixture": {"id": 1}}, {"fixture": {"id": 2}}]}
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=200,
                                          json=lambda: mock_response))
    client = APIFootballClient(api_key="test_key")
    result = client.fetch_multiple_fixtures([1, 2])
    assert len(result) == 2


def test_fetch_prediction(mocker):
    mock_response = {
        "response": [{
            "predictions": {
                "winner": {"name": "Argentina"},
                "percent": {"home": 45, "draw": 30, "away": 25}
            }
        }]
    }
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=200,
                                          json=lambda: mock_response))
    client = APIFootballClient(api_key="test_key")
    result = client.fetch_prediction(fixture_id=100)
    assert result["predictions"]["winner"]["name"] == "Argentina"


def test_check_coverage(mocker):
    mock_response = {
        "response": [{
            "seasons": [{
                "coverage": {
                    "fixtures": {"events": True, "lineups": True},
                    "standings": True,
                    "predictions": True,
                    "odds": True,
                }
            }]
        }]
    }
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=200,
                                          json=lambda: mock_response))
    client = APIFootballClient(api_key="test_key")
    cov = client.check_coverage(league_id=1, season=2026)
    assert cov["predictions"] is True
    assert cov["odds"] is True


def test_daily_limit_enforced(mocker):
    mock_get = mocker.patch("requests.Session.get",
                            return_value=mocker.Mock(status_code=200,
                                                     json=lambda: {"response": []}))
    client = APIFootballClient(api_key="test_key")
    client._daily_count = 99  # Force near-limit state
    client.fetch_fixtures(league_id=9, season=2025)  # 100th request
    with pytest.raises(RuntimeError, match="Daily limit reached"):
        client.fetch_fixtures(league_id=10, season=2025)
