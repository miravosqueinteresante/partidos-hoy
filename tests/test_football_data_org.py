import pytest
from src.data.football_data_org import FootballDataOrgClient


def test_fetch_returns_empty_on_error(mocker):
    mocker.patch("requests.Session.get",
                 side_effect=Exception("API error"))
    client = FootballDataOrgClient(api_key="test")
    result = client.fetch_matches(date_from="2026-06-11", date_to="2026-06-12")
    assert result == []


def test_fetch_parses_response(mocker):
    mock_response = {
        "matches": [
            {
                "homeTeam": {"name": "Argentina"},
                "awayTeam": {"name": "Chile"},
                "utcDate": "2026-06-11T21:00:00Z",
                "competition": {"name": "FIFA World Cup"},
            }
        ]
    }
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=200,
                                          json=lambda: mock_response))
    client = FootballDataOrgClient(api_key="test")
    result = client.fetch_matches(date_from="2026-06-11", date_to="2026-06-12")
    assert len(result) == 1
    assert result[0]["home_team"] == "Argentina"


def test_rate_limit_handled(mocker):
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=429,
                                          json=lambda: {"error": "rate limit"}))
    client = FootballDataOrgClient(api_key="test")
    result = client.fetch_matches()
    assert result == []
