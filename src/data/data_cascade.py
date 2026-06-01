import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.data.api_football_client import APIFootballClient
from src.data.fbref_scraper import FBrefScraper
from src.data.football_data_org import FootballDataOrgClient

logger = logging.getLogger(__name__)


class DataCascade:
    def __init__(self):
        self.api_football = APIFootballClient()
        self.fbref = FBrefScraper()
        self.football_data = FootballDataOrgClient()

    def get_worldcup_fixtures(self) -> List[Dict]:
        try:
            result = self.api_football.fetch_worldcup_fixtures()
            if result:
                return result
        except Exception as e:
            logger.warning("API-Football failed: %s", e)

        try:
            result = self.fbref.fetch_worldcup_fixtures()
            if result:
                return result
        except Exception as e:
            logger.warning("FBref failed: %s", e)

        try:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            result = self.football_data.fetch_matches(
                date_from=today, date_to=today
            )
            if result:
                return result
        except Exception as e:
            logger.warning("football-data.org failed: %s", e)

        logger.error("ALL data sources failed for World Cup fixtures")
        return []

    def get_worldcup_standings(self) -> List[Dict]:
        try:
            result = self.api_football.fetch_worldcup_standings()
            if result:
                return result
        except Exception:
            pass

        try:
            result = self.fbref.fetch_worldcup_standings()
            if result:
                return result
        except Exception:
            pass

        return []

    def get_elo_ratings(self) -> Dict[str, float]:
        try:
            result = self.fbref.fetch_elo_ratings()
            if result:
                return result
        except Exception:
            pass
        return {}

    def quota_status(self) -> dict:
        return {
            "api_football": self.api_football.quota_usage(),
            "fbref": {"type": "scraping", "limit": "unlimited"},
            "football_data_org": {"type": "api", "limit": "10 req/min"},
        }
