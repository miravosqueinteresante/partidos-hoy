import json
import hashlib
import os
import re
import unicodedata
from datetime import datetime, timezone
from typing import Dict, Optional

import pandas as pd


class EloPredictor:
    def __init__(self, ratings_path: Optional[str] = None):
        self.home_advantage = 100
        self.ratings: Dict[str, float] = {}
        if ratings_path and os.path.exists(ratings_path):
            with open(ratings_path, encoding="utf-8") as f:
                raw = json.load(f)
            for team, info in raw.items():
                self.ratings[team] = info.get("elo", 1500)
        self._load_fallback()

    def _normalize(self, name: str) -> str:
        if not name:
            return ""
        nfkd = unicodedata.normalize("NFKD", name)
        ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
        return ascii_text

    def _load_fallback(self):
        if not self.ratings:
            self.ratings = {
                "Spain": 2165, "Argentina": 2113, "France": 2081, "England": 2020,
                "Brazil": 1988, "Portugal": 1984, "Colombia": 1975, "Netherlands": 1961,
                "Ecuador": 1935, "Croatia": 1930, "Germany": 1925, "Norway": 1912,
                "Japan": 1906, "Turkiye": 1902, "Switzerland": 1894, "Uruguay": 1892,
                "Mexico": 1868, "Belgium": 1867, "Senegal": 1866, "Paraguay": 1833,
                "Austria": 1827, "Morocco": 1822, "Canada": 1784, "Australia": 1775,
                "Scotland": 1770, "IR Iran": 1764, "Korea Republic": 1756, "Algeria": 1743,
                "Czechia": 1733, "USA": 1733, "Panama": 1733, "Uzbekistan": 1727,
                "Sweden": 1719, "Egypt": 1699, "Jordan": 1685, "Cote d'Ivoire": 1676,
                "Tunisia": 1636, "Iraq": 1608, "Bosnia and Herzegovina": 1591,
                "New Zealand": 1585, "Cabo Verde": 1576, "Saudi Arabia": 1566,
                "Haiti": 1532, "South Africa": 1517, "Ghana": 1503, "Qatar": 1423,
                "Curacao": 1433, "Congo DR": 1207,
            }

    def get_rating(self, team: str) -> float:
        if not team:
            return 0.0
        rating = self.ratings.get(team)
        if rating is not None:
            return rating
        normalized = self._normalize(team)
        for key, val in self.ratings.items():
            if self._normalize(key) == normalized:
                return val
        return 1500.0

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        diff = rating_a - rating_b + self.home_advantage
        return 1.0 / (1.0 + 10.0 ** (-diff / 400.0))

    def predict_proba(self, home_team: str, away_team: str) -> Dict[str, float]:
        r_home = self.get_rating(home_team)
        r_away = self.get_rating(away_team)
        exp_home = self.expected_score(r_home, r_away)
        rating_gap = abs(r_home - r_away)
        draw_prob = max(0.05, 0.30 - (rating_gap / 4000.0))
        if exp_home > 0.5:
            home_prob = exp_home * (1.0 - draw_prob)
            away_prob = 1.0 - home_prob - draw_prob
        else:
            away_prob = (1.0 - exp_home) * (1.0 - draw_prob)
            home_prob = 1.0 - away_prob - draw_prob
        if home_prob < 0.05:
            home_prob = 0.05
        if away_prob < 0.05:
            away_prob = 0.05
        total = home_prob + draw_prob + away_prob
        return {
            "home": round(home_prob / total, 4),
            "draw": round(draw_prob / total, 4),
            "away": round(away_prob / total, 4),
        }

    def generate(self, upcoming_matches: pd.DataFrame) -> str:
        matches_list = []
        for _, match in upcoming_matches.iterrows():
            home = match["home_team"]
            away = match["away_team"]
            if pd.isna(home) or pd.isna(away) or not home or not away:
                matches_list.append({
                    "id": hashlib.md5(f"tbd-{match.get('date', '')}".encode()).hexdigest()[:8],
                    "home": None,
                    "away": None,
                    "league": match.get("league", ""),
                    "date": str(match.get("date", "")),
                    "stage": match.get("stage", ""),
                    "status": "TBD",
                })
                continue
            match_id = hashlib.md5(
                f"{home}-{away}-{match.get('date', '')}".encode()
            ).hexdigest()[:8]
            probs = self.predict_proba(home, away)
            home_xg = probs["home"] * 2.5 + probs["draw"] * 1.0
            away_xg = probs["away"] * 2.5 + probs["draw"] * 1.0
            matches_list.append({
                "id": match_id,
                "home": home,
                "away": away,
                "league": match.get("league", ""),
                "date": str(match.get("date", "")),
                "stage": match.get("stage", ""),
                "probabilities": probs,
                "expected_goals": {
                    "home": round(home_xg, 2),
                    "away": round(away_xg, 2),
                },
                "model": "elo",
            })
        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model_version": "1.0.0-elo",
            "model": "World Football Elo Ratings (eloratings.net)",
            "notes": "Predicciones basadas en Elo ratings de selecciones nacionales.",
            "matches": matches_list,
        }
        return json.dumps(output, indent=2, ensure_ascii=False)
