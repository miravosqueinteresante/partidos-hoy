import json
import os
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import requests

from src.config import config
from src.utils.rate_limiter import RateLimiter


class APIFootballClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.api_football_key
        self.base_url = config.api_football_base
        self._daily_count = 0
        self._daily_reset = date.today()
        self.session = requests.Session()
        self.session.headers.update({
            "x-apisports-key": self.api_key
        })
        self.rate_limiter = RateLimiter(max_per_minute=config.api_football_rate_limit)

    def _request(self, endpoint: str, params: Dict[str, Any]) -> List[Dict]:
        self._check_daily_limit()
        self.rate_limiter.wait_if_needed()
        resp = self.session.get(f"{self.base_url}/{endpoint}", params=params)
        self._daily_count += 1
        if resp.status_code != 200:
            raise RuntimeError(f"API error {resp.status_code}: {resp.text}")
        data = resp.json()
        if data.get("errors") and any(data["errors"].values()):
            raise RuntimeError(f"API error: {data['errors']}")
        return data.get("response", [])

    def _check_daily_limit(self):
        today = date.today()
        if today != self._daily_reset:
            self._daily_count = 0
            self._daily_reset = today
        if self._daily_count >= config.api_football_daily_limit:
            raise RuntimeError("Daily limit reached - free tier allows 100 req/day")

    # ─── Fixtures ───────────────────────────────────────────────

    def fetch_fixtures(self, league_id: int, season: int,
                       date_from: Optional[str] = None,
                       date_to: Optional[str] = None) -> List[Dict]:
        params = {"league": league_id, "season": season}
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to
        return self._request("fixtures", params)

    def fetch_fixtures_by_round(self, league_id: int, season: int,
                                 round_name: str) -> List[Dict]:
        return self._request("fixtures", {
            "league": league_id, "season": season, "round": round_name
        })

    def fetch_fixture_detail(self, fixture_id: int) -> Dict:
        result = self._request("fixtures", {"id": fixture_id})
        return result[0] if result else {}

    def fetch_multiple_fixtures(self, fixture_ids: List[int]) -> List[Dict]:
        ids_str = "-".join(str(i) for i in fixture_ids[:20])
        return self._request("fixtures", {"ids": ids_str})

    def fetch_rounds(self, league_id: int, season: int) -> List[str]:
        result = self._request("fixtures/rounds", {
            "league": league_id, "season": season
        })
        return [r["name"] for r in result] if result else []

    # ─── Live ───────────────────────────────────────────────────

    def fetch_live_matches(self, league_id: Optional[int] = None) -> List[Dict]:
        params = {"live": "all"}
        if league_id:
            params["league"] = league_id
        return self._request("fixtures", params)

    # ─── Standings ──────────────────────────────────────────────

    def fetch_standings(self, league_id: int, season: int) -> List[Dict]:
        return self._request("standings", {"league": league_id, "season": season})

    # ─── Teams ──────────────────────────────────────────────────

    def fetch_teams_by_league(self, league_id: int, season: int) -> List[Dict]:
        return self._request("teams", {"league": league_id, "season": season})

    # ─── Team Stats ─────────────────────────────────────────────

    def fetch_team_stats(self, team_id: int, league_id: int, season: int) -> Dict:
        result = self._request("teams/statistics", {
            "team": team_id, "league": league_id, "season": season
        })
        return result[0] if result else {}

    # ─── H2H ────────────────────────────────────────────────────

    def fetch_h2h(self, home_id: int, away_id: int, last: int = 10) -> List[Dict]:
        return self._request("fixtures/headtohead", {
            "h2h": f"{home_id}-{away_id}", "last": last
        })

    # ─── Predictions (API-Football) ─────────────────────────────

    def fetch_prediction(self, fixture_id: int) -> Dict:
        result = self._request("predictions", {"fixture": fixture_id})
        return result[0] if result else {}

    # ─── Odds ───────────────────────────────────────────────────

    def fetch_odds(self, fixture_id: int) -> List[Dict]:
        return self._request("odds", {"fixture": fixture_id})

    def fetch_live_odds(self, fixture_id: int) -> List[Dict]:
        return self._request("odds/live", {"fixture": fixture_id})

    # ─── Coverage check ────────────────────────────────────────

    def check_coverage(self, league_id: int, season: int) -> Dict:
        result = self._request("leagues", {"id": league_id, "season": season})
        if not result:
            return {}
        season_data = result[0].get("seasons", [])
        if season_data:
            return season_data[0].get("coverage", {})
        return {}

    # ─── Convenience: World Cup 2026 ───────────────────────────

    def fetch_worldcup_fixtures(self, date_from: Optional[str] = None,
                                 date_to: Optional[str] = None) -> List[Dict]:
        return self.fetch_fixtures(
            league_id=config.worldcup_league_id,
            season=config.worldcup_season,
            date_from=date_from, date_to=date_to
        )

    def fetch_worldcup_standings(self) -> List[Dict]:
        return self.fetch_standings(
            league_id=config.worldcup_league_id,
            season=config.worldcup_season
        )

    def fetch_worldcup_teams(self) -> List[Dict]:
        return self.fetch_teams_by_league(
            league_id=config.worldcup_league_id,
            season=config.worldcup_season
        )

    # ─── Quota management ───────────────────────────────────────

    def remaining_requests(self) -> int:
        return config.api_football_daily_limit - self._daily_count

    def quota_usage(self) -> dict:
        return {
            "used": self._daily_count,
            "limit": config.api_football_daily_limit,
            "remaining": self.remaining_requests(),
            "reset": str(self._daily_reset),
        }
