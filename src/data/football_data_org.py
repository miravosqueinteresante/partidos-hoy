from datetime import date, datetime
from typing import Any, Dict, List, Optional

import requests

from src.config import config


class FootballDataOrgClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.football_data_org_key
        self.base_url = config.football_data_org_base
        self.session = requests.Session()
        self.session.headers.update({
            "X-Auth-Token": self.api_key
        })

    def fetch_matches(self, date_from: Optional[str] = None,
                      date_to: Optional[str] = None,
                      competition_id: Optional[int] = None) -> List[Dict]:
        try:
            params = {}
            if date_from:
                params["dateFrom"] = date_from
            if date_to:
                params["dateTo"] = date_to
            if competition_id:
                params["competitions"] = str(competition_id)

            resp = self.session.get(
                f"{self.base_url}/matches", params=params, timeout=15
            )
            if resp.status_code != 200:
                return []

            data = resp.json()
            matches = data.get("matches", [])
            return [
                {
                    "home_team": m["homeTeam"]["name"],
                    "away_team": m["awayTeam"]["name"],
                    "date": m["utcDate"],
                    "competition": m["competition"]["name"],
                    "source": "football-data.org",
                }
                for m in matches
            ]
        except Exception:
            return []

    def fetch_standings(self, competition_id: int) -> List[Dict]:
        try:
            resp = self.session.get(
                f"{self.base_url}/competitions/{competition_id}/standings",
                timeout=15
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            return data.get("standings", [])
        except Exception:
            return []
