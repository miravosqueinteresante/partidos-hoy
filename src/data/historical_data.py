from typing import Optional
import pandas as pd
import requests


class HistoricalDataParser:
    BASE_URL = "https://www.football-data.co.uk"

    LEAGUE_MAP = {
        "E0": "Premier League", "E1": "Championship",
        "SP1": "La Liga", "I1": "Serie A",
        "D1": "Bundesliga", "F1": "Ligue 1",
        "N1": "Eredivisie", "P1": "Primeira Liga",
        "B1": "Belgian Pro League", "T1": "Super Lig",
    }

    COLUMN_MAP = {
        "Div": "league", "Date": "date",
        "HomeTeam": "home_team", "AwayTeam": "away_team",
        "FTHG": "home_goals", "FTAG": "away_goals",
        "FTR": "result",
        "HST": "home_shots_target", "AST": "away_shots_target",
        "HC": "home_corners", "AC": "away_corners",
        "B365H": "odds_home", "B365D": "odds_draw", "B365A": "odds_away",
        "PSH": "odds_home_pinnacle", "PSD": "odds_draw_pinnacle", "PSA": "odds_away_pinnacle",
    }

    def load_csv(self, filepath: str) -> pd.DataFrame:
        df = pd.read_csv(filepath)
        df = df.rename(columns=self.COLUMN_MAP)
        keep_cols = [c for c in self.COLUMN_MAP.values() if c in df.columns]
        df = df[keep_cols]
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        return df.dropna(subset=["home_team", "away_team", "home_goals", "away_goals"])

    def download_league(self, league_code: str) -> Optional[pd.DataFrame]:
        url = f"{self.BASE_URL}/mmz4281/{league_code}.csv"
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            with open("temp.csv", "wb") as f:
                f.write(resp.content)
            return self.load_csv("temp.csv")
        except Exception:
            return None

    def filter_league(self, df: pd.DataFrame, league_code: str) -> pd.DataFrame:
        return df[df["league"] == league_code].copy()

    def get_available_leagues(self) -> list:
        return list(self.LEAGUE_MAP.keys())
