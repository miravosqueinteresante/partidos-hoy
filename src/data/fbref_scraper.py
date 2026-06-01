from typing import Dict, List, Optional

from src.config import config


class FBrefScraper:
    def __init__(self):
        self._fbref = None
        self._club_elo = None

    @property
    def fbref(self):
        if self._fbref is None:
            from soccerdata import FBref as FBrefLib
            self._fbref = FBrefLib(league="WC", season=2026)
        return self._fbref

    @property
    def club_elo(self):
        if self._club_elo is None:
            from soccerdata import ClubElo
            self._club_elo = ClubElo()
        return self._club_elo

    def fetch_worldcup_fixtures(self) -> List[Dict]:
        try:
            df = self.fbref.read_schedule()
            if df is None or df.empty:
                return []
            records = df.to_dict("records")
            for r in records:
                r["source"] = "fbref"
            return records
        except Exception:
            return []

    def fetch_worldcup_standings(self) -> List[Dict]:
        try:
            df = self.fbref.read_standings()
            if df is None or df.empty:
                return []
            return df.to_dict("records")
        except Exception:
            return []

    def fetch_elo_ratings(self) -> Dict[str, float]:
        try:
            data = self.club_elo.data
            if data is None:
                return {}
            return {
                team: float(rating)
                for team, rating in data.items()
            }
        except Exception:
            return {}

    def is_worldcup_available(self) -> bool:
        try:
            df = self.fbref.read_schedule()
            return df is not None and not df.empty
        except Exception:
            return False
